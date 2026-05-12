import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from sqlmodel import Session

from backend.core.database import engine
from backend.services.import_service import refresh_origin_data, refresh_sales_data

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _scheduled_collect():
    with Session(engine) as db:
        try:
            logger.info("定时采集任务启动")
            refresh_sales_data(db)
            refresh_origin_data(db)
        except Exception as e:
            logger.error(f"定时采集任务失败: {e}")


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