from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.routers.chat import router as chat_router
from app.routers.roadmap import router as roadmap_router
from app.routers.dashboard import router as dashboard_router
from app.routers.courses import router as courses_router
from app.routers.recommend import router as recommend_router
from app.routers.skill import router as skill_router

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0",
    description="An AI-powered learning assistant."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(roadmap_router, prefix="/roadmap", tags=["Roadmap"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(courses_router, prefix="/courses", tags=["Courses"])
app.include_router(recommend_router, prefix="/recommend", tags=["Smart Recommendation"])
app.include_router(skill_router, prefix="/skill", tags=["Skill"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Learning Buddy API",
        "status": "Learning Buddy API is running.",
        "version": "1.0"
    }