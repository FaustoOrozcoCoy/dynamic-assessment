# Domain Model

## Overview

This document describes the main domain concepts, relationships, and business rules for Dynamic Assessment API.

The goal of the domain model is to define how the system works from a business perspective before designing the database schema, API endpoints, or application code.

---

## Main Actors

### Admin

A user with administrative permissions.

Main responsibilities:

- Manage users.
- Assign roles.
- Create courses and assign teachers.
- Access system-wide information.

### Teacher

A user responsible for managing courses, questions, assessments, and student results.

Main responsibilities:

- Create and manage assigned courses.
- Enroll students.
- Create reusable questions.
- Build and publish assessments.
- Review student attempts and results.

### Student

A user who participates in courses and completes assessments.

Main responsibilities:

- View enrolled courses.
- View pending assessments.
- Start assessment attempts.
- Save progress.
- Resume unfinished attempts.
- Submit answers.
- View grades and feedback.

---

## Main Entities

### User

Represents a person who can access the system.

A user may have one or more roles.

Examples:

- Admin user
- Teacher user
- Student user
- User with both teacher and student roles

Main responsibilities:

- Store authentication identity.
- Represent the person interacting with the system.
- Connect to roles, courses, enrollments, and attempts.

---

### Role

Represents a system-level permission category.

Initial roles:

- admin
- teacher
- student

A role can be assigned to multiple users.

---

### UserRole

Represents the relationship between users and roles.

This entity is required because a user may have more than one role.

Example:

A user may be both a teacher and a student.

---

### Course

Represents an academic course.

Examples:

- Automatic Control I
- Electric Circuits II
- Digital Systems

Main responsibilities:

- Group enrolled students.
- Group assessments.
- Belong to a responsible teacher.

Rules:

- A course must have one responsible teacher.
- A teacher may create courses assigned to themselves.
- An admin may create courses and assign them to a teacher.
- Courses may be deactivated using soft delete.

---

### Enrollment

Represents the enrollment of a student in a course.

This entity connects students and courses.

Rules:

- Only users with the student role may be enrolled.
- A student cannot be enrolled twice in the same course.
- A teacher may manage enrollments only for their own courses.
- An admin may manage enrollments globally.

---

### Question

Represents a reusable question from the shared question bank.

Supported question types:

- single_choice
- multiple_choice
- open_text
- number
- boolean
- scale

Main responsibilities:

- Store the question statement.
- Define the question type.
- Store validation configuration when required.
- Optionally reference one image.
- Be reused across multiple assessments.

Rules:

- Questions are shared across the system.
- Questions are reusable.
- Questions are not editable in the MVP.
- Questions may be deactivated using soft delete.
- Each question may contain at most one image.

---

### QuestionOption

Represents a possible answer option for a question.

This entity applies mainly to:

- single_choice
- multiple_choice
- boolean
- scale

Main responsibilities:

- Store option labels and values.
- Indicate whether an option is correct.
- Support exclusive options when needed.

Rules:

- A question may have multiple options.
- An option belongs to one question.
- Exclusive options cannot be combined with other options in the same answer.

---

### Assessment

Represents an evaluative activity associated with a course.

Supported assessment types:

- quiz
- workshop
- exam
- form

Main responsibilities:

- Group questions into an activity.
- Belong to a course.
- Be published before students can answer it.
- Receive student attempts.

Rules:

- Every assessment belongs to one course.
- Only students enrolled in the course may access the assessment.
- An assessment must be published before students can answer it.

---

### AssessmentQuestion

Represents the relationship between an assessment and a question.

This entity is necessary because:

- An assessment may contain many questions.
- A question may be reused in many assessments.

AssessmentQuestion also stores assessment-specific configuration.

Main responsibilities:

- Define question order within an assessment.
- Define question score.
- Define whether the question is required.
- Connect visibility rules to questions inside an assessment.

---

### VisibilityRule

Represents a dynamic visibility condition for a question inside an assessment.

Example:

Show question 5 only if question 2 was answered with "yes".

Main responsibilities:

- Define when a question should be visible.
- Connect one question's visibility to a previous answer.

Rules:

- In the MVP, each assessment question may have at most one visibility rule.
- The frontend may use visibility rules to show or hide questions.
- The backend must also validate visibility rules before accepting final answers.
- Required questions are only required when they are visible.
- Hidden questions should not block assessment submission.

---

### AssessmentAttempt

Represents a student's attempt to complete an assessment.

Supported states:

- in_progress
- submitted
- graded

Main responsibilities:

- Track the student's progress.
- Allow partial saves.
- Allow students to resume unfinished attempts.
- Store the final assessment result.

Rules:

- A student may start an attempt only for published assessments.
- A student may start an attempt only if enrolled in the course.
- If an attempt is in progress, the student may resume it.
- Once submitted, the attempt should not allow answer modifications.
- Final submission must validate all required rules before closing the attempt.

---

### QuestionAnswer

Represents a student's answer to a specific question within an assessment attempt.

Main responsibilities:

- Store the student's answer.
- Store the score obtained for the question.
- Store manual or automatic feedback when applicable.
- Connect the answer to its assessment attempt.

Rules:

- Answers may be saved partially while the attempt is in progress.
- Answers may be updated before final submission.
- Answers should not be modified after the attempt is submitted.
- Objective answers may be graded automatically.
- Open-text answers may receive AI-assisted feedback.

---

### AIFeedback

Represents feedback generated by an AI model for an open-text answer.

Main responsibilities:

- Store the generated feedback.
- Store the model used.
- Store the provider used.
- Store the raw response when needed.
- Track generation status.

Rules:

- AIFeedback is associated with a QuestionAnswer.
- Not every QuestionAnswer requires AIFeedback.
- AI feedback applies mainly to open_text questions.
- If AI feedback generation fails, the system must not corrupt the saved student answer.

---

## Entity Relationships

### Users and Roles

A user may have multiple roles.

A role may belong to multiple users.

Relationship:

User N --- N Role

Implemented conceptually through:

UserRole

---

### Teachers and Courses

A teacher may own multiple courses.

Each course has one responsible teacher.

Relationship:

User 1 --- N Course

---

### Students and Courses

A student may be enrolled in multiple courses.

A course may have multiple students.

Relationship:

User N --- N Course

Implemented conceptually through:

Enrollment

---

### Courses and Assessments

A course may have multiple assessments.

Each assessment belongs to one course.

Relationship:

Course 1 --- N Assessment

---

### Questions and Options

A question may have multiple answer options.

Each option belongs to one question.

Relationship:

Question 1 --- N QuestionOption

---

### Assessments and Questions

An assessment may contain multiple questions.

A question may be reused in multiple assessments.

Relationship:

Assessment N --- N Question

Implemented conceptually through:

AssessmentQuestion

---

### Assessment Questions and Visibility Rules

An assessment question may have one visibility rule.

A visibility rule belongs to one assessment question.

Relationship:

AssessmentQuestion 1 --- 0..1 VisibilityRule

---

### Assessments and Attempts

An assessment may have multiple student attempts.

Each attempt belongs to one assessment.

Relationship:

Assessment 1 --- N AssessmentAttempt

---

### Students and Attempts

A student may have multiple assessment attempts.

Each attempt belongs to one student.

Relationship:

User 1 --- N AssessmentAttempt

---

### Attempts and Answers

An assessment attempt may have multiple answers.

Each answer belongs to one attempt.

Relationship:

AssessmentAttempt 1 --- N QuestionAnswer

---

### Answers and AI Feedback

A question answer may have AI-generated feedback.

AI feedback belongs to one question answer.

Relationship:

QuestionAnswer 1 --- 0..1 AIFeedback

---

## Business Rules

### User Rules

- A user may have one or more roles.
- Only active users can authenticate.
- Users are created by authorized users.
- Self-registration is not supported in the MVP.

---

### Course Rules

- A course must have a responsible teacher.
- Teachers can create courses assigned to themselves.
- Admins can create courses and assign a teacher.
- Teachers can only manage their own courses.
- Courses are deactivated using soft delete.

---

### Enrollment Rules

- Only users with the student role can be enrolled.
- Duplicate enrollments are not allowed.
- Students can only access courses where they are enrolled.
- Teachers can only manage enrollments for their own courses.
- Admins can manage enrollments globally.

---

### Question Rules

- Questions belong to a shared question bank.
- Questions can be reused across assessments.
- Questions are not editable in the MVP.
- Questions can be deactivated using soft delete.
- Each question may contain at most one image.
- Each question must have one supported question type.

---

### Assessment Rules

- Every assessment belongs to one course.
- An assessment may contain multiple questions.
- Questions may be reused across assessments.
- An assessment must be published before students can answer it.
- Only enrolled students can answer assessments from a course.

---

### Dynamic Form Rules

- Each assessment question may have at most one visibility rule.
- The frontend may use visibility rules to render the form dynamically.
- The backend must validate visibility rules before accepting final answers.
- A required question is required only if it is visible.
- Hidden questions should not block final submission.

---

### Attempt Rules

- Students can start attempts only for published assessments.
- Students can save partial answers while the attempt is in progress.
- Students can resume unfinished attempts.
- Final submission validates all required answers and visibility rules.
- Submitted attempts should not allow answer modifications.
- Final submission must be handled as an atomic operation.

---

### Grading and Feedback Rules

- Objective questions can be graded automatically.
- Open-text questions can receive AI-assisted feedback.
- AI feedback must be stored separately from the student answer.
- AI failures must not corrupt saved answers.
- Students can view grades and feedback after grading.

---

## Conceptual Diagram

```mermaid
erDiagram
    USER ||--o{ USER_ROLE : has
    ROLE ||--o{ USER_ROLE : assigned_to

    USER ||--o{ COURSE : teaches
    USER ||--o{ ENROLLMENT : enrolls
    COURSE ||--o{ ENROLLMENT : contains

    COURSE ||--o{ ASSESSMENT : has

    QUESTION ||--o{ QUESTION_OPTION : has

    ASSESSMENT ||--o{ ASSESSMENT_QUESTION : includes
    QUESTION ||--o{ ASSESSMENT_QUESTION : reused_as

    ASSESSMENT_QUESTION ||--o| VISIBILITY_RULE : controls

    ASSESSMENT ||--o{ ASSESSMENT_ATTEMPT : receives
    USER ||--o{ ASSESSMENT_ATTEMPT : submits

    ASSESSMENT_ATTEMPT ||--o{ QUESTION_ANSWER : contains
    ASSESSMENT_QUESTION ||--o{ QUESTION_ANSWER : answered_as

    QUESTION_ANSWER ||--o| AI_FEEDBACK : receives