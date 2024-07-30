from http import HTTPStatus
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse


class Problem(BaseModel):
    DEFAULT_TYPE: ClassVar[str] = "about:blank"
    model_config = ConfigDict(extra="allow")

    type: str = Field(
        default=DEFAULT_TYPE,
        description=(
            "A URI reference that uniquely identifies the problem type only "
            "in the context of the provided API. Opposed to the specification in RFC-9457, "
            "it is neither recommended to be dereferenceable and point to a human-readable "
            "documentation nor globally unique for the problem type"
        ),
        examples=["/some/uri-reference"],
    )
    title: str | None = Field(
        default=None,
        description=(
            "A short summary of the problem type. Written in English and readable "
            "for engineers, usually not suited for non technical stakeholders and "
            "not localized."
        ),
        examples=["some title for the error situation"],
    )
    status: int | None = Field(
        default=None,
        ge=100,
        lt=600,
        description=(
            "The HTTP status code generated by the origin server for this occurrence "
            "of the problem"
        ),
    )
    detail: str | None = Field(
        default=None,
        description=(
            "A human readable explanation specific to this occurrence of the "
            "problem that is helpful to locate the problem and give advice on how "
            "to proceed. Written in English and readable for engineers, usually not "
            "suited for non technical stakeholders and not localized."
        ),
        examples=["some description for the error situation"],
    )
    instance: str | None = Field(
        default=None,
        description=(
            "A URI reference that identifies the specific occurrence of the problem, "
            "e.g. by adding a fragment identifier or sub-path to the problem type. "
            "May be used to locate the root of this problem in the source code."
        ),
        examples=["/some/uri-reference#specific-occurrence-context"],
    )

    @classmethod
    def from_status(
        cls,
        status: int,
        type: str | None = None,  # noqa: A002
        title: str | None = None,
        detail: str | None = None,
        instance: str | None = None,
        **extra: Any,  # noqa: ANN401
    ) -> "Problem":
        """Create a new Problem object from given HTTP Status code.

        Problem title and detail will default respectively to `phrase` and `description``
        properties of `HTTPStatus` enum constant corresponding to given status like
        `HTTPstatus(status).phrase` and `HTTPstatus(status).description`
        """
        status_obj = HTTPStatus(status)
        return Problem(
            status=status,
            type=type or cls.DEFAULT_TYPE,
            title=title or status_obj.phrase,
            detail=detail or status_obj.description,
            instance=instance,
            **extra,
        )


class ProblemException(Exception):  # noqa: N818
    def __init__(  # noqa: PLR0913
        self,
        status: int,
        title: str | None = None,
        detail: str | None = None,
        type: str | None = None,  # noqa: A002
        instance: str | None = None,
        headers: dict[str, str] | None = None,
        **extra: Any,  # noqa: ANN401
    ) -> None:
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type
        self.instance = instance
        self.headers = headers
        self.extra = extra


class ProblemResponse(JSONResponse):
    media_type = "application/problem+json"

    def __init__(  # noqa: PLR0913
        self,
        status: int,
        title: str | None = None,
        detail: str | None = None,
        type: str | None = None,  # noqa: A002
        instance: str | None = None,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        **extra: Any,  # noqa: ANN401
    ) -> None:
        problem = Problem.from_status(
            status=status,
            type=type,
            title=title,
            detail=detail,
            instance=instance,
            **extra,
        )
        super().__init__(
            problem.model_dump(mode="json"),
            status,
            headers,
            media_type,
            background,
        )