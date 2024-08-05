# fastapi-problem-details <!-- omit in toc -->

This FastAPI plugin allow you to automatically format any errors as Problem details described in [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html). This allow rich error responses and consistent errors formatting within a single or multiple APIs.

- [Getting Started](#getting-started)
- [Validation errors handling](#validation-errors-handling)
  - [Changing default validation error status code and/or detail](#changing-default-validation-error-status-code-andor-detail)
- [HTTP errors handling](#http-errors-handling)
  - [Unexisting routes error handling](#unexisting-routes-error-handling)
- [Unhandled errors handling](#unhandled-errors-handling)
  - [Including exceptions type and stack traces](#including-exceptions-type-and-stack-traces)
- [Custom errors handling](#custom-errors-handling)
- [Returning HTTP errors as Problem Details](#returning-http-errors-as-problem-details)
  - [Keeping the code DRY](#keeping-the-code-dry)
    - [1. Inheritance](#1-inheritance)
    - [2. Custom error handlers](#2-custom-error-handlers)

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

And you're done! (mostly)

At this point any unhandled errors `Exception`, validation errors `fastapi.exceptions.RequestValidationError` and HTTP errors `starlette.exceptions.HTTPException` will be automatically handled and returned as Problem Details objects, for example, an unhandled error will be catched and returned as following JSON:

```json
{
  "type": "about:blank",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "Server got itself in trouble"
}
```

Now, let's dig a bit more on what the plugin is actually doing.

## Validation errors handling

Plugin will automatically handle any FastAPI `RequestValidationError` and returns a Problem Details response.

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

Trying to create an user using invalid payload will result in a validation error formatted as a Problem Details response. In particular, it will put the validation errors into an `errors` property in returned object.

```bash
curl -X POST http://localhost:8000/users/ -d '{}' -H "Content-Type: application/json"
{
  "type": "about:blank",
  "title": "Unprocessable Entity",
  "status": 422,
  "detail": "Request validation failed",
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

### Changing default validation error status code and/or detail

By default, validation errors will returns a 422 status code (FastAPI default) with a `"Request validation failed"` detail message.
However, you can override both of those if you want.

```python
from fastapi import FastAPI, status
import fastapi_problem_details as problem


app = FastAPI()

problem.init_app(app, validation_error_code=status.HTTP_400_BAD_REQUEST, validation_error_detail="Invalid payload!")
```

## HTTP errors handling

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
}
```

The `title` property is the official phrase corresponding to the HTTP status code.
The `detail` property is filled with the one passed to the raised `HTTPException` and defaults to the description of the HTTP status code `http.HTTPStatus(status).description` if not provided.

> Note that `headers` passed to the `HTTPException` will be returned as well.

### Unexisting routes error handling

Requests against non existing routes of your API also raise 404 `HTTPException`. The key difference is in the `detail` property message. This is pretty handy for clients to distinguish between a resource not found (e.g: trying to get an user which does not exist) and a route not existing

```bash
curl -X POST http://localhost:8000/not-exist
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Nothing matches the given URI",
}
```

## Unhandled errors handling

Any unhandled errors raised during processing of a request will be automatically handled by the plugin which will returns an internal server error formatted as a Problem Details.

> Also note that the exception will be logged as well using logger named `fastapi_problem_details.error_handlers`

The message of the error `str(exception)` will be used as the `detail` property and will default to a more generic message when not defined.

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
    raise CustomError

@app.get("/with-details")
def raise_error() -> Any:  # noqa: ANN401
    raise CustomError("Something went wrong...")
```

```bash
$ curl http://localhost:8000
{
  "type": "about:blank",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "Server got itself in trouble",
}
$ curl http://localhost:8000/with-details
{
  "type": "about:blank",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "Something went wrong...",
}
```

### Including exceptions type and stack traces

During development, it can sometimes be useful to include in your HTTP responses the type and stack trace of unhandled errors for easier debugging.

```python
problem.init_app(app, include_exc_info_in_response=True)
```

Doing so will enrich Problem Details response with exception type `exc_type` (`str`) and stack trace `exc_stack` (`list[str]`)

```bash
$ curl http://localhost:8000
{
  "type": "about:blank",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "Server got itself in trouble",
  "exc_type": "snippet.CustomError",
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
  ]
}
```

> :warning: This feature is expected to be used only for development purposes. You should not enable this on production because it can leak sensitive internal information. Use it at your own risk.

## Custom errors handling

To handle specific errors in your API you can simply register custom error handlers (see [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers)) and returns `ProblemResponse` object.

```python
from typing import Any

from fastapi import FastAPI, Request, status

import fastapi_problem_details as problem
from fastapi_problem_details import ProblemResponse

app = FastAPI()
problem.init_app(app)


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

Note that in this example I've provided a custom `type` property but this might not be necessary for this use case. Basically, you should only use specific type and title when your error goes beyond the original meaning of the HTTP status code. See the [RFC](https://datatracker.ietf.org/doc/html/rfc9457#name-defining-new-problem-types) for more details.

> Likewise, truly generic problems -- i.e., conditions that might apply to any resource on the Web -- are usually better expressed as plain status codes. For example, a "write access disallowed" problem is probably unnecessary, since a 403 Forbidden status code in response to a PUT request is self-explanatory.

Also note that you can additional properties to the `ProblemResponse` object like `headers` or `instance`. Any extra properties will be added as-is in the returned Problem Details object (like the `user_id` in this example)

## Returning HTTP errors as Problem Details

As shown in previous sections, any `HTTPException` raised during a request cause the API to respond with a well formatted Problem Details object. However, what if we want to raise a `HTTPException` but with extra properties or Problem Details specific properties?

In that case you can instead raise a `ProblemException` exception.

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
{
  "type":"about:blank",
  "title":"Service Unavailable",
  "status":503,
  "detail":"One or several internal services are not working properly","service_1":"down",
  "service_2":"up"
}
```

The `ProblemException` exception takes almost same arguments as a `ProblemResponse`.

### Keeping the code DRY

If you start having to raise almost the same `ProblemException` in several places of your code (for example when you validate a requester permissions) you have too ways to avoid copy-pasting the same object in many places of your code

#### 1. Inheritance

Simply create your own subclass of `ProblemException`

```python
from fastapi import status

from fastapi_problem_details.models import ProblemException


class UserPermissionError(ProblemException):
    def __init__(
        self,
        user_id: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status=status.HTTP_403_FORBIDDEN,
            detail=f"User {user_id} is not allowed to perform this operation",
            headers=headers,
            user_id=user_id,
        )


def do_something_meaningful(user_id: str):
    raise UserPermissionError(user_id)
```

The advantage of this solution is that its rather simple and straightforward. You do not have anything else to do to properly returns Problem Details responses.

The main issue of this is that it can cause your code to cross boundaries. If you start to use `ProblemException` into your domain logic, you couple your core code with your primary adapter (See ports and adapters pattern), your API. If you decide to build a CLI and/or and event based application using the same core logic, you'll end up with uncomfortable problem exception and status code which has no meaning here.

#### 2. Custom error handlers

The other approach is to only use custom exceptions in your code and add custom error handlers in your FastAPI app to properly map your core errors with Problem Details.

```python
from typing import Any

from fastapi import FastAPI, Request, status

import fastapi_problem_details as problem
from fastapi_problem_details import ProblemResponse

app = FastAPI()
problem.init_app(app)


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
    raise get_user_by_id(user_id)


# somewhere else, in a repository.py file for example or dao.py
db: dict[str, dict[str, Any]] = {}

def get_user_by_id(user_id: str):
  if user_id not in db:
    raise UserNotFoundError(user_id)
```

The biggest advantage of this solution is that you decouple your core code from your FastAPI app. You can define regular Python exceptions whatever you want and just do the conversion for your API in your custom error handler(s).

The disadvantage obviously is that it requires you to write more code. Its a question of balance.
