import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database.database import Base, engine
from app.services.remainder_scheduler import check_due_tasks
from app.routers.task_router import router as task_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True
)

Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        check_due_tasks,
        trigger="interval",
        minutes=5,
        id="upcoming_task_remainders",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    ) 

    scheduler.start()
    logger.info("TaskPilot AI reminder scheduler started.")
    logger.info("Scheduler running: %s ", scheduler.running)
    logger.info("Registered jobs: %s ", scheduler.get_jobs())

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        logger.info("TaskPilot AI task remainder stopped")

app = FastAPI(title="TaskPilot AI",
              description="AI Powered personal Task tracker and remainder",
              version="1.0.0",
              lifespan=lifespan)

@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.error(
        "An unhandled exception during %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc),exc,exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail":"An unhandled server error occurred."
        },
    )

app.include_router(task_router)

@app.get("/")
def health_check():
    return {
        "status": "Running",
        "message": "TaskPilot AI is running"
    }

