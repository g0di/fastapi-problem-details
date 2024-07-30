from typing import Any

from fastapi import FastAPI, status

import fastapi_problem_details
from fastapi_problem_details.problem import ProblemException

app = FastAPI()

fastapi_problem_details.init_app(app)


@app.get("/")
def raise_error() -> Any:  # noqa: ANN401
    raise ProblemException(
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="One or several internal services are not working properly",
        service_1="down",
        service_2="up",
        headers={"Retry-After": "30"},
    )
