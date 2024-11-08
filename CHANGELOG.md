# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
