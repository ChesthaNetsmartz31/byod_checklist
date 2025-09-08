from fastapi import FastAPI
from app_today.routers import checklist_router
from app_today.core.scheduler import scheduler, populate_daily_checklists
import logging

app = FastAPI(root_path="/checklist")

# Routers
app.include_router(checklist_router.router, prefix="", tags=["Checklist"])

# Startup & Shutdown
@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(populate_daily_checklists, "interval", minutes=720)
    scheduler.start()
    logging.info("⏰ Scheduler started (interval=720m)")

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()
    logging.info("🛑 Scheduler stopped")

@app.get("/")
def home():
    return {"msg": "FastAPI + APScheduler running; see checklist.log for job output"}
