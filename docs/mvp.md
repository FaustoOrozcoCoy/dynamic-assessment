# Dynamic Assessment API — MVP

## Overview

Dynamic Assessment API is a backend platform designed to manage dynamic academic assessments within a university environment.

The platform allows administrators and teachers to manage users, courses, students, question banks, assessments, responses, grading, and AI-assisted feedback.

The primary goal of the MVP is to support reusable questions, dynamic forms, assessment workflows, and student progress tracking.

---

## Product Goal

Deliver a platform capable of:

- Managing users with multiple roles.
- Managing courses and enrollments.
- Providing a shared question bank.
- Creating assessments from reusable questions.
- Delivering dynamic forms to a frontend application.
- Supporting partial saves and resumable attempts.
- Automatically grading objective questions.
- Generating AI-assisted feedback for open-text answers.

---

## Actors

### Admin

Responsibilities:

- Manage users.
- Assign roles.
- Create courses and assign teachers.
- Access system-wide information.

### Teacher

Responsibilities:

- Create and manage courses.
- Enroll students.
- Create questions.
- Build assessments.
- Publish assessments.
- Review responses and results.

### Student

Responsibilities:

- View enrolled courses.
- View pending assessments.
- Start assessments.
- Save progress.
- Resume unfinished attempts.
- Submit answers.
- View grades and feedback.

---

## Scope

### User Management

Supported roles:

- admin
- teacher
- student

A user may have multiple roles.

Users are created by administrators or authorized teachers.

Self-registration is not supported.

---

### Courses

Features:

- Create courses.
- View courses.
- Manage courses.
- Deactivate courses.

Rules:

- Teachers may create courses assigned to themselves.
- Admins may create courses and assign a teacher.
- Teachers may only manage their own courses.

---

### Enrollments

Features:

- Enroll students into courses.
- View course enrollments.
- View student courses.
- Remove enrollments.

Rules:

- Only users with the student role may be enrolled.
- Duplicate enrollments are not allowed.

---

### Question Bank

Supported question types:

- single_choice
- multiple_choice
- open_text
- number
- boolean
- scale

Question attributes:

- statement
- type
- validation configuration
- answer options (if applicable)
- image

Rules:

- Questions are reusable.
- Questions are not editable in the MVP.
- Questions may be deactivated.
- Each question may contain a single image.

---

### Assessments

Supported assessment types:

- quiz
- workshop
- exam
- form

Features:

- Create assessments.
- Add questions.
- Configure ordering.
- Configure scoring.
- Configure required questions.
- Publish assessments.

Rules:

- Every assessment belongs to a course.
- Questions may be reused across assessments.
- Only enrolled students may access assessments.

---

### Dynamic Forms

The backend provides the structure required by the frontend to render an assessment.

Question payloads may include:

- question type
- statement
- image
- options
- validation rules
- ordering
- score
- required flag
- visibility rule

Rules:

- Each question may have a single visibility rule.
- The backend validates visibility constraints before accepting answers.

---

### Attempts and Responses

Supported attempt states:

- in_progress
- submitted
- graded

Features:

- Start an assessment.
- Save partial answers.
- Resume unfinished attempts.
- Submit final answers.
- View attempt results.

Rules:

- Students may save progress and continue later.
- Student identity is resolved from the authenticated session.
- Assessment submission must be atomic.

---

### Grading and Feedback

Automatic grading is supported for:

- single_choice
- multiple_choice
- boolean
- number
- scale

Open-text answers receive AI-assisted feedback.

Generated feedback is stored together with the student's response.

---

## Out of Scope

The following features are not included in the MVP:

- Multi-university support.
- Academic terms and semesters.
- Question editing and versioning.
- Advanced file uploads.
- PDF or video-based questions.
- Date, matrix, ranking, file upload, or calculated question types.
- Complex OR-based visibility rules.
- Advanced analytics dashboards.
- Microservices.
- MCP integration.
- ADK integration.
- Exam timers.
- Advanced question randomization.

---

## Main Workflow

1. Admin creates users and assigns roles.
2. Admin or teacher creates a course.
3. Teacher enrolls students.
4. Teacher creates reusable questions.
5. Teacher creates an assessment.
6. Teacher adds questions to the assessment.
7. Teacher configures scoring, ordering, and visibility rules.
8. Teacher publishes the assessment.
9. Student views pending assessments.
10. Student starts an assessment attempt.
11. Student saves progress.
12. Student resumes unfinished work if needed.
13. Student submits answers.
14. The system validates and stores responses.
15. The system grades objective questions.
16. The system generates AI-assisted feedback.
17. Student reviews results.
18. Teacher reviews assessment outcomes.

---

## Success Criteria

The MVP is considered complete when:

- Users may hold multiple roles.
- Courses and enrollments function correctly.
- Teachers can build assessments from reusable questions.
- Students can save and resume attempts.
- Dynamic visibility rules are enforced.
- Automatic grading works for objective questions.
- AI-assisted feedback works for open-text responses.
- Question images can be rendered by the frontend.
- Core workflows are fully testable.