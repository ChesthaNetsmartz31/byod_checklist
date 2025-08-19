import logging
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config.config import settings
from src.utils.cron import ChecklistEventScheduler
from src.logger.logger_config import setup_logger
import asyncio
from datetime import datetime
import pytz

logger = setup_logger()

def reflect_tables():
    sync_engine = create_engine(settings.sync_database_url, echo=False)
    metadata = MetaData()
    table_names = [
        "checklist_schedule",
        "checklist_frequency",
        "checklist_schedule_event",
        "checklist_schedule_date",
        "checklist_template"
    ]
    tables = {}
    for table_name in table_names:
        try:
            tables[table_name] = Table(table_name, metadata, autoload_with=sync_engine)
            logger.info(f"Successfully reflected table: {table_name}")
        except Exception as e:
            logger.error(f"Error reflecting table {table_name}: {str(e)}")
            raise
    sync_engine.dispose()
    return tables

async def main():
    try:
        tables = reflect_tables()
    except Exception as e:
        logger.error(f"Failed to reflect tables: {str(e)}")
        return

    async_engine = create_async_engine(settings.async_database_url, echo=False)
    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db_session:
        scheduler = ChecklistEventScheduler(db_session, tables)
        logger.info(f"Initializing scheduler at {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')} IST")
        scheduler.start()
        logger.info(f"Scheduler running: {scheduler.scheduler.running}")

        try:
            loop = asyncio.get_event_loop()
            logger.info(f"Starting event loop at {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')} IST")
            await asyncio.Future()  
        except (KeyboardInterrupt, SystemExit):
            scheduler.scheduler.shutdown()
            logger.info("Scheduler shut down")
        finally:
            await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())