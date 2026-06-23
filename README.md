# Dynamic Assessment API

Dynamic Assessment API is a backend platform for managing dynamic academic assessments in a university environment.

The system allows administrators and teachers to manage users, courses, enrollments, reusable questions, assessments, student attempts, grading, and AI-assisted feedback.

The project is designed as a modular monolith using a layered architecture.

---

## Project Status

This project is currently in the initial setup phase.

The product scope, domain model, architecture, database design, and API design are documented before implementation.

Current documentation:

```text
docs/
├── mvp.md
├── domain.md
├── architecture.md
├── database-design.md
└── api-design.md
```

---

## Main Features

The MVP includes:

- User management with multiple roles.
- Role-based access control.
- Course management.
- Student enrollments.
- Shared reusable question bank.
- Dynamic assessments.
- Dynamic form rendering support.
- Partial answer saving.
- Resumable assessment attempts.
- Automatic grading for objective questions.
- AI-assisted feedback for open-text answers.
- Static image support for questions.
- Soft delete for selected resources.

---

## Main Roles

The system supports the following roles:

- `admin`
- `teacher`
- `student`

A user may have more than one role.

---

## Technology Stack

Planned technologies:

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT authentication
- Docker
- Bruno
- OpenRouter
- GitHub

---

## Architecture

The application follows a modular monolith architecture with global layers.

Planned structure:

```text
app/
  main.py

  core/
  models/
  schemas/
  repositories/
  services/
  routers/
  integrations/
  static/
    images/
```

Layer responsibilities:

- `routers/`: HTTP endpoints.
- `services/`: business logic.
- `repositories/`: database access.
- `models/`: SQLAlchemy models.
- `schemas/`: Pydantic request and response schemas.
- `core/`: configuration, security, and shared utilities.
- `integrations/`: external service clients.
- `static/images/`: local static images served by the backend.

---

## Documentation

Detailed design documents are available in the `docs/` directory:

| Document | Purpose |
| :--- | :--- |
| `docs/mvp.md` | Product scope and MVP definition. |
| `docs/domain.md` | Domain model, entities, relationships, and business rules. |
| `docs/architecture.md` | Application architecture and layer responsibilities. |
| `docs/database-design.md` | Initial relational database design. |
| `docs/api-design.md` | Main API endpoints, permissions, and workflows. |

---

## Local Development

Local development instructions will be added as the implementation progresses.

Planned setup:

```text
1. Create a virtual environment.
2. Install dependencies.
3. Configure environment variables.
4. Start PostgreSQL with Docker.
5. Run Alembic migrations.
6. Seed initial data.
7. Start the FastAPI application.
```

---

## Environment Variables

The project will use environment variables for sensitive configuration.

An example file will be provided:

```text
.env.example
```

Local secrets must be stored in:

```text
.env
```

The `.env` file must not be committed to the repository.

Expected variables:

```env
DATABASE_URL=
SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
```

---

## API Testing

The API will be tested using:

- FastAPI Swagger UI
- Bruno collections

The Bruno collection will be stored in:

```text
bruno/
```


---

## Current Phase

The project is currently in:

```text
Phase 6 — Project Preparation
```

Previous completed planning phases:

```text
Phase 0 — Product discovery
Phase 1 — MVP definition
Phase 2 — Domain modeling
Phase 3 — Architecture design
Phase 4 — Database design
Phase 5 — API design
```

Next implementation phase:

```text
Phase 7 — Base backend implementation
```

---

## License

License information will be added later.