# To catch user not found exception
import logging
import traceback
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request, status
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
    app.router.responses.setdefault("default", {"model": Problem})

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> ProblemResponse:
        return ProblemResponse(
            status=validation_error_code,
            detail=validation_error_detail,
            errors=exc.errors(),
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
        # NOTE: HTTPException detail default to HTTStatus.phrase when not provided
        # However, Problem use this phrase as title, to avoid duplicate between problem
        # title and detail we set detail to None if actual http exception detail is the
        # default value.
        detail = (
            exc.detail if exc.detail != HTTPStatus(exc.status_code).phrase else None
        )
        return ProblemResponse(
            status=exc.status_code,
            detail=detail,
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> ProblemResponse:
        logger = logging.getLogger(__name__)
        logger.exception("Unhandled exception")

        extra: dict[str, Any] = {}
        if include_exc_info_in_response:
            extra["exc_stack"] = traceback.format_exception(exc)
            extra["exc_type"] = f"{type(exc).__module__}.{type(exc).__qualname__}"

        return ProblemResponse(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc), **extra
        )

    return app
