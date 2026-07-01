from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import auth, courses, questions, roles, users, assessments, forms, attempts, results


app = FastAPI(
    title=settings.app_name,
    description="Backend API for dynamic academic assessments.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

app.mount(
    "/ui",
    StaticFiles(directory="frontend", html=True),
    name="frontend",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(courses.router)
app.include_router(questions.router)
app.include_router(assessments.router)
app.include_router(forms.router)
app.include_router(attempts.router)
app.include_router(results.router)



@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/")

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Dynamic Assessment API is running",
        "environment": settings.app_env,
    }