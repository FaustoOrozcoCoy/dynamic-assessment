from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings


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


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Dynamic Assessment API is running",
        "environment": settings.app_env,
    }