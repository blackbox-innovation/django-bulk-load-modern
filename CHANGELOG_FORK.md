# Changelog - django-bulk-load-modern

All notable changes to this fork will be documented in this file.

## [2.0.0] - 2024-01-XX

### Added
- Full psycopg3 support - replaced psycopg2 with modern psycopg (version 3)
- SQL composition safety features using psycopg3's SQL building capabilities
- Comprehensive edge case tests for SQL injection protection
- Performance tests for large datasets
- Modern Python packaging with uv
- Python 3.12+ requirement for optimal performance

### Changed
- **BREAKING**: Now requires PostgreSQL 14+ (was PostgreSQL 10+)
- **BREAKING**: Now requires Python 3.12+ (was Python 3.6+)
- **BREAKING**: Replaced psycopg2 with psycopg3
- COPY operations now use psycopg3's context manager syntax
- JSON/JSONB field serialization updated for psycopg3
- Binary field detection improved
- Test runner uses `uv run` instead of direct Python execution
- Docker images built with uv for faster builds

### Fixed
- JSON field serialization now properly handles psycopg3's Json/Jsonb types
- Binary field detection now works correctly with psycopg3

### Known Limitations
- NULL value filtering in `bulk_select_model_dicts` with IN clauses doesn't work (SQL limitation, not specific to this implementation)

## Fork History
This project is a fork of [django-bulk-load](https://github.com/cedar-team/django-bulk-load) v1.4.3, created to provide psycopg3 support and modernize the codebase.