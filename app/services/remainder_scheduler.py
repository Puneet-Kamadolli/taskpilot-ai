import logging

from datetime import datetime, timedelta

from app.database.database import SessionLocal
from app.models.task import Task

logger = logging.getLogger(__name__)

REMAINDER_WINDOW_MINUTES = 15

def check_due_tasks()-> None:

    print("DEBUG: check_due_tasks() executed")
    """Log one remainder for pending tasks due within 15 mins"""

    db = SessionLocal()

    try:

        now = datetime.now()
        remainder_window_end = now + timedelta(minutes=REMAINDER_WINDOW_MINUTES)

        print("DEBUG: DB session created. Inside try block now")

        logger.info(
            "Reminder check started | now=%s | window_end=%s",
            now,
            remainder_window_end,
        )

        upcoming_tasks = (
            db.query(Task)
            .filter(
                Task.due_date.isnot(None),
                Task.due_date >= now,
                Task.due_date <= remainder_window_end,
                Task.status == "Pending",
                Task.reminder_sent.is_(False)
            )
            .all()
        )

        logger.info(
            "Reminder check completed | matching_tasks=%s",
            len(upcoming_tasks),
        )

        for task in upcoming_tasks:
            logger.info(
                "UPCOMING TASK REMAINDERS | ID=%s | Title=%s |"
                "Deadline=%s",
                task.id,
                task.title,
                task.due_date,
            )
            task.reminder_sent = True

        if upcoming_tasks:
            db.commit()

    except Exception:
        db.rollback()
        logger.exception("Error while checking upcoming task remainders")

    finally:
        db.close()