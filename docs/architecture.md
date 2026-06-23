# Architecture

## Overview

Dynamic Assessment API follows a modular monolith architecture with a global layered structure.

The application is deployed as a single backend service, but its internal code is organized into clear layers. Each layer has a specific responsibility and communicates with the adjacent layers in a controlled way.

This approach keeps the project simple enough for the MVP while still supporting maintainability, testing, and future growth.

---

## Architectural Style

The selected architecture is:

**Modular monolith with global layers**

This means:

- The system is implemented as one backend application.
- The codebase is organized by technical layers.
- Business responsibilities are separated into services.
- Database access is isolated in repositories.
- External integrations are isolated from the core application.

Microservices are intentionally out of scope for the MVP.

---

## Why Not Microservices?

Microservices are not required for the MVP because the project does not yet need:

- Independent deployments per service.
- Service-to-service communication.
- Distributed transactions.
- Complex infrastructure.
- Advanced monitoring across multiple services.

A modular monolith provides a better balance between simplicity and maintainability for this stage of the product.

---

## High-Level Flow

The typical request flow is:

```text
Client / Frontend / Bruno
        ↓
FastAPI Router
        ↓
Service
        ↓
Repository
        ↓
SQLAlchemy Model
        ↓
PostgreSQL
```

For external AI feedback:

```text
Service
   ↓
Integration Client
   ↓
LLM Provider
```

---

## Layered Structure

The project uses the following global layers:

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
```

Each layer has a specific responsibility.

---

## Layers

### Routers

Routers define the HTTP interface of the application.

Responsibilities:

- Receive HTTP requests.
- Read path parameters, query parameters, and request bodies.
- Call the appropriate service.
- Return HTTP responses.
- Define route-level dependencies when needed.

Routers should not contain complex business logic.

Examples:

```text
POST /auth/login
POST /courses
GET /assessments/{assessment_id}/form
POST /attempts/{attempt_id}/submit
```

---

### Services

Services contain the business logic of the application.

Responsibilities:

- Enforce business rules.
- Coordinate workflows.
- Validate contextual permissions.
- Use repositories to access data.
- Coordinate transactions.
- Call external integrations when needed.
- Decide how domain operations should behave.

Examples:

```text
AuthService
UserService
CourseService
QuestionService
AssessmentService
FormService
AttemptService
GradingService
AIFeedbackService
```

Services are the main place for application behavior.

---

### Repositories

Repositories isolate database access.

Responsibilities:

- Query the database.
- Create records.
- Update records.
- Encapsulate SQLAlchemy queries.
- Provide reusable data access methods to services.

Examples:

```text
UserRepository
CourseRepository
QuestionRepository
AssessmentRepository
AttemptRepository
```

Repositories should not contain business decisions. They should focus on data access.

---

### Models

Models represent database tables using SQLAlchemy.

Responsibilities:

- Define tables.
- Define columns.
- Define relationships.
- Define database constraints.

Examples:

```text
User
Role
UserRole
Course
Enrollment
Question
QuestionOption
Assessment
AssessmentQuestion
VisibilityRule
AssessmentAttempt
QuestionAnswer
AIFeedback
```

Models should not contain complex business workflows.

---

### Schemas

Schemas define request and response contracts using Pydantic.

Responsibilities:

- Validate input data.
- Define response structures.
- Prevent internal fields from being exposed accidentally.
- Document API data shapes.

Examples:

```text
UserCreate
UserRead
CourseCreate
CourseRead
QuestionCreate
AssessmentCreate
AttemptSubmit
```

Schemas are not database models. They represent data exchanged through the API.

---

### Core

The core layer contains shared application infrastructure.

Responsibilities:

- Application settings.
- Security utilities.
- Password hashing.
- JWT handling.
- Common dependencies.
- Custom exceptions.
- Shared constants.

Examples:

```text
config.py
security.py
dependencies.py
exceptions.py
```

---

### Integrations

The integrations layer contains clients for external services.

Responsibilities:

- Communicate with external providers.
- Hide provider-specific implementation details.
- Handle external service errors.
- Provide a stable interface to services.

Initial integration:

```text
LLM provider through OpenRouter
```

The rest of the application should not depend directly on OpenRouter. It should depend on an internal integration interface or client.

---

### Static Files

The static layer stores files served directly by the backend.

Initial use:

```text
static/images/
```

Question images are stored locally in the backend project and exposed through public static URLs.

This allows the frontend to render question images without requiring an external file server during the MVP.

---

## Proposed Folder Structure

```text
dynamic-assessment-api/
  app/
    main.py

    core/
      config.py
      security.py
      dependencies.py
      exceptions.py

    models/
      user.py
      course.py
      question.py
      assessment.py
      attempt.py
      ai_feedback.py

    schemas/
      auth.py
      user.py
      course.py
      question.py
      assessment.py
      attempt.py
      ai_feedback.py

    repositories/
      user_repository.py
      course_repository.py
      question_repository.py
      assessment_repository.py
      attempt_repository.py
      ai_feedback_repository.py

    services/
      auth_service.py
      user_service.py
      course_service.py
      question_service.py
      assessment_service.py
      form_service.py
      attempt_service.py
      grading_service.py
      ai_feedback_service.py

    routers/
      auth.py
      users.py
      courses.py
      questions.py
      assessments.py
      attempts.py

    integrations/
      llm_client.py

    static/
      images/

  alembic/
  bruno/
  docs/
  scripts/
  tests/

  docker-compose.yml
  README.md
  .env.example
  .gitignore
```

---

## Dependency Direction

Dependencies should flow inward and downward:

```text
Router → Service → Repository → Model → Database
```

Allowed dependencies:

- Routers may depend on services and schemas.
- Services may depend on repositories, schemas, integrations, and core utilities.
- Repositories may depend on models and database sessions.
- Models should not depend on routers, services, or repositories.
- Integrations should not contain domain rules.
- Core utilities may be used across layers.

Disallowed dependencies:

- Repositories should not call services.
- Models should not call repositories.
- Routers should not access the database directly.
- Business rules should not be implemented inside routers.
- External provider logic should not be spread across services.

---

## Example Request Flow

Example: submitting an assessment attempt.

```text
POST /attempts/{attempt_id}/submit
```

Flow:

```text
1. Router receives the HTTP request.
2. Router extracts the authenticated user.
3. Router calls AttemptService.submit_attempt().
4. AttemptService validates ownership and permissions.
5. AttemptService validates required answers.
6. AttemptService validates visibility rules.
7. AttemptService calls GradingService.
8. AttemptService calls AIFeedbackService when open-text feedback is required.
9. Repositories persist changes.
10. The transaction is committed.
11. Router returns the response.
```

---

## Business Logic Placement

Business logic belongs in services.

Examples of business logic:

- Checking if a teacher owns a course.
- Checking if a student is enrolled in a course.
- Checking if an assessment is published.
- Checking whether a question is visible.
- Checking whether required questions were answered.
- Calculating attempt scores.
- Deciding when AI feedback should be generated.

Routers should delegate these decisions to services.

---

## Transaction Strategy

Critical workflows must be handled atomically.

Examples:

- Creating an assessment with questions.
- Starting an assessment attempt.
- Saving partial answers.
- Submitting an assessment attempt.
- Grading an attempt.
- Storing AI feedback.

Atomic operation means:

- All required changes are saved successfully, or
- No partial changes are committed if an error occurs.

Services are responsible for coordinating transactions.

---

## Validation Strategy

Validation happens at multiple levels.

### Schema Validation

Handled by Pydantic schemas.

Examples:

- Required fields.
- Data types.
- Basic input structure.

### Business Validation

Handled by services.

Examples:

- Permission checks.
- Enrollment checks.
- Published assessment checks.
- Visibility rules.
- Required visible questions.

### Database Validation

Handled by the database and SQLAlchemy models.

Examples:

- Foreign keys.
- Unique constraints.
- Non-null constraints.

---

## Error Handling Strategy

The application should expose clear and consistent errors.

Common error categories:

- Authentication errors.
- Authorization errors.
- Validation errors.
- Not found errors.
- Conflict errors.
- External service errors.

External service failures, such as LLM provider errors, should not corrupt saved application data.

---

## AI Integration Strategy

AI feedback is part of the MVP.

The AI integration should be isolated in the integrations layer and used through the AI feedback service.

Responsibilities:

- Build the prompt.
- Send the request to the LLM provider.
- Parse the response.
- Store generated feedback.
- Handle provider errors safely.

The system must not depend directly on provider-specific logic outside the integration layer.

---

## Static Image Strategy

Question images are stored in the backend under:

```text
app/static/images/
```

The backend exposes this directory through a static route.

The API returns an image URL as part of the question payload.

Example response field:

```json
{
  "image_url": "/static/images/example-question.png"
}
```

The frontend can render the image using the provided URL.

---

## Design Rules

The project follows these design rules:

1. Routers handle HTTP concerns only.
2. Services handle business rules.
3. Repositories handle database access.
4. Models define persistence structure.
5. Schemas define API contracts.
6. Integrations isolate external providers.
7. Critical operations use transactions.
8. Backend validation is mandatory for business rules.
9. Static files are served through a controlled backend path.
10. Secrets are loaded from environment variables.

---

## Out of Scope for the MVP

The following architectural concerns are out of scope for the MVP:

- Microservices.
- Event-driven architecture.
- Message queues.
- Distributed transactions.
- Cloud file storage.
- Multi-tenant architecture.
- Advanced observability stack.
- Separate AI service deployment.

---

## Future Evolution

If the project grows, the architecture may evolve toward a more modular structure such as:

```text
app/
  modules/
    courses/
      router.py
      service.py
      repository.py
      schemas.py
    assessments/
      router.py
      service.py
      repository.py
      schemas.py
```

For the MVP, the global layered structure is preferred because it is simpler, clear, and easier to maintain while learning and building the first version.

---

## Summary

Dynamic Assessment API uses a modular monolith with global layers.

The main architectural goal is to keep the codebase organized, maintainable, and clear without introducing unnecessary infrastructure complexity.

This architecture supports the MVP while leaving room for future growth.