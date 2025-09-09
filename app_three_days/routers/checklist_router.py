from fastapi import APIRouter
from datetime import date, timedelta
from app_three_days.services.checklist_service import generate_events_for_three_days, mark_overdue_events
from app_three_days.schemas.checklist_schema import GenerateResponse

router = APIRouter()

@router.post("/generate-3days", response_model=GenerateResponse)
def generate_three_days():
    n = generate_events_for_three_days()
    today = date.today()
    days = [today + timedelta(days=i) for i in range(3)]
    return {"attempted_inserts": n, "dates": days}


@router.post("/mark-overdue")
def mark_overdue():
    count = mark_overdue_events()
    return {"updated": count}

