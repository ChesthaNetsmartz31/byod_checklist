from fastapi import FastAPI
from app_three_days.routers import checklist_router
from app_three_days.core.scheduler import scheduler, populate_three_days_checklists, check_overdue_events
import logging

app = FastAPI(root_path="/checklist")

# Routers
app.include_router(checklist_router.router, prefix="", tags=["Checklist"])

# Startup & Shutdown
@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(populate_three_days_checklists, "interval", minutes=720)  # every 12h
    scheduler.add_job(check_overdue_events, "interval", minutes=60)  # every 1h
    scheduler.start()
    logging.info("⏰ Scheduler started (checklists=720m, overdue=60m)")

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()
    logging.info("🛑 Scheduler stopped")

@app.get("/")
def home():
    return {"msg": "FastAPI + APScheduler running for 3 days; see checklist.log for job output"}
