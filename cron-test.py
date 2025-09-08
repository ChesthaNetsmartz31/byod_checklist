# from fastapi import FastAPI
# from apscheduler.schedulers.background import BackgroundScheduler
# import psycopg2
# from datetime import datetime
#
# app = FastAPI()
#
# def populate_daily_checklists():
#     conn = psycopg2.connect(
#         dbname="checklistdb",
#         user="postgres",
#         password="postgres",
#         host="localhost",
#         port=5432
#     )
#     cur = conn.cursor()
#
#     insert_query = """
#         INSERT INTO checklist_schedule_event (
#             workplace,
#             checklist_schedule,
#             checklist_template,
#             scheduled_date,
#             scheduled_time,
#             status,
#             signoff_required,
#             approved,
#             created_at
#         )
#         SELECT
#             s.workplace,
#             s.id AS checklist_schedule,
#             s.checklist_template,
#             CURRENT_DATE AS scheduled_date,
#             CURRENT_TIME AS scheduled_time,
#             'pending' AS status,
#             t.signoff_required,
#             false AS approved,
#             NOW() AS created_at
#         FROM checklist_schedule s
#         JOIN checklist_template t ON s.checklist_template = t.id
#         WHERE s.status = true;
#     """
#
#     cur.execute(insert_query)
#     conn.commit()
#     cur.close()
#     conn.close()
#     print(f"[{datetime.now()}] ✅ Populated daily checklists")
#
#
# # --- APScheduler integration ---
# scheduler = BackgroundScheduler()
#
# @app.on_event("startup")
# def start_scheduler():
#     # run daily at 17:40
#     # scheduler.add_job(populate_daily_checklists, "cron", hour=17, minute=40)
#     scheduler.add_job(populate_daily_checklists, "interval", minutes=2)
#     scheduler.start()
#     print("⏰ Scheduler started")
#
# @app.on_event("shutdown")
# def shutdown_scheduler():
#     scheduler.shutdown()
#     print("🛑 Scheduler stopped")
#
#
# # --- Example FastAPI endpoint ---
# @app.get("/")
# def home():
#     return {"msg": "FastAPI is running with APScheduler!"}
#
# @app.get("/run-now")
# def run_now():
#     populate_daily_checklists()
#     return {"msg": "Checklist job executed manually"}


from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from psycopg2.extras import RealDictCursor
import psycopg2
from datetime import datetime, date, time, timedelta
import logging
import os
import json
from typing import Any, Dict, List, Optional

# ---------- Logging ----------
LOG_FILE = os.path.join(os.path.dirname(__file__), "checklist.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ---------- FastAPI ----------
app = FastAPI()

# ---------- DB ----------
# DB_KW = dict(
#     dbname="checklistdb",
#     user="postgres",
#     password="postgres",
#     host="localhost",
#     port=5432,
# )

# ---------- DB ----------
DB_KW = dict(
    dbname="mabel_stage",
    user="mabel_user",
    password="Z44chg9GYgwtSqK",
    host="byod-stage.crwagmalobuu.us-east-2.rds.amazonaws.com",
    port=5432,
)

# postgresql://mabel_user:Z44chg9GYgwtSqK@byod-stage.crwagmalobuu.us-east-2.rds.amazonaws.com:5432/mabel_stage

# ---------- Helpers ----------
DAY_NAME_TO_INDEX = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}


def _parse_time_str(s: str) -> Optional[time]:
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
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        return v
    try:
        return json.loads(v)
    except Exception:
        return None


def _week_of_month(dt: date) -> int:
    first_day = dt.replace(day=1)
    return (dt.day + first_day.weekday()) // 7 + 1


def _is_last_week_of_month(dt: date) -> bool:
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
            times.append(_parse_time_str(str(once_time)))
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
    specific_dates = _ensure_json(srow.get("monthly_schedule_specific_dates")) or []
    for item in specific_dates:
        if not isinstance(item, dict):
            continue
        day_str = str(item.get("date"))
        if day_str.isdigit() and int(day_str) == today.day:
            times = _ensure_json(item.get("times")) or []
            return [_parse_time_str(str(t)) for t in times if _parse_time_str(str(t))]

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


# ---------- DB Insert ----------
def _insert_event_if_absent(cur, workplace: int, schedule_id: int, template_id: int,
                            scheduled_date: date, scheduled_time: Optional[time],
                            signoff_required: bool):
    cur.execute(
        """
        INSERT INTO checklist_schedule_event (
            workplace,
            checklist_schedule,
            checklist_template,
            scheduled_date,
            scheduled_time,
            status,
            signoff_required,
            approved,
            created_at
        )
        SELECT %s, %s, %s, %s, %s, 'pending', %s, false, NOW()
        WHERE NOT EXISTS (
            SELECT 1 FROM checklist_schedule_event e
            WHERE e.checklist_schedule = %s
              AND e.checklist_template = %s
              AND e.workplace = %s
              AND e.scheduled_date = %s
              AND (e.scheduled_time IS NOT DISTINCT FROM %s)
        );
        """,
        (
            workplace, schedule_id, template_id, scheduled_date, scheduled_time,
            signoff_required,
            schedule_id, template_id, workplace, scheduled_date, scheduled_time
        )
    )


def generate_today_events(target_date: Optional[date] = None) -> int:
    today = target_date or date.today()
    inserted_attempts = 0

    with psycopg2.connect(**DB_KW) as conn:
        conn.autocommit = False  # Ensure transactions are managed manually
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    s.*,
                    f.label AS frequency_label,
                    t.signoff_required
                FROM checklist_schedule s
                JOIN checklist_frequency f ON f.id = s.checklist_frequency
                JOIN checklist_template  t ON t.id = s.checklist_template
                WHERE s.status = true;
                """
            )
            rows: List[Dict[str, Any]] = list(cur.fetchall())

            for r in rows:
                try:
                    times = _times_for_schedule_today(r.get("frequency_label"), r, today)
                    for tm in times:
                        _insert_event_if_absent(
                            cur=cur,
                            workplace=int(r["workplace"]),
                            schedule_id=int(r["id"]),
                            template_id=int(r["checklist_template"]),
                            scheduled_date=today,
                            scheduled_time=tm,
                            signoff_required=bool(r.get("signoff_required", False)),
                        )
                        inserted_attempts += 1

                    conn.commit()  # Commit after successful inserts for one schedule
                except Exception as ex:
                    logging.error(f"Error processing schedule id={r.get('id')}: {ex}")
                    conn.rollback()  # Rollback only this schedule's failed transaction

    return inserted_attempts


# ---------- Scheduler job ----------
def populate_daily_checklists():
    try:
        n = generate_today_events()
        logging.info(f"✅ Generated events (attempted inserts): {n}")
    except Exception as e:
        logging.error(f"❌ populate_daily_checklists failed: {e}")


# ---------- APScheduler integration ----------
scheduler = BackgroundScheduler()


@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(populate_daily_checklists, "interval", minutes=2)
    scheduler.start()
    logging.info("⏰ Scheduler started (interval=2m)")


@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()
    logging.info("🛑 Scheduler stopped")


# ---------- Endpoints ----------
@app.get("/")
def home():
    return {"msg": "FastAPI + APScheduler running; see checklist.log for job output"}


@app.post("/generate-today")
def generate_today():
    n = generate_today_events()
    return {"attempted_inserts": n, "date": str(date.today())}
