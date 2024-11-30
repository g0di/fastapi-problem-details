# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## Docs

- Aligned this changelog with actual github releases
- Updated project URL pointing to this changelog (for PyPi)

## [0.1.4] - 2024-11-08

## Fixed

- Fixed the content type of the `default` problem details response in the generated FastAPI OpenAPI specification to `application/problem+json` ([#720e154](https://github.com/g0di/fastapi-problem-details/commit/720e1541053b416123ac67b3c90ef4c71d7c5e44))

## Docs

- Add a troubleshooting section in the documentation about a small workaround when dealing with FastAPI `APIRouter` routers ([#447df1e](https://github.com/g0di/fastapi-problem-details/commit/447df1e319efb966c9484ffa5338978c8b53e2e9))

## [0.1.3] - 2024-11-04

### Fixed

- Fixed incorrect problem details openapi schema examples ([#b9769fb](https://github.com/g0di/fastapi-problem-details/commit/b9769fbbfb6279e62776f93c20c27e7bf3d7062a))

### Docs

- Updated the doc examples to align with changes made in previous release
- Add a section explaining how to document and register additional problem details
- Mention that `null` values are stripped from returned problem details
- Mention that all error handlers can be overriden

## [0.1.2] - 2024-08-01

### Fixed

- Remove unexpected `ge` and `lt` properties from generated JSON Schema for `status` property of `Problem` schema.

## [0.1.1] - 2024-08-01

### Added

- Added external documentation pointing to the official Problem details RFC in the Problem OpenAPI Schema

### Changed

- `exc_type` simplified property returned in problem responses for unhandled errors (was `<class 'path.to.module.YourError'>`, now `path.to.module.YourError`)
- `null`/`None` values are now omitted from Problem response. Problem JSON Schema has been updated to reflect that

### Fixed

- Constraints on Problem status code (`100 <= status code < 600`) is now properly displayed in the Problem JSON Schema

## [0.1.0] - 2024-07-30

### Added

- Add ability to register the plugin to transform unhandled, validation and http errors as problem details response
- Add ability to raise `ProblemException` directly for returning problem details responses
- Add ability to returns `ProblemResponse` objects for returning problem details responses

[unreleased]: https://github.com/g0di/fastapi-problem-details/compare/0.1.4...HEAD
[0.1.4]: https://github.com/g0di/fastapi-problem-details/releases/tag/0.1.4
[0.1.3]: https://github.com/g0di/fastapi-problem-details/releases/tag/0.1.3
[0.1.2]: https://github.com/g0di/fastapi-problem-details/releases/tag/0.1.2
[0.1.1]: https://github.com/g0di/fastapi-problem-details/releases/tag/0.1.1
[0.1.0]: https://github.com/g0di/fastapi-problem-details/releases/tag/0.1.0
