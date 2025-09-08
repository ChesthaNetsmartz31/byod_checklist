from fastapi import APIRouter
from datetime import date
from app_today.services.checklist_service import generate_today_events
from app_today.schemas.checklist_schema import GenerateTodayResponse

router = APIRouter()

@router.post("/generate-today", response_model=GenerateTodayResponse)
def generate_today():
    n = generate_today_events()
    return {"attempted_inserts": n, "date": str(date.today())}
