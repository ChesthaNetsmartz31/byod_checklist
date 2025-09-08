from apscheduler.schedulers.background import BackgroundScheduler
import logging
from app_today.services.checklist_service import generate_today_events

scheduler = BackgroundScheduler()

def populate_daily_checklists():
    try:
        n = generate_today_events()
        logging.info(f"✅ Generated events (attempted inserts): {n}")
    except Exception as e:
        logging.error(f"❌ populate_daily_checklists failed: {e}")
