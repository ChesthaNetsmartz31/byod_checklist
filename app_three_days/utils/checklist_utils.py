import json
from datetime import datetime, date, time, timedelta
from typing import Any, Dict, List, Optional

# ---------- Constants ----------
DAY_NAME_TO_INDEX = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}

# ---------- Helpers ----------
def _parse_time_str(s: str) -> Optional[time]:
    """Convert 'HH:MM[:SS]' string into datetime.time object"""
    if not s:
        return None
    try:
        parts = [int(p) for p in str(s).split(":")]
        if len(parts) == 2:
            return time(parts[0], parts[1])
        if len(parts) >= 3:
            return time(parts[0], parts[1], parts[2])
    except Exception:
        return None
    return None

def _ensure_json(v: Any) -> Any:
    """Ensure input is loaded JSON if it's a string"""
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        return v
    try:
        return json.loads(v)
    except Exception:
        return None

def _week_of_month(dt: date) -> int:
    """Return week index of given date inside month"""
    first_day = dt.replace(day=1)
    return (dt.day + first_day.weekday()) // 7 + 1

def _is_last_week_of_month(dt: date) -> bool:
    """Check if the date is in the last week of its month"""
    next_week = dt + timedelta(days=7)
    return next_week.month != dt.month

# ---------- Schedule Parsing ----------
def _today_times_for_daily(srow: Dict[str, Any]) -> List[Optional[time]]:
    daily_times = _ensure_json(srow.get("daily_times"))
    times: List[Optional[time]] = []
    if isinstance(daily_times, list):
        for t in daily_times:
            pt = _parse_time_str(str(t))
            if pt:
                times.append(pt)
    if not times:
        once_time = srow.get("once_time")
        if once_time:
            pt = _parse_time_str(str(once_time))
            if pt:
                times.append(pt)
    return times or [None]

def _today_times_for_weekly(srow: Dict[str, Any], today: date) -> List[Optional[time]]:
    weekly_times = _ensure_json(srow.get("weekly_times")) or {}
    weekday_times = _ensure_json(srow.get("weekday_times")) or []
    dow = today.weekday()
    times: List[Optional[time]] = []

    if isinstance(weekly_times, dict):
        for k, v in weekly_times.items():
            k_idx = DAY_NAME_TO_INDEX.get(str(k).strip().lower())
            if k_idx == dow:
                if isinstance(v, list):
                    for t in v:
                        pt = _parse_time_str(str(t))
                        if pt:
                            times.append(pt)
                else:
                    pt = _parse_time_str(str(v))
                    if pt:
                        times.append(pt)
        if times:
            return times

    if dow < 5 and isinstance(weekday_times, list):
        for t in weekday_times:
            pt = _parse_time_str(str(t))
            if pt:
                times.append(pt)
        if times:
            return times

    return _today_times_for_daily(srow)

def _today_times_for_weekday(srow: Dict[str, Any], today: date) -> List[Optional[time]]:
    if today.weekday() < 5:
        wdt = _ensure_json(srow.get("weekday_times"))
        times: List[Optional[time]] = []
        if isinstance(wdt, list):
            for t in wdt:
                pt = _parse_time_str(str(t))
                if pt:
                    times.append(pt)
        if times:
            return times
        return _today_times_for_daily(srow)
    return []

def _today_times_for_monthly(srow: Dict[str, Any], today: date) -> List[Optional[time]]:
    # Specific dates
    specific_dates = _ensure_json(srow.get("monthly_schedule_specific_dates")) or []
    for item in specific_dates:
        if not isinstance(item, dict):
            continue
        day_str = str(item.get("date"))
        if day_str.isdigit() and int(day_str) == today.day:
            times = _ensure_json(item.get("times")) or []
            return [_parse_time_str(str(t)) for t in times if _parse_time_str(str(t))]

    # Recurring days (like every 2nd Monday)
    recurring_days = _ensure_json(srow.get("monthly_schedule_recurring_days")) or []
    dow = today.weekday()
    for item in recurring_days:
        if not isinstance(item, dict):
            continue
        day_idx = DAY_NAME_TO_INDEX.get(str(item.get("day")).strip().lower())
        if day_idx == dow:
            times = _ensure_json(item.get("times")) or []
            return [_parse_time_str(str(t)) for t in times if _parse_time_str(str(t))]

    return []

def _today_times_for_yearly(srow: Dict[str, Any], today: date) -> List[Optional[time]]:
    ad = srow.get("annual_date")
    if isinstance(ad, str):
        try:
            ad = datetime.strptime(ad, "%Y-%m-%d").date()
        except Exception:
            ad = None
    if isinstance(ad, date) and ad.month == today.month and ad.day == today.day:
        at = srow.get("annual_time")
        if isinstance(at, str):
            return [_parse_time_str(at)]
        return _today_times_for_daily(srow)
    return []

def _today_times_for_once(srow: Dict[str, Any], today: date) -> List[Optional[time]]:
    od = srow.get("once_date")
    if isinstance(od, str):
        try:
            od = datetime.strptime(od, "%Y-%m-%d").date()
        except Exception:
            od = None
    if isinstance(od, date) and od == today:
        ot = srow.get("once_time")
        if isinstance(ot, str):
            return [_parse_time_str(ot)]
        return _today_times_for_daily(srow)
    return []

def _times_for_schedule_today(freq_label: str, srow: Dict[str, Any], today: date) -> List[Optional[time]]:
    f = (freq_label or "").strip().lower()
    if f == "daily":
        return _today_times_for_daily(srow)
    if f == "weekly":
        return _today_times_for_weekly(srow, today)
    if f == "weekday":
        return _today_times_for_weekday(srow, today)
    if f == "monthly":
        return _today_times_for_monthly(srow, today)
    if f == "yearly":
        return _today_times_for_yearly(srow, today)
    if f == "once":
        return _today_times_for_once(srow, today)
    return []
