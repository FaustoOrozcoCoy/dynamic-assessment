# Dynamic Assessment API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![OpenRouter](https://img.shields.io/badge/AI_Feedback-OpenRouter-blue?style=for-the-badge)

A backend platform designed to manage dynamic academic assessments within a university environment. 

This API allows administrators and teachers to manage users, courses, question banks, dynamic assessments, responses, automatic grading, and AI-assisted feedback.

## 🚀 Features

- **Role-Based Access Control (RBAC):** Users can hold multiple roles (`admin`, `teacher`, `student`) with specific permissions.
- **Shared Question Bank:** Reusable questions with various types (`single_choice`, `multiple_choice`, `open_text`, `boolean`, etc.).
- **Dynamic Assessments:** Rule-based visibility mapping (e.g., show Question 2 only if Question 1 answer is "Yes"). Validated atomically in the backend.
- **Stateful Attempts:** Students can start, save progress (`in_progress`), and submit assessments.
- **Automatic Grading & AI Feedback:** Objective questions are graded instantly. Open-text responses are evaluated using LLMs via OpenRouter, providing constructive feedback asynchronously.
- **Modular Monolith Architecture:** Clean separation of concerns using Routers, Services, Repositories, and Models.

## 🛠️ Tech Stack

- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 16
- **ORM & Migrations:** SQLAlchemy 2.0 & Alembic
- **Validation:** Pydantic
- **Authentication:** JWT (JSON Web Tokens) with bcrypt hashing
- **AI Integration:** httpx & OpenRouter API (gpt-4o-mini)
- **Containerization:** Docker & Docker Compose
- **API Testing:** Bruno

## 📂 Project Structure

```text
dynamic-assessment-api/
├── alembic/                # Database migrations
├── app/
│   ├── core/               # Settings, security, dependencies
│   ├── integrations/       # External services (LLM client)
│   ├── models/             # SQLAlchemy ORM models
│   ├── repositories/       # Database access layer
│   ├── routers/            # FastAPI HTTP endpoints
│   ├── schemas/            # Pydantic validation models
│   ├── services/           # Business logic and transaction management
│   └── main.py             # Application entry point
├── bruno/                  # API test collections
├── docs/                   # System design documentation
├── scripts/                # Utility scripts (seeders)
└── docker-compose.yml      # Local database environment
```

## ⚙️ Local Setup & Installation

### 1. Prerequisites
- Python 3.11 or higher
- Docker & Docker Compose
- Git

### 2. Clone and Configure Environment
Clone the repository and set up your virtual environment:
```bash
git clone <repository-url>
cd dynamic-assessment-api
python -m venv .venv
```

Activate the virtual environment:
- **Windows:** `.\.venv\Scripts\Activate.ps1` (or `.bat`)
- **macOS/Linux:** `source .venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy the example environment file and update the variables:
```bash
cp .env.example .env
```
Make sure to add your actual `OPENROUTER_API_KEY` in the `.env` file to enable AI grading.

### 4. Start Database & Run Migrations
Start the local PostgreSQL container:
```bash
docker compose up -d
```
Apply the database schema using Alembic:
```bash
alembic upgrade head
```

### 5. Seed the Database (Demo Data)
Populate the database with initial roles, users, a course, a question bank, a published assessment, and dynamic visibility rules:
```bash
python -m scripts.seed_demo
```
*Note: This will create an `admin`, a `teacher`, and a `student` (default password: `password123`).*

### 6. Run the Application
Start the FastAPI development server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`

## 🧪 Testing the API

This project uses **[Bruno](https://www.usebruno.com/)** for API testing instead of Postman.

1. Download and install Bruno.
2. Click **Open Collection** and select the `bruno/` folder in this repository.
3. Select the `Local` environment in the top right corner.
4. Execute the `Login` requests. Bruno will automatically capture the JWT token and inject it into subsequent requests using collection variables.

## 📖 Documentation

Detailed architectural decisions, domain models, and API contracts can be found in the `docs/` directory:
- `api-design.md`
- `architecture.md`
- `database-design.md`
- `domain.md`
- `mvp.md`