# API Design

## Overview

This document defines the initial API design for Dynamic Assessment API.

The goal is to describe the main API resources, endpoints, responsibilities, permissions, and workflows required for the MVP.

This document focuses on API behavior and does not define implementation details, SQLAlchemy models, or internal service logic.

---

## API Design Principles

The API follows these principles:

- Use clear REST-style endpoints.
- Use nouns for resources.
- Use HTTP methods consistently.
- Keep authentication separate from business resources.
- Resolve the authenticated user from the JWT token.
- Do not allow clients to send their own user identity when it can be derived from authentication.
- Keep business validation in the backend.
- Avoid exposing internal fields unnecessarily.
- Use soft delete where required by the domain model.
- Return enough information for a frontend to render dynamic assessment forms.

---

## Authentication

Most endpoints require authentication.

Authentication is handled using JWT.

The client sends the token using the Authorization header:

```text
Authorization: Bearer <access_token>
```

---

## Common HTTP Status Codes

The API may use the following status codes:

```text
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
500 Internal Server Error
502 Bad Gateway
```

Common meanings:

- `400 Bad Request`: invalid business operation.
- `401 Unauthorized`: missing or invalid authentication.
- `403 Forbidden`: authenticated user does not have permission.
- `404 Not Found`: requested resource does not exist.
- `409 Conflict`: duplicated or conflicting operation.
- `422 Unprocessable Entity`: invalid request body or schema validation error.
- `502 Bad Gateway`: external provider error, such as LLM provider failure.

---

# Endpoint Groups

## 1. Health

Health endpoints verify that the API is running.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| GET | `/health` | Check API status. | No |

---

## 2. Auth

Authentication and current user endpoints.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/auth/login` | Authenticate user and return access token. | No |
| GET | `/auth/me` | Return current authenticated user. | Yes |

### Notes

Public user registration is not supported in the MVP.

Users are created by authorized admins or teachers.

---

## 3. Users

User management endpoints.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/users` | Create a user. | Admin / authorized Teacher |
| GET | `/users` | List users. | Admin |
| GET | `/users/{user_id}` | Get user details. | Admin |
| PATCH | `/users/{user_id}` | Update basic user data. | Admin |
| DELETE | `/users/{user_id}` | Deactivate user using soft delete. | Admin |

### Business rules

- Users are not physically deleted in the MVP.
- Deleting a user means setting the user as inactive.
- Only active users can authenticate.
- Teachers may create student users only if allowed by the service rules.

---

## 4. Roles

Role management endpoints.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| GET | `/roles` | List available roles. | Admin |
| POST | `/users/{user_id}/roles/{role_name}` | Assign a role to a user. | Admin |
| DELETE | `/users/{user_id}/roles/{role_name}` | Remove a role from a user. | Admin |

### Supported roles

```text
admin
teacher
student
```

### Business rules

- A user may have more than one role.
- The same role cannot be assigned twice to the same user.

---

## 5. Courses

Course management endpoints.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/courses` | Create a course. | Admin / Teacher |
| GET | `/courses` | List courses. | Admin / Teacher |
| GET | `/courses/{course_id}` | Get course details. | Admin / Teacher |
| PATCH | `/courses/{course_id}` | Update course data. | Admin / Course Teacher |
| DELETE | `/courses/{course_id}` | Deactivate course using soft delete. | Admin / Course Teacher |

### Business rules

- If a teacher creates a course, the course is assigned to that teacher.
- If an admin creates a course, the request must include the teacher to assign.
- The assigned teacher must have the `teacher` role.
- Teachers may only manage their own courses.
- Courses are deactivated using soft delete.

---

## 6. Enrollments

Enrollment endpoints manage students enrolled in courses.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/courses/{course_id}/enrollments` | Enroll a student in a course. | Admin / Course Teacher |
| GET | `/courses/{course_id}/enrollments` | List students enrolled in a course. | Admin / Course Teacher |
| DELETE | `/courses/{course_id}/enrollments/{student_id}` | Remove or deactivate an enrollment. | Admin / Course Teacher |
| GET | `/me/courses` | List courses for the authenticated student. | Student |

### Business rules

- Only users with the `student` role may be enrolled.
- Duplicate enrollments are not allowed.
- Teachers may only manage enrollments for their own courses.
- Students may only view their own enrolled courses.

---

## 7. Questions

Question bank endpoints.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/questions` | Create a reusable question. | Admin / Teacher |
| GET | `/questions` | List active questions. | Admin / Teacher |
| GET | `/questions/{question_id}` | Get question details. | Admin / Teacher |
| DELETE | `/questions/{question_id}` | Deactivate question using soft delete. | Admin / Teacher |

### Business rules

- Questions are part of a shared question bank.
- Questions are reusable across assessments.
- Questions are not editable in the MVP.
- Each question may have at most one image.
- Images are served by the backend through static URLs.

### Question creation note

The MVP may support creating a question together with its options in a single request.

This simplifies the initial workflow for teachers.

---

## 8. Question Options

Question option endpoints manage options for closed questions.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/questions/{question_id}/options` | Add an option to a question. | Admin / Teacher |
| GET | `/questions/{question_id}/options` | List options for a question. | Admin / Teacher |
| DELETE | `/questions/{question_id}/options/{option_id}` | Remove or deactivate an option. | Admin / Teacher |

### Business rules

- Options apply mainly to `single_choice`, `multiple_choice`, `boolean`, and `scale`.
- A `single_choice` question should have one correct option.
- A `multiple_choice` question may have multiple correct options.
- Exclusive options cannot be combined with other options in the same student answer.

---

## 9. Assessments

Assessment endpoints manage evaluative activities.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/courses/{course_id}/assessments` | Create an assessment in a course. | Admin / Course Teacher |
| GET | `/courses/{course_id}/assessments` | List assessments in a course. | Admin / Course Teacher / Enrolled Student |
| GET | `/assessments/{assessment_id}` | Get assessment details. | Admin / Course Teacher |
| PATCH | `/assessments/{assessment_id}` | Update assessment basic data. | Admin / Course Teacher |
| DELETE | `/assessments/{assessment_id}` | Archive an assessment. | Admin / Course Teacher |
| POST | `/assessments/{assessment_id}/publish` | Publish an assessment. | Admin / Course Teacher |

### Supported assessment types

```text
quiz
workshop
exam
form
```

### Business rules

- Every assessment belongs to a course.
- Only course teachers or admins may manage assessments.
- Students can only access published assessments.
- Students can only access assessments from courses where they are enrolled.

---

## 10. Assessment Questions

Assessment question endpoints manage questions inside assessments.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/assessments/{assessment_id}/questions` | Add a question from the bank to an assessment. | Admin / Course Teacher |
| GET | `/assessments/{assessment_id}/questions` | List questions in an assessment. | Admin / Course Teacher |
| PATCH | `/assessments/{assessment_id}/questions/{assessment_question_id}` | Update order, score, or required flag. | Admin / Course Teacher |
| DELETE | `/assessments/{assessment_id}/questions/{assessment_question_id}` | Remove a question from an assessment. | Admin / Course Teacher |

### Business rules

- A question may be reused across assessments.
- A question cannot be added twice to the same assessment.
- Question order must be unique within the assessment.
- Question score and required flag are specific to the assessment.

---

## 11. Visibility Rules

Visibility rule endpoints manage dynamic form behavior.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/assessment-questions/{assessment_question_id}/visibility-rule` | Create a visibility rule. | Admin / Course Teacher |
| GET | `/assessment-questions/{assessment_question_id}/visibility-rule` | Get visibility rule. | Admin / Course Teacher |
| DELETE | `/assessment-questions/{assessment_question_id}/visibility-rule` | Delete visibility rule. | Admin / Course Teacher |

### Business rules

- In the MVP, each assessment question may have at most one visibility rule.
- Visibility rules depend on answers to previous assessment questions.
- The frontend may use rules for rendering.
- The backend must validate visibility before accepting final answers.

---

## 12. Forms

Form endpoints provide frontend-ready assessment structures.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| GET | `/assessments/{assessment_id}/form` | Get renderable form structure. | Enrolled Student |
| POST | `/assessments/{assessment_id}/form/visibility-preview` | Evaluate visibility based on current answers. | Enrolled Student |

### Form payload responsibilities

The form response may include:

- assessment information
- question id
- assessment question id
- question type
- statement
- image URL
- options
- validation rules
- score
- order
- required flag
- visibility rule

### Security rule

The form response must not expose correct answers.

---

## 13. Student Assessment Views

Student-focused endpoints.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| GET | `/me/pending-assessments` | List pending or in-progress assessments for the current student. | Student |
| GET | `/me/assessment-attempts` | List attempts for the current student. | Student |

### Pending assessments logic

`/me/pending-assessments` should include:

- published assessments from enrolled courses
- assessments not yet started by the student
- assessments with an `in_progress` attempt
- basic course and attempt status information

---

## 14. Attempts

Attempt endpoints manage student work on assessments.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/assessments/{assessment_id}/attempts/start` | Start or resume an in-progress attempt. | Student |
| GET | `/attempts/{attempt_id}` | Get attempt status. | Attempt Owner / Admin / Course Teacher |
| GET | `/attempts/{attempt_id}/form` | Get form with saved answers. | Attempt Owner |
| POST | `/attempts/{attempt_id}/answers` | Save or update a partial answer. | Attempt Owner |
| POST | `/attempts/{attempt_id}/submit` | Submit attempt for final grading. | Attempt Owner |
| GET | `/attempts/{attempt_id}/results` | Get attempt results. | Attempt Owner / Admin / Course Teacher |

### Business rules

- Student identity is resolved from the JWT token.
- The client must not send `student_id`.
- A student can start attempts only for published assessments.
- A student can start attempts only for courses where they are enrolled.
- If an `in_progress` attempt exists, the start endpoint should return or resume it.
- Partial answers can be saved while the attempt is `in_progress`.
- Submitted attempts should not allow answer modifications.
- Final submission must validate required visible questions.
- Final submission must be atomic.

---

## 15. Teacher Results

Teacher result endpoints allow reviewing assessment outcomes.

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| GET | `/assessments/{assessment_id}/attempts` | List attempts for an assessment. | Admin / Course Teacher |
| GET | `/assessments/{assessment_id}/results` | Get assessment results summary. | Admin / Course Teacher |
| GET | `/courses/{course_id}/results` | Get course results summary. | Admin / Course Teacher |

### Business rules

- Teachers may only access results for their own courses.
- Admins may access global results.

---

## 16. AI Feedback

AI feedback is generated automatically during final attempt submission.

Primary trigger:

```text
POST /attempts/{attempt_id}/submit
```

When an attempt is submitted:

1. Objective answers are graded automatically.
2. Open-text answers are sent for AI-assisted feedback.
3. AI feedback is stored in the `ai_feedback` table.
4. Attempt results are updated.

### Optional inspection endpoint

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| GET | `/question-answers/{answer_id}/ai-feedback` | Get AI feedback for a question answer. | Attempt Owner / Admin / Course Teacher |

### Business rules

- AI feedback applies mainly to `open_text` answers.
- AI feedback generation is automatic on attempt submission.
- If the LLM provider fails, the student answer must remain stored safely.
- Provider errors should not corrupt the attempt data.
- Failed AI feedback may be stored with status `failed`.

---

# Main Workflows

## Admin Workflow

```text
1. Admin logs in.
2. Admin creates users.
3. Admin assigns roles.
4. Admin creates a course and assigns a teacher.
5. Admin may inspect system-wide resources.
```

Related endpoints:

```text
POST /auth/login
POST /users
POST /users/{user_id}/roles/{role_name}
POST /courses
GET /users
GET /courses
```

---

## Teacher Workflow

```text
1. Teacher logs in.
2. Teacher creates or manages a course.
3. Teacher enrolls students.
4. Teacher creates reusable questions.
5. Teacher creates an assessment.
6. Teacher adds questions to the assessment.
7. Teacher configures order, score, required flags, and visibility rules.
8. Teacher publishes the assessment.
9. Teacher reviews attempts and results.
```

Related endpoints:

```text
POST /auth/login
POST /courses
POST /courses/{course_id}/enrollments
POST /questions
POST /courses/{course_id}/assessments
POST /assessments/{assessment_id}/questions
POST /assessment-questions/{assessment_question_id}/visibility-rule
POST /assessments/{assessment_id}/publish
GET /assessments/{assessment_id}/attempts
GET /assessments/{assessment_id}/results
```

---

## Student Workflow

```text
1. Student logs in.
2. Student views pending assessments.
3. Student starts or resumes an assessment attempt.
4. Student retrieves the form.
5. Student saves partial answers.
6. Student submits the attempt.
7. System grades objective answers.
8. System generates AI feedback for open-text answers.
9. Student views results.
```

Related endpoints:

```text
POST /auth/login
GET /me/pending-assessments
POST /assessments/{assessment_id}/attempts/start
GET /attempts/{attempt_id}/form
POST /attempts/{attempt_id}/answers
POST /attempts/{attempt_id}/submit
GET /attempts/{attempt_id}/results
```

---

# Request and Response Notes

## User identity

The authenticated user is always resolved from the JWT token.

The client should not send:

```text
student_id
teacher_id
```

when the backend can determine it from the authenticated user.

Exception:

An admin may provide `teacher_id` when creating a course.

---

## Soft delete

Delete endpoints usually perform soft delete.

Soft deleted resources are marked inactive or archived instead of being physically removed.

Examples:

```text
DELETE /users/{user_id}
DELETE /courses/{course_id}
DELETE /questions/{question_id}
```

---

## Static images

Question images are stored by the backend and exposed as static files.

The API returns image URLs in question or form payloads.

Example:

```json
{
  "image_url": "/static/images/example-question.png"
}
```

The frontend is responsible for rendering the image.

---

## Dynamic visibility

Dynamic visibility is handled by both frontend and backend.

The frontend uses visibility rules to render the form dynamically.

The backend validates visibility rules before final submission.

This prevents invalid manual submissions.

---

## Atomic submission

Attempt submission must be atomic.

The final submission should either:

- save answers, calculate grades, generate required feedback, and update attempt status successfully, or
- fail safely without corrupting stored data.

---

# Out of Scope for API MVP

The following API features are out of scope for the MVP:

- Public user registration.
- Question editing.
- Question versioning.
- Advanced upload management.
- PDF or video resources.
- Complex OR-based visibility rules.
- Multi-university endpoints.
- Academic term endpoints.
- Microservice boundaries.
- MCP endpoints.
- ADK endpoints.