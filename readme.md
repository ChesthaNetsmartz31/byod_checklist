Cron Job Scheduler Application
This is a Python-based application designed to manage and schedule recurring checklist events using an asynchronous scheduler. It utilizes a PostgreSQL database to store schedule data and leverages the APScheduler library for task scheduling.
Features

Flexible Scheduling: Supports daily, weekly, weekday, quarterly(Not confirmed yet), monthly, ad-hoc, annually, and one-time event schedules.
Database Integration: Reflects and manages tables from a PostgreSQL database for schedules and events.
Logging: Provides detailed logging to track scheduler activities and errors.
API Support: Includes an optional API endpoint to trigger jobs manually.
Async Support: Built with asyncio for non-blocking operations.

Prerequisites

Python 3.8 or higher
PostgreSQL database
Required Python packages:
fastapi
uvicorn
sqlalchemy
sqlalchemy[asyncio]
apscheduler
pytz
psycopg2-binary (or your preferred PostgreSQL driver)



Installation

Clone the repository:
git clone <repository-url>
cd cron


Create a virtual environment and activate it:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt


Configure the database settings:

Create a config.py file with your database URLs:settings = {
    "sync_database_url": "postgresql://user:password@localhost:5432/cron_db",
    "async_database_url": "postgresql+asyncpg://user:password@localhost:5432/cron_db"
}


Update user, password, and cron_db with your PostgreSQL credentials and database name.


Set up the database:

Create the database and tables manually or use a migration tool.
Required tables: checklist_schedule, checklist_frequency, checklist_schedule_event, checklist_schedule_date, checklist_template.



Usage
Running the Scheduler

Start the application:
python main.py


The scheduler will run daily at the configured time and process events based on the schedule data.


Check logs in the logs/ directory for execution details.



This schedules the run method to execute 1 minute after the API call.


Configuration

Cron Time: Adjust cron_hour and cron_minute in cron.py to set the daily run time.
Misfire Grace Time: Modify misfire_grace_time in add_job calls to handle delayed starts (default 300 seconds).
Database Tables: Ensure the schema includes all required columns (e.g., annually_date, once_date).



checklist_frequency values: 7 (Annually), 8 (Once), etc.

Logging

Logs are stored in the logs/ directory with daily rotation.
Use logger_config.py to customize logging levels or handlers.

Troubleshooting

Scheduler Not Running: Ensure self.scheduler.start() is called in cron.py and the event loop is active in main.py.
No Events Created: Verify schedule data matches the current date and time (e.g., today is 2025-08-13).
API Issues: Check server logs and ensure the database connection is active.
