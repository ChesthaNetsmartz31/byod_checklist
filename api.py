from fastapi import FastAPI
from src.utils.cron import ChecklistEventScheduler
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config.config import settings
from src.logger.logger_config import setup_logger

# Configure logging
logger = setup_logger()

app = FastAPI()

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

@app.post("/run-cron")
async def run_cron():
    try:
        tables = reflect_tables()
        async_engine = create_async_engine(settings.async_database_url, echo=False)
        async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as db_session:
            scheduler = ChecklistEventScheduler(db_session, tables)
            await scheduler.run()
        await async_engine.dispose()
        return {"status": "Cron job executed"}
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return {"status": "Error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)