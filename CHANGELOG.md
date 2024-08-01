# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
