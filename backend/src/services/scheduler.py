import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.src.core.database import SessionLocal
from backend.src.services.import_service import import_history

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _scheduled_collect():
    db = SessionLocal()
    try:
        logger.info("定时采集任务启动")
        import_history(db, months=1)
    except Exception as e:
        logger.error(f"定时采集任务失败: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        _scheduled_collect,
        CronTrigger(day="10-15", hour=9, minute=0),
        id="monthly_collect",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler 已启动")


def stop_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler 已停止")