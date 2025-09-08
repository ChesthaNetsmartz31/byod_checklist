from pydantic import BaseModel
from typing import Optional
from datetime import date

class GenerateTodayResponse(BaseModel):
    attempted_inserts: int
    date: date

class ChecklistSchedule(BaseModel):
    id: int
    workplace: int
    checklist_template: int
    checklist_frequency: int
    status: bool
    daily_times: Optional[str] = None
    weekly_times: Optional[str] = None
    weekday_times: Optional[str] = None
    monthly_schedule_specific_dates: Optional[str] = None
    monthly_schedule_recurring_days: Optional[str] = None
    annual_date: Optional[str] = None
    annual_time: Optional[str] = None
    once_date: Optional[str] = None
    once_time: Optional[str] = None
