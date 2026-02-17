# Database Migrations

This directory will contain Alembic migration scripts for database schema changes.

## Directory Structure

```
migrations/
├── versions/          # Migration version files (created by alembic revision command)
├── env.py            # Alembic environment configuration
└── README.md          # This file
```

## Usage

When migrations/ directory is available:

1. Run `alembic revision --autogenerate -m "description"` to create a new migration
2. Run `alembic upgrade head` to apply migrations
3. Run `alembic downgrade -1` to revert last migration

## Database Schema

The application uses the following tables:

- **files**: Uploaded file metadata
- **templates**: Template definitions
- **mappings**: Column mappings between files and templates
- **jobs**: Batch processing job tracking
- **job_outputs**: Generated output documents

See `migrations.py` for SQLAlchemy model definitions.

## Notes

- Migrations directory structure is created dynamically when running alembic commands
- The migrations.py file contains base SQLAlchemy models
- PostgreSQL is the target database (using psycopg2-binary driver)
