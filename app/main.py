from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import auth, courses, roles, users


app = FastAPI(
    title=settings.app_name,
    description="Backend API for dynamic academic assessments.",
    version="0.1.0",
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(courses.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Dynamic Assessment API is running",
        "environment": settings.app_env,
    }