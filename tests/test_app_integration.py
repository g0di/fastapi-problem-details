from http import HTTPStatus
from typing import Any, cast
from unittest.mock import ANY

import pytest
from faker import Faker
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from httpx import Response

import fastapi_problem_details as problem
from fastapi_problem_details import Problem, ProblemException, ProblemResponse


def assert_problem_response(  # noqa: PLR0913
    resp: Response,
    *,
    status: int,
    type: str = "about:blank",  # noqa: A002
    title: str | None = None,
    detail: str | None = None,
    instance: str | None = None,
    headers: dict[str, str] | None = None,
    **extra: Any,  # noqa: ANN401
) -> dict[str, Any]:
    assert resp.status_code == status
    assert resp.headers.get("Content-Type") == "application/problem+json"

    if headers:
        for h, v in headers.items():
            assert h in resp.headers
            assert resp.headers[h] == v

    problem_data = resp.json()
    assert problem_data == omit_none(
        {
            "type": type,
            "status": status,
            "title": title or HTTPStatus(status).phrase,
            "detail": detail or HTTPStatus(status).description,
            "instance": instance,
            **extra,
        }
    )

    return cast(dict[str, Any], problem_data)


def omit_none(value: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in value.items() if v is not None}


def test_init_app_register_problem_details_as_default_response() -> None:
    # Given
    app = FastAPI()
    # When
    problem.init_app(app)
    # Then
    assert ("default", {"model": Problem}) in app.router.responses.items()


class TestValidationError:
    @pytest.fixture
    def app(self) -> FastAPI:
        app = FastAPI()

        @app.post("/")
        def _(_body: dict[str, str]) -> None:
            pass

        return app

    def test_app_validation_error_returns_a_problem_details(self, app: FastAPI) -> None:
        # Given
        problem.init_app(app)

        # When
        with TestClient(app) as test_client:
            resp = test_client.post("/", json=[])

        # Then
        problem_data = assert_problem_response(
            resp,
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Request validation failed",
            errors=ANY,
        )
        assert isinstance(problem_data["errors"], list)
        assert problem_data["errors"], "errors list should not be empty"

    def test_app_validation_error_with_custom_status_returns_a_problem_details_with_status(
        self, app: FastAPI
    ) -> None:
        # Given
        problem.init_app(app, validation_error_code=status.HTTP_400_BAD_REQUEST)

        # When
        with TestClient(app) as test_client:
            resp = test_client.post("/", json=[])

        # Then
        problem_data = assert_problem_response(
            resp,
            status=status.HTTP_400_BAD_REQUEST,
            detail="Request validation failed",
            errors=ANY,
        )
        assert isinstance(problem_data["errors"], list)
        assert problem_data["errors"], "errors list should not be empty"

    def test_app_validation_error_with_custom_detail_returns_a_problem_details_with_given_detail(
        self, app: FastAPI, faker: Faker
    ) -> None:
        # Given
        detail = faker.sentence()
        problem.init_app(app, validation_error_detail=detail)

        # When
        with TestClient(app) as test_client:
            resp = test_client.post("/", json=[])

        # Then
        problem_data = assert_problem_response(
            resp,
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            errors=ANY,
        )
        assert isinstance(problem_data["errors"], list)
        assert problem_data["errors"], "errors list should not be empty"


class TestUnhandledError:
    class FakeError(Exception):
        pass

    def test_app_unhandled_error_returns_a_problem_details(self, faker: Faker) -> None:
        # Given
        app = FastAPI()
        error_message = faker.sentence()

        @app.post("/")
        def _() -> Any:  # noqa: ANN401
            raise TestUnhandledError.FakeError(error_message)

        problem.init_app(app)

        # When
        with TestClient(app, raise_server_exceptions=False) as test_client:
            resp = test_client.post("/")

        # Then
        assert_problem_response(
            resp, status=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message
        )

    def test_app_unhandled_error_with_exc_info_enabled_returns_a_problem_details_with_error_type_and_stack(
        self,
        faker: Faker,
    ) -> None:
        # Given
        app = FastAPI()
        error_message = faker.sentence()

        @app.post("/")
        def _() -> Any:  # noqa: ANN401
            raise TestUnhandledError.FakeError(error_message)

        problem.init_app(app, include_exc_info_in_response=True)

        # When
        with TestClient(app, raise_server_exceptions=False) as test_client:
            resp = test_client.post("/")

        # Then
        problem_data = assert_problem_response(
            resp,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
            exc_type="tests.test_app_integration.TestUnhandledError.FakeError",
            exc_stack=ANY,
        )
        assert problem_data["exc_stack"], "exc_stack should not be empty"
        assert isinstance(problem_data["exc_stack"], list)


class TestHttpException:
    def test_app_http_exception_returns_a_problem_details(self, faker: Faker) -> None:
        # Given
        app = FastAPI()
        status = faker.http_status_code(include_unassigned=False)
        error_message = faker.sentence()
        headers = {faker.word(): faker.pystr() for _ in range(10)}

        @app.post("/")
        def _() -> Any:  # noqa: ANN401
            raise HTTPException(
                status_code=status,
                detail=error_message,
                headers=headers,
            )

        problem.init_app(app)

        # When
        with TestClient(app, raise_server_exceptions=False) as test_client:
            resp = test_client.post("/")

        # Then
        assert_problem_response(
            resp, status=status, detail=error_message, headers=headers
        )

    def test_app_http_exception_without_details_returns_a_problem_details_with_default_details(
        self, faker: Faker
    ) -> None:
        # Given
        app = FastAPI()
        status = faker.http_status_code(include_unassigned=False)

        @app.post("/")
        def _() -> Any:  # noqa: ANN401
            raise HTTPException(status_code=status)

        problem.init_app(app)

        # When
        with TestClient(app, raise_server_exceptions=False) as test_client:
            resp = test_client.post("/")

        # Then
        assert_problem_response(resp, status=status)


class TestProblemResponse:
    def test_app_problem_response_returns_a_problem_details(self, faker: Faker) -> None:
        app = FastAPI()
        status = faker.http_status_code(include_unassigned=False)

        @app.post("/")
        def _() -> ProblemResponse:
            return ProblemResponse(status=status)

        problem.init_app(app)

        # When
        with TestClient(app, raise_server_exceptions=False) as test_client:
            resp = test_client.post("/")

        # Then
        assert_problem_response(resp, status=status)

    def test_app_problem_response_with_custom_values_returns_a_problem_details_with_those_values(
        self, faker: Faker
    ) -> None:
        app = FastAPI()
        status = faker.http_status_code(include_unassigned=False)
        headers = {faker.word(): faker.pystr() for _ in range(10)}
        title = faker.sentence()
        detail = faker.sentence()
        instance = faker.uri()
        type = faker.uri()  # noqa: A001
        extra = faker.pydict(allowed_types=[str, int, float, bool])

        @app.post("/")
        def _() -> ProblemResponse:
            return ProblemResponse(
                status=status,
                headers=headers,
                title=title,
                detail=detail,
                instance=instance,
                type=type,
                **extra,
            )

        problem.init_app(app)

        # When
        with TestClient(app, raise_server_exceptions=False) as test_client:
            resp = test_client.post("/")

        # Then
        assert_problem_response(
            resp,
            status=status,
            title=title,
            detail=detail,
            headers=headers,
            type=type,
            instance=instance,
            **extra,
        )


class TestProblemException:
    def test_app_problem_exception_returns_a_problem_details(
        self, faker: Faker
    ) -> None:
        app = FastAPI()
        status = faker.http_status_code(include_unassigned=False)

        @app.post("/")
        def _() -> Any:  # noqa: ANN401
            raise ProblemException(status)

        problem.init_app(app)

        # When
        with TestClient(app, raise_server_exceptions=False) as test_client:
            resp = test_client.post("/")

        # Then
        assert_problem_response(resp, status=status)

    def test_app_problem_response_with_custom_values_returns_a_problem_details_with_those_values(
        self, faker: Faker
    ) -> None:
        app = FastAPI()
        status = faker.http_status_code(include_unassigned=False)
        headers = {faker.word(): faker.pystr() for _ in range(10)}
        title = faker.sentence()
        detail = faker.sentence()
        instance = faker.uri()
        type = faker.uri()  # noqa: A001
        extra = faker.pydict(allowed_types=[str, int, float, bool])

        @app.post("/")
        def _() -> ProblemResponse:
            raise ProblemException(
                status=status,
                headers=headers,
                title=title,
                detail=detail,
                instance=instance,
                type=type,
                **extra,
            )

        problem.init_app(app)

        # When
        with TestClient(app, raise_server_exceptions=False) as test_client:
            resp = test_client.post("/")

        # Then
        assert_problem_response(
            resp,
            status=status,
            title=title,
            detail=detail,
            headers=headers,
            type=type,
            instance=instance,
            **extra,
        )
