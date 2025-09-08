from datetime import date, time
import logging
from typing import Any, Dict, List, Optional
from app_today.core.db import get_connection
from app_today.utils.checklist_utils import _times_for_schedule_today

def _insert_event_if_absent(cur, workplace: int, schedule_id: int, template_id: int,
                            scheduled_date: date, scheduled_time: Optional[time],
                            signoff_required: bool):
    cur.execute(
        """
        INSERT INTO checklist_schedule_event (
            workplace, checklist_schedule, checklist_template,
            scheduled_date, scheduled_time, status,
            signoff_required, approved, created_at
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

    with get_connection() as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.*, f.label AS frequency_label, t.signoff_required
                FROM checklist_schedule s
                JOIN checklist_frequency f ON f.id = s.checklist_frequency
                JOIN checklist_template  t ON t.id = s.checklist_template
                WHERE s.status = true;
                """
            )
            rows: List[Dict[str, Any]] = list(cur.fetchall())

            for r in rows:
                try:
                    logging.info(f"➡️ Processing schedule id={r.get('id')}, frequency={r.get('frequency_label')}")
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

                    conn.commit()
                    logging.info(f"✅ Successfully processed schedule id={r.get('id')}")
                except Exception as ex:
                    logging.error(f"❌ Error processing schedule id={r.get('id')} -> rolled back")
                    logging.error(str(ex), exc_info=True)
                    conn.rollback()

    return inserted_attempts
