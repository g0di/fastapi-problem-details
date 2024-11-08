# To catch user not found exception
import logging
from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from .models import Problem, ProblemException, ProblemResponse


def init_app(
    app: FastAPI,
    *,
    validation_error_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
    validation_error_detail: str = "Request validation failed",
    include_exc_info_in_response: bool = False,
) -> FastAPI:
    app.router.responses.setdefault(
        "default",
        {
            "description": "Problem",
            "content": {
                "application/problem+json": {"schema": Problem.model_json_schema()}
            },
        },
    )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> ProblemResponse:
        return ProblemResponse(
            status=validation_error_code,
            detail=validation_error_detail,
            errors=jsonable_encoder(exc.errors()),
        )

    @app.exception_handler(ProblemException)
    async def handle_problem_exception(
        _: Request, exc: ProblemException
    ) -> ProblemResponse:
        return ProblemResponse(
            status=exc.status,
            title=exc.title,
            detail=exc.detail,
            type=exc.type,
            instance=exc.instance,
            headers=exc.headers,
            **exc.extra,
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException) -> ProblemResponse:
        http_status = HTTPStatus(exc.status_code)
        # NOTE: HTTPException detail default to HTTStatus.phrase when not provided
        # However, Problem use this phrase as title, to avoid duplicate between problem
        # title and detail we set detail to None if actual http
        # exception detail is the default value.
        detail = exc.detail if exc.detail != http_status.phrase else None
        return ProblemResponse(
            status=exc.status_code,
            detail=detail,
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> ProblemResponse:
        logger = logging.getLogger(__name__)
        logger.exception("Unexpected error")
        return ProblemResponse.from_exception(
            exc, include_exc_info=include_exc_info_in_response
        )

    return app
