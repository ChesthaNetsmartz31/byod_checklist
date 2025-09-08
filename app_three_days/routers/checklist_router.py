from fastapi import APIRouter
from datetime import date, timedelta
from services.checklist_service import generate_events_for_three_days
from schemas.checklist_schema import GenerateResponse

router = APIRouter()

@router.post("/generate-3days", response_model=GenerateResponse)
def generate_three_days():
    n = generate_events_for_three_days()
    today = date.today()
    days = [today + timedelta(days=i) for i in range(3)]
    return {"attempted_inserts": n, "dates": days}
