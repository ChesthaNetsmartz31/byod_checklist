import logging
from datetime import datetime, date, time
from sqlalchemy import select, Table
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.schedulers.frequencies import DailyScheduler, WeeklyScheduler, WeekdayScheduler, QuarterlyScheduler, MonthlyScheduler, AdhocScheduler, AnnuallyScheduler, OnceScheduler
import pytz
from src.logger.logger_config import setup_logger

logger = setup_logger()

class ChecklistEventScheduler:
    def __init__(self, db_session: AsyncSession, tables: dict):
        self.db_session = db_session
        self.tables = tables
        self.scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
        self.frequency_schedulers = {
            "daily": DailyScheduler(),
            "weekly": WeeklyScheduler(),
            "weekday": WeekdayScheduler(),
            "quarterly": QuarterlyScheduler(),
            "monthly": MonthlyScheduler(),
            "adhoc": AdhocScheduler(),
            "annually": AnnuallyScheduler(),
            "once": OnceScheduler()
        }
        self.cron_hour = 5  # 6:00 PM for testing
        self.cron_minute = 0  # Adjusted to 6:30 PM for next test

    def start(self):
        # Schedule the job to run daily at configured time
        self.scheduler.add_job(self.run, "cron", hour=self.cron_hour, minute=self.cron_minute, misfire_grace_time=300)
        self.scheduler.start()  # Start the scheduler
        logger.info(f"Scheduler started, runs daily at {self.cron_hour:02d}:{self.cron_minute:02d} IST, state: {self.scheduler.running}", extra={"unique_id": id(self)})
        logger.info(f"Scheduled jobs: {self.scheduler.get_jobs()}")

    async def run(self):
        try:
            ist = pytz.timezone("Asia/Kolkata")
            today = datetime.now(ist).date()
            start_time = time(self.cron_hour, self.cron_minute)
            now_naive = datetime.now(ist).replace(tzinfo=None)

            logger.info(f"Executing run method at {datetime.now(ist).strftime('%H:%M:%S')} for instance {id(self)}")
            result = await self.db_session.execute(
                select(
                    self.tables["checklist_schedule"].c.id,
                    self.tables["checklist_schedule"].c.workplace,
                    self.tables["checklist_schedule"].c.checklist_template,
                    self.tables["checklist_schedule"].c.daily_time,
                    self.tables["checklist_schedule"].c.weekly_day,
                    self.tables["checklist_schedule"].c.weekly_time,
                    self.tables["checklist_schedule"].c.monthly_schedule_type,
                    self.tables["checklist_schedule"].c.monthly_day,
                    self.tables["checklist_schedule"].c.monthly_time,
                    self.tables["checklist_schedule"].c.monthly_week_of_month,
                    self.tables["checklist_schedule"].c.monthly_weekday,
                    self.tables["checklist_schedule"].c.weekday_time,
                    self.tables["checklist_frequency"].c.label,
                    self.tables["checklist_schedule"].c.annually_date,
                    self.tables["checklist_schedule"].c.annually_time,
                    self.tables["checklist_schedule"].c.once_date,
                    self.tables["checklist_schedule"].c.once_time
                ).select_from(
                    self.tables["checklist_schedule"].join(
                        self.tables["checklist_frequency"],
                        self.tables["checklist_schedule"].c.checklist_frequency == self.tables["checklist_frequency"].c.id
                    )
                ).where(
                    self.tables["checklist_schedule"].c.status == True,
                    self.tables["checklist_frequency"].c.active == True
                )
            )
            schedules = result.fetchall()

            events_to_create = []
            events_to_update = []

            for schedule in schedules:
                try:
                    result = await self.db_session.execute(
                        select(self.tables["checklist_template"].c.signoff_required).where(
                            self.tables["checklist_template"].c.id == schedule.checklist_template
                        )
                    )
                    template = result.fetchone()
                    if not template:
                        logger.warning(f"No valid template for schedule ID {schedule.id}")
                        continue

                    frequency_label = schedule.label.lower().replace(" ", "")
                    scheduler = self.frequency_schedulers.get(frequency_label)
                    if not scheduler:
                        logger.error(f"Unknown frequency: {frequency_label} for schedule ID {schedule.id}")
                        continue

                    expected_events = await scheduler.generate_events(
                        schedule._asdict(),
                        today,
                        start_time,
                        self.db_session,
                        self.tables
                    )

                    result = await self.db_session.execute(
                        select(
                            self.tables["checklist_schedule_event"].c.id,
                            self.tables["checklist_schedule_event"].c.scheduled_date,
                            self.tables["checklist_schedule_event"].c.scheduled_time,
                            self.tables["checklist_schedule_event"].c.signoff_required,
                            self.tables["checklist_schedule_event"].c.checklist_template
                        ).where(
                            self.tables["checklist_schedule_event"].c.checklist_schedule == schedule.id,
                            self.tables["checklist_schedule_event"].c.scheduled_date == today
                        )
                    )
                    existing_events = result.fetchall()
                    existing_event_pairs = {(e.scheduled_date, e.scheduled_time) for e in existing_events}

                    for event_date, event_time in expected_events:
                        if (event_date, event_time) not in existing_event_pairs:
                            event = {
                                "workplace": schedule.workplace,
                                "checklist_schedule": schedule.id,
                                "checklist_template": schedule.checklist_template,
                                "scheduled_date": event_date,
                                "scheduled_time": event_time,
                                "status": "pending",
                                "signoff_required": template.signoff_required,
                                "created_at": now_naive,
                                "updated_at": now_naive
                            }
                            events_to_create.append(event)
                            logger.info(f"[{schedule.label}] Queued event creation for schedule ID {schedule.id} on {event_date} at {event_time}")
                        else:
                            for existing_event in existing_events:
                                if existing_event.scheduled_date == event_date and existing_event.scheduled_time == event_time:
                                    if (
                                        existing_event.scheduled_time != event_time or
                                        existing_event.signoff_required != template.signoff_required or
                                        existing_event.checklist_template != schedule.checklist_template
                                    ):
                                        if (event_date, event_time) not in {(e["scheduled_date"], e["scheduled_time"]) for e in events_to_update}:
                                            event = {
                                                "id": existing_event.id,
                                                "scheduled_time": event_time,
                                                "signoff_required": template.signoff_required,
                                                "checklist_template": schedule.checklist_template,
                                                "updated_at": now_naive
                                            }
                                            events_to_update.append(event)
                                            logger.info(f"[{schedule.label}] Queued event update for schedule ID {schedule.id} on {event_date} to time {event_time}")

                except Exception as e:
                    logger.error(f"Error processing schedule ID {schedule.id} (frequency: {schedule.label}): {str(e)}")
                    continue

            if events_to_create:
                await self.db_session.execute(
                    self.tables["checklist_schedule_event"].insert(),
                    events_to_create
                )
                logger.info(f"Created {len(events_to_create)} new events")

            if events_to_update:
                for event in events_to_update:
                    await self.db_session.execute(
                        self.tables["checklist_schedule_event"].update()
                        .where(self.tables["checklist_schedule_event"].c.id == event["id"])
                        .values(
                            scheduled_time=event["scheduled_time"],
                            signoff_required=event["signoff_required"],
                            checklist_template=event["checklist_template"],
                            updated_at=event["updated_at"]
                        )
                    )
                logger.info(f"Updated {len(events_to_update)} existing events")

            await self.db_session.commit()
            logger.info("Event creation and updates completed")

        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error during event creation/update: {str(e)}")
        finally:
            await self.db_session.close()