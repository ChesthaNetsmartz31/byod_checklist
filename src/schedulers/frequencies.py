import logging
from abc import ABC, abstractmethod
from datetime import date, time, datetime
from typing import List, Tuple
from sqlalchemy import select, Table
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil import rrule
from dateutil.rrule import DAILY, WEEKLY, MONTHLY
import pytz

logger = logging.getLogger(__name__)

class FrequencyScheduler(ABC):
    @abstractmethod
    async def generate_events(
        self,
        schedule: dict,
        today: date,
        start_time: time,
        db_session: AsyncSession,
        tables: dict
    ) -> List[Tuple[date, time]]:
        """
        Generate a list of (date, time) tuples for events happening today after start_time.
        """
        pass

class DailyScheduler(FrequencyScheduler):
    async def generate_events(self, schedule: dict, today: date, start_time: time, db_session: AsyncSession, tables: dict) -> List[Tuple[date, time]]:
        if not schedule.get("daily_time"):
            logger.warning(f"No daily_time specified for schedule ID {schedule['id']}")
            return []
        if schedule["daily_time"] >= start_time:
            return [(today, schedule["daily_time"])]
        return []

class WeeklyScheduler(FrequencyScheduler):
    async def generate_events(self, schedule: dict, today: date, start_time: time, db_session: AsyncSession, tables: dict) -> List[Tuple[date, time]]:
        if not schedule.get("weekly_day") or not schedule.get("weekly_time"):
            logger.warning(f"Missing weekly_day or weekly_time for schedule ID {schedule['id']}")
            return []
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        # Adjust for Sunday=0 convention
        schedule_weekday = (now.weekday() + 1) % 7
        if schedule_weekday == schedule["weekly_day"] and schedule["weekly_time"] >= start_time:
            return [(today, schedule["weekly_time"])]
        return []

class WeekdayScheduler(FrequencyScheduler):
    async def generate_events(self, schedule: dict, today: date, start_time: time, db_session: AsyncSession, tables: dict) -> List[Tuple[date, time]]:
        if not schedule.get("weekday_time"):
            logger.warning(f"No weekday_time specified for schedule ID {schedule['id']}")
            return []
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        if now.weekday() < 5 and schedule["weekday_time"] >= start_time:
            return [(today, schedule["weekday_time"])]
        return []

class QuarterlyScheduler(FrequencyScheduler):
    async def generate_events(self, schedule: dict, today: date, start_time: time, db_session: AsyncSession, tables: dict) -> List[Tuple[date, time]]:
        if not schedule.get("monthly_time"):
            logger.warning(f"No monthly_time specified for schedule ID {schedule['id']}")
            return []
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        quarterly_months = {1, 5, 9}
        if now.month in quarterly_months and now.day == 1 and schedule["monthly_time"] >= start_time:
            return [(today, schedule["monthly_time"])]
        return []

class MonthlyScheduler(FrequencyScheduler):
    async def generate_events(self, schedule: dict, today: date, start_time: time, db_session: AsyncSession, tables: dict) -> List[Tuple[date, time]]:
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        # Adjust for Sunday=0 convention
        schedule_weekday = (now.weekday() + 1) % 7
        events = []
        if schedule.get("monthly_schedule_type") == "specific_day" and schedule.get("monthly_day") and schedule.get("monthly_time"):
            if now.day == schedule["monthly_day"] and schedule["monthly_time"] >= start_time:
                events.append((today, schedule["monthly_time"]))
        elif schedule.get("monthly_schedule_type") == "week_based" and schedule.get("monthly_week_of_month") and schedule.get("monthly_weekday") and schedule.get("weekday_time"):
            week_of_month = (now.day - 1) // 7 + 1
            if week_of_month == schedule["monthly_week_of_month"] and schedule_weekday == schedule["monthly_weekday"] and schedule["weekday_time"] >= start_time:
                events.append((today, schedule["weekday_time"]))
        else:
            logger.warning(f"Invalid monthly schedule configuration for schedule ID {schedule['id']}")
        return events

class AdhocScheduler(FrequencyScheduler):
    async def generate_events(self, schedule: dict, today: date, start_time: time, db_session: AsyncSession, tables: dict) -> List[Tuple[date, time]]:
        result = await db_session.execute(
            select(tables["checklist_schedule_date"]).where(
                tables["checklist_schedule_date"].c.checklist_schedule == schedule["id"],
                tables["checklist_schedule_date"].c.scheduled_date == today,
                tables["checklist_schedule_date"].c.scheduled_time >= start_time
            )
        )
        adhoc_dates = result.fetchall()
        unique_events = {(d.scheduled_date, d.scheduled_time) for d in adhoc_dates}
        return list(unique_events)

class AnnuallyScheduler(FrequencyScheduler):
    async def generate_events(self, schedule: dict, today: date, start_time: time, db_session: AsyncSession, tables: dict) -> List[Tuple[date, time]]:
        if not schedule.get("annually_date") or not schedule.get("annually_time"):
            logger.warning(f"No annually_date or annually_time specified for schedule ID {schedule['id']}")
            return []
        annually_month = schedule["annually_date"].month
        annually_day = schedule["annually_date"].day
        annually_time = schedule["annually_time"]
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        if now.month == annually_month and now.day == annually_day and annually_time >= start_time:
            return [(today, annually_time)]
        return []

class OnceScheduler(FrequencyScheduler):
    async def generate_events(self, schedule: dict, today: date, start_time: time, db_session: AsyncSession, tables: dict) -> List[Tuple[date, time]]:
        if not schedule.get("once_date") or not schedule.get("once_time"):
            logger.warning(f"No once_date or once_time specified for schedule ID {schedule['id']}")
            return []
        once_date = schedule["once_date"]
        once_time = schedule["once_time"]
        if once_date == today and once_time >= start_time:
            return [(today, once_time)]
        return []