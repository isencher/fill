# fill

A web application for automatically filling 2D table data into template files.

## Project Overview

**fill** is a document automation tool that:
- Reads structured 2D table data (Excel, CSV, database)
- Maps data fields to template placeholders
- Generates filled documents (DOCX, PDF, etc.)

## Project Location

This project is developed inside the **fill-dev-env** container workspace:

```
┌─────────────────────────────────────────┐
│       Docker 容器（父环境）              │
│                                       │
│  ┌───────────────────────────────────┐  │
│  │   /app/fill-dev-env/             │  │
│  │                                 │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │   fill/ (本目录)            │  │  │
│  │  │                             │  │  │
│  │  │  ┌─── src/                 │  │  │
│  │  │  │   (源代码)              │  │  │
│  │  │  │                          │  │  │
│  │  │  ├── tests/                │  │  │
│  │  │  │   (测试代码)             │  │  │
│  │  │  │                          │  │  │
│  │  │  ├── .ralph/               │  │  │
│  │  │  │   (Ralph 配置)          │  │  │
│  │  │  │                          │  │  │
│  │  │  └── README.md             │  │  │
│  │  │                            │  │  │
│  │  └─────────────────────────────┘  │  │
│  │                                 │  │
│  └───────────────────────────────────┘  │
│                                       │
└─────────────────────────────────────────┘
```

## Tech Stack

**Status**: Tech stack not yet selected

**Recommended Options**:
- **Python**: FastAPI + pytest (recommended for document processing)
- **Node.js**: Express/Fastify + Vitest

## Directory Structure

```
fill/                      # Application project root (本目录)
├── src/                   # Source code (empty - awaiting implementation)
│   ├── api/              # API endpoints
│   ├── services/         # Business logic
│   ├── models/           # Data models
│   └── utils/            # Utilities
├── tests/                 # Test code (to be created)
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── .ralph/               # Ralph AI agent configuration
├── .ralphrc              # Ralph configuration
├── pyproject.toml        # Python config (to be created)
├── requirements.txt      # Python dependencies (to be created)
├── package.json          # Node.js config (to be created - optional)
└── README.md             # This file
```

## Container Environment

This project requires the **fill-dev-env** container:

| Container Provides | For This Project |
|------------------|------------------|
| Python 3.11 | Runtime environment |
| Node.js 20+ | E2E testing with Playwright |
| Browsers | Playwright E2E tests |
| PostgreSQL | Test database |
| pytest/vitest | Testing frameworks |
| Prometheus/Grafana | Metrics collection |

The container **must satisfy** requirements defined in:
- [docker-requirements.md](../docker-requirements.md) (in parent directory)

## Quick Start

```bash
# 1. Start the container (on host - in parent directory)
cd /app/fill-dev-env
docker-compose up -d

# 2. Enter the container
docker-compose exec app bash

# 3. Work on fill project (inside container)
cd /app/fill-dev-env/fill

# 4. Install dependencies (when tech stack is chosen)
pip install -r requirements.txt    # Python option
# or
npm install                        # Node.js option

# 5. Run tests
pytest

# 6. Run development server
uvicorn src.main:app --reload
```

## Development Standards

This project follows strict quality standards in `.ralph/AGENT.md`:

- **Minimum Test Coverage**: 85%
- **Test Pass Rate**: 100%
- **All Tests Must Pass** before committing
- **Conventional Commits** required
- **All changes pushed** to remote before moving to next feature

## Features

**Status**: Project in setup phase - no features implemented yet

**Planned Features**:
- [ ] File upload (Excel, CSV)
- [ ] Template management
- [ ] Field mapping UI
- [ ] Document generation (DOCX, PDF)
- [ ] Batch processing
- [ ] API for programmatic access

## Testing Targets

```
Coverage Requirements:
├── Unit Tests:     >90%  (business logic, services)
├── Integration:    >85%  (API endpoints, database)
└── E2E Tests:     100%  (critical user workflows)

Execution Time:
├── Unit + Integration: <30 seconds
└── E2E:              <2 minutes
```

## Documentation

- [Build Instructions](.ralph/AGENT.md) - Setup and quality standards
- [Development Tasks](.ralph/fix_plan.md) - Current development plan
- [Project Context](.ralph/PROMPT.md) - AI agent project prompt
- [Container Requirements](../docker-requirements.md) - 容器环境要求

## License

[Specify your license]
