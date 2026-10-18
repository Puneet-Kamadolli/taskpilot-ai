import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app.database.database import Base
from app.database.database import engine
from app.services.remainder_scheduler import check_due_tasks

from app.routers.task_router import router as task_router

Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True
)
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        check_due_tasks,
        trigger="interval",
        minutes=1,
        id="upcoming_task_remainders",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    ) 

    scheduler.start()
    print("TaskPilot AI task remainder started.")
    print("TaskPilot AI reminder scheduler started.")
    print("Scheduler running:", scheduler.running)
    print("Registered jobs:", scheduler.get_jobs())

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        print("TaskPilot AI task remainder stopped")

app = FastAPI(title="TaskPilot AI",
              description="AI Powered personal Task tracker and remainder",
              version="1.0.0",
              lifespan=lifespan)

app.include_router(task_router)


@app.get("/")
def health_check():
    return {
        "status": "Running",
        "message": "TaskPilot AI is running"
    }

