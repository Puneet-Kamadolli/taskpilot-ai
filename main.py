from fastapi import FastAPI

from app.database.database import Base
from app.database.database import engine

from app.routers.task_router import router as task_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskPilot AI",
              description="AI Powered personal Task tracker and remainder",
              version="1.0.0")

app.include_router(task_router)

@app.get("/")
def health_check():
    return {
        "status": "Running",
        "message": "TaskPilot AI is running"
    }