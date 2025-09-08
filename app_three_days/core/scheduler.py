from apscheduler.schedulers.background import BackgroundScheduler
import logging
from services.checklist_service import generate_events_for_three_days

scheduler = BackgroundScheduler()

def populate_three_days_checklists():
    try:
        n = generate_events_for_three_days()
        logging.info(f"✅ Generated events for 3 days (attempted inserts): {n}")
    except Exception as e:
        logging.error(f"❌ populate_three_days_checklists failed: {e}")
