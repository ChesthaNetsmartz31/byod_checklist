from apscheduler.schedulers.background import BackgroundScheduler
import logging
from app_three_days.services.checklist_service import generate_events_for_three_days, mark_overdue_events

scheduler = BackgroundScheduler()

def populate_three_days_checklists():
    try:
        n = generate_events_for_three_days()
        logging.info(f"✅ Generated events for 3 days (attempted inserts): {n}")
    except Exception as e:
        logging.error(f"❌ populate_three_days_checklists failed: {e}")

def check_overdue_events():
    try:
        n = mark_overdue_events()
        logging.info(f"⚠️ Marked {n} events as overdue")
    except Exception as e:
        logging.error(f"❌ check_overdue_events failed: {e}")
