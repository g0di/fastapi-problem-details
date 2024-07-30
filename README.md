# fastapi-problem-details <!-- omit in toc -->

This FastAPI plugin allow you to automatically format any errors as Problem details described in [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html). This allow rich error responses and consistent errors formatting within a single or multiple APIs.

- [Getting Started](#getting-started)
- [Handling validation errors](#handling-validation-errors)
- [Handling a HTTPException](#handling-a-httpexception)
- [Handling request against non existing routes](#handling-request-against-non-existing-routes)
- [Changing default validation error status code and/or detail](#changing-default-validation-error-status-code-andor-detail)
- [Including unhandled exceptions type and stack traces](#including-unhandled-exceptions-type-and-stack-traces)
- [Registering custom error handlers](#registering-custom-error-handlers)
- [Raising ProblemException to returns error with more details](#raising-problemexception-to-returns-error-with-more-details)

## Getting Started

Install the plugin

```bash
pip install fastapi-problem-details
```

Register the plugin against your FastAPI app

```python
from fastapi import FastAPI
import fastapi_problem_details as problem


app = FastAPI()

problem.init_app(app)
```

At this point any unhandled errors, validation errors and HTTP errors will be automatically formatted as Problem details objects.

## Handling validation errors

Plugin will automatically handle any FastAPI `RequestValidationError`.

```python
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

import fastapi_problem_details as problem

app = FastAPI()

problem.init_app(app)


class User(BaseModel):
    id: str
    name: str


@app.post("/users/")
def create_user(_user: User) -> Any:  # noqa: ANN401
    pass
```

Trying to create an user using invalid payload will result in a validation error formatted as a Problem detail response

```bash
curl -X POST http://localhost:8000/users/ -d '{}' -H "Content-Type: application/json"
{
  "type": "about:blank",
  "title": "Unprocessable Entity",
  "status": 422,
  "detail": "",
  "instance": null,
  "errors": [
    {
      "type": "missing",
      "loc": [
        "body",
        "id"
      ],
      "msg": "Field required",
      "input": {}
    },
    {
      "type": "missing",
      "loc": [
        "body",
        "name"
      ],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

## Handling a HTTPException

Any FastAPI or starlette `HTTPException` raised during a request will be automatically catched and formatted as a Problem details response.

```python
from typing import Any

from fastapi import FastAPI, HTTPException, status

import fastapi_problem_details as problem

app = FastAPI()

problem.init_app(app)


@app.get("/")
def raise_error() -> Any:  # noqa: ANN401
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
```

Requesting this endpoint will get you the following response

```bash
curl http://localhost:8000/
{
  "type":"about:blank",
  "title":"Unauthorized",
  "status":401,
  "detail":"No permission -- see authorization schemes",
  "instance":null
}
```

> Note that any `headers` passed to the `HTTPException` will be returned as well.

> Note that you can override the returned `detail` property by passing a detail argument to the `HTTPException` like `HTTPException(status, detail="Oops!")`

## Handling request against non existing routes

Requests against non existing routes are also handled and returned as Problem details response automatically.

```bash
curl -X POST http://localhost:8000/not-exist
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Nothing matches the given URI",
  "instance": null
}
```

> Here the `detail` property allow a client to distinguish a 404 caused by an incorrect URL

## Changing default validation error status code and/or detail

By default, validation errors will returns a 422 status code (FastAPI default) with a `"Request validation failed"` detail message.
However, you can override both of those if you want.

```python
from fastapi import FastAPI, status
import fastapi_problem_details as problem


app = FastAPI()

problem.init_app(app, validation_error_code=status.HTTP_400_BAD_REQUEST, validation_error_detail="Invalid payload!")
```

## Including unhandled exceptions type and stack traces

During development, it can sometimes be useful to include in your HTTP responses the type and stack trace of an unhandled error for easier debugging.

```python
from typing import Any

from fastapi import FastAPI

import fastapi_problem_details as problem

app = FastAPI()

problem.init_app(app, include_exc_info_in_response=True)


class CustomError(Exception):
    pass


@app.get("/")
def raise_error() -> Any:  # noqa: ANN401
    return do_something()


def do_something():
    raise CustomError

```

When requesting an endpoint raising an unhandled error you'll get a problem detail like the following

```bash
$ curl http://localhost:8000
{
  "type": "about:blank",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "Server got itself in trouble",
  "instance": null,
  "exc_stack": [
    "Traceback (most recent call last):\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/middleware/errors.py\", line 164, in __call__\n    await self.app(scope, receive, _send)\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/middleware/exceptions.py\", line 65, in __call__\n    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py\", line 64, in wrapped_app\n    raise exc\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py\", line 53, in wrapped_app\n    await app(scope, receive, sender)\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/routing.py\", line 756, in __call__\n    await self.middleware_stack(scope, receive, send)\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/routing.py\", line 776, in app\n    await route.handle(scope, receive, send)\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/routing.py\", line 297, in handle\n    await self.app(scope, receive, send)\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/routing.py\", line 77, in app\n    await wrap_app_handling_exceptions(app, request)(scope, receive, send)\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py\", line 64, in wrapped_app\n    raise exc\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py\", line 53, in wrapped_app\n    await app(scope, receive, sender)\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/routing.py\", line 72, in app\n    response = await func(request)\n               ^^^^^^^^^^^^^^^^^^^\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/fastapi/routing.py\", line 278, in app\n    raw_response = await run_endpoint_function(\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/fastapi/routing.py\", line 193, in run_endpoint_function\n    return await run_in_threadpool(dependant.call, **values)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/starlette/concurrency.py\", line 42, in run_in_threadpool\n    return await anyio.to_thread.run_sync(func, *args)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/anyio/to_thread.py\", line 56, in run_sync\n    return await get_async_backend().run_sync_in_worker_thread(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py\", line 2177, in run_sync_in_worker_thread\n    return await future\n           ^^^^^^^^^^^^\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py\", line 859, in run\n    result = context.run(func, *args)\n             ^^^^^^^^^^^^^^^^^^^^^^^^\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/snippet.py\", line 22, in raise_error\n    return raise_some_error()\n           ^^^^^^^^^^^^^^^^^^\n",
    "  File \"/Users/gody/Development/OpenSource/fastapi-problem-details/snippet.py\", line 17, in raise_some_error\n    raise CustomError\n",
    "snippet.CustomError\n"
  ],
  "exc_type": "<class 'snippet.CustomError'>"
}
```

By doing so, any unhandled errors will ends up with a Problem details response including a `exc_type` and `exc_stack` properties containing respectively the type of the exception and its stack traces as a list of strings.

> :warning: This feature is expected to be used only for development purposes. You should not enable this on production because it can leak sensitive internal information. Use it at your own risk.

## Registering custom error handlers

To handle specific errors in your API you can register custom error handlers. When doing so use the `ProblemResponse` class for returning Problem details responses

```python
from typing import Any

from fastapi import FastAPI, Request, status

import fastapi_problem_details as problem
from fastapi_problem_details import ProblemResponse

app = FastAPI()
problem.init_app(app) # Note that this is not required if you simply return ProblemResponse object yourself


class UserNotFoundError(Exception):
    def __init__(self, user_id: str) -> None:
        super().__init__(f"There is no user with id {user_id!r}")
        self.user_id = user_id


@app.exception_handler(UserNotFoundError)
async def handle_user_not_found_error(
    _: Request, exc: UserNotFoundError
) -> ProblemResponse:
    return ProblemResponse(
        status=status.HTTP_404_NOT_FOUND,
        type="/problems/user-not-found",
        title="User Not Found",
        detail=str(exc),
        user_id=exc.user_id,
    )


@app.get("/users/{user_id}")
def get_user(user_id: str) -> Any:  # noqa: ANN401
    raise UserNotFoundError(user_id)

```

Requesting an user will get you following problem details

```bash
$ curl http://localhost:8000/users/1234
{
  "type":"/problems/user-not-found",
  "title":"User Not Found",
  "status":404,
  "detail":"There is no user with id '1234'",
  "instance":null,
  "user_id":"1234"
}
```

## Raising ProblemException to returns error with more details

If you want to include more information in an error, instead of raising a `HTTPException` you can instead raise a `ProblemException`

```python
from typing import Any

from fastapi import FastAPI, status

import fastapi_problem_details as problem
from fastapi_problem_details import ProblemException

app = FastAPI()

problem.init_app(app)


@app.get("/")
def raise_error() -> Any:  # noqa: ANN401
    raise ProblemException(
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="One or several internal services are not working properly",
        service_1="down",
        service_2="up",
        headers={"Retry-After": "30"},
    )
```

```bash
curl http://localhost:8000 -v
*   Trying [::1]:8000...
* connect to ::1 port 8000 failed: Connection refused
*   Trying 127.0.0.1:8000...
* Connected to localhost (127.0.0.1) port 8000
> GET / HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/8.4.0
> Accept: */*
>
< HTTP/1.1 503 Service Unavailable
< date: Tue, 30 Jul 2024 14:10:02 GMT
< server: uvicorn
< retry-after: 30
< content-length: 186
< content-type: application/problem+json
<
* Connection #0 to host localhost left intact
{"type":"about:blank","title":"Service Unavailable","status":503,"detail":"One or several internal services are not working properly","instance":null,"service_1":"down","service_2":"up"}
```
