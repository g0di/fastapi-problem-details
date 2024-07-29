from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import Url
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse

_500_INTERNAL_SERVER_ERROR = HTTPStatus(500)


class Problem(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str | Url = Field(
        "about:blank", description="An URI reference that identifies the problem type"
    )
    status: int = Field(
        _500_INTERNAL_SERVER_ERROR.value,
        description="HTTP status code for this occurrence of the problem",
    )
    title: str = Field(
        _500_INTERNAL_SERVER_ERROR.phrase,
        description="Short, human-readable summary of the problem type",
    )
    detail: str | None = Field(
        _500_INTERNAL_SERVER_ERROR.description,
        description="Human-readable explanation specific to this occurrence of the problem",
    )
    instance: str | None = None

    @classmethod
    def from_status_code():


class ProblemResponse(JSONResponse):
    media_type = "application/problem+json"

    def __init__(  # noqa: PLR0913
        self,
        status_code: int = 500,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        title: str | None = None,
        detail: str | None = None,
        type: str | None = None,  # noqa: A002
        **extra: Any,  # noqa: ANN401
    ) -> None:
        status_obj = HTTPStatus(status_code)
        problem = Problem(
            status=status_code,
            type=type or "about:blank",
            title=title or status_obj.phrase,
            detail=detail or status_obj.description or None,
            **extra,
        )
        super().__init__(
            problem.model_dump(mode="json"),
            status_code,
            headers,
            media_type,
            background,
        )
