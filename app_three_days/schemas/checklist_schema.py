from pydantic import BaseModel
from typing import List
from datetime import date

class GenerateResponse(BaseModel):
    attempted_inserts: int
    dates: List[date]
