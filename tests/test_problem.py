from http import HTTPStatus

import pytest
from faker import Faker

from fastapi_problem_details import Problem


@pytest.mark.parametrize("http_status", HTTPStatus)
def test_create_problem_from_status_fill_problem_fields_using_status_description_and_phrase(
    http_status: HTTPStatus,
) -> None:
    # When
    problem = Problem.from_status(http_status.value)
    # Then
    assert problem == Problem(
        type="about:blank",
        status=http_status.value,
        title=http_status.phrase,
        detail=http_status.description,
    )


def test_create_problem_from_status_with_type_overrides_default_type(
    faker: Faker,
) -> None:
    # Given
    status = HTTPStatus(faker.http_status_code(include_unassigned=False))
    type = faker.uri()  # noqa: A001
    # When
    problem = Problem.from_status(status, type=type)
    # Then
    assert problem == Problem(
        type=type,
        status=status.value,
        title=status.phrase,
        detail=status.description,
    )


def test_create_problem_from_status_with_title_overrides_default_title(
    faker: Faker,
) -> None:
    # Given
    status = HTTPStatus(faker.http_status_code(include_unassigned=False))
    title = faker.sentence()
    # When
    problem = Problem.from_status(status, title=title)
    # Then
    assert problem == Problem(
        status=status.value,
        title=title,
        detail=status.description,
    )


def test_create_problem_from_status_with_detail_overrides_default_detail(
    faker: Faker,
) -> None:
    # Given
    status = HTTPStatus(faker.http_status_code(include_unassigned=False))
    detail = faker.sentence()
    # When
    problem = Problem.from_status(status, detail=detail)
    # Then
    assert problem == Problem(
        status=status.value,
        title=status.phrase,
        detail=detail,
    )


def test_create_problem_from_status_with_instance_overrides_default_instance(
    faker: Faker,
) -> None:
    # Given
    status = HTTPStatus(faker.http_status_code(include_unassigned=False))
    instance = faker.uri()
    # When
    problem = Problem.from_status(status, instance=instance)
    # Then
    assert problem == Problem(
        status=status.value,
        title=status.phrase,
        detail=status.description,
        instance=instance,
    )


def test_create_problem_from_status_with_extra_includes_extra(
    faker: Faker,
) -> None:
    # Given
    status = HTTPStatus(faker.http_status_code(include_unassigned=False))
    extra = faker.pydict()
    # When
    problem = Problem.from_status(status, **extra)
    # Then
    assert problem == Problem(
        status=status.value, title=status.phrase, detail=status.description, **extra
    )
