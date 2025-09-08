# ⏰ Cron Job Scheduler Application

This project provides **Python-based applications** to manage and schedule recurring checklist events using **FastAPI**, **PostgreSQL**, and **APScheduler**.

It includes two applications:

* **`app_today`** → Generates checklist events only for **today**.
* **`app_three_days`** → Generates checklist events for **today + the next 2 days**.

---

## ✨ Features

* **Flexible Scheduling**
  Supports multiple frequencies:

  * Daily
  * Weekly
  * Weekday
  * Monthly
  * Annually
  * Ad-hoc
  * One-time events
  * *(Quarterly support is under review)*

* **Database Integration**

  * Schedules are pulled from PostgreSQL.
  * Events are inserted if not already present.

* **Logging**

  * Tracks execution flow, errors, and inserted events.

* **API Endpoints**

  * Trigger event generation manually via FastAPI.

* **Two Versions**

  * `app_today`: Runs daily for current date.
  * `app_three_days`: Runs for 3-day rolling window.

---

## 📦 Prerequisites

* Python **3.8+**
* PostgreSQL database
* Required Python packages:

  ```
  fastapi
  uvicorn
  sqlalchemy
  sqlalchemy[asyncio]
  apscheduler
  pytz
  psycopg2-binary
  ```

---

## ⚙️ Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd cron
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate       # On macOS/Linux
   .venv\Scripts\activate          # On Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**

   * Create `config.py`:

     ```python
     settings = {
         "sync_database_url": "postgresql://user:password@localhost:5432/cron_db",
         "async_database_url": "postgresql+asyncpg://user:password@localhost:5432/cron_db"
     }
     ```
   * Replace `user`, `password`, and `cron_db` with actual credentials.

5. **Prepare required tables**

   * `checklist_schedule`
   * `checklist_frequency`
   * `checklist_schedule_event`
   * `checklist_schedule_date`
   * `checklist_template`

---

## 🚀 Usage

### Run `app_today`

Generates checklist events for **today only**.

```bash
uvicorn app_today:app --reload --host 0.0.0.0 --port 8000
```

* Default endpoint:

  ```http
  GET /checklist/
  ```
* Trigger generation manually:

  ```http
  POST /checklist/generate-today
  ```

---

### Run `app_three_days`

Generates checklist events for **today + next 2 days**.

```bash
uvicorn app_three_days:app --reload --host 0.0.0.0 --port 8001
```

* Default endpoint:

  ```http
  GET /checklist/
  ```
* Trigger generation manually:

  ```http
  POST /checklist/generate-three-days
  ```

---

## 🔧 Configuration

* **Cron Time** → Set in `cron.py`:

  ```python
  cron_hour = 9
  cron_minute = 30
  ```
* **Misfire Grace Time** → Defaults to `300s` (5 minutes).
* **Frequency Codes** (from `checklist_frequency` table):

  * `7` → Annually
  * `8` → One-time

---

## 📜 Logging

* Logs are written to `checklist.log` (per app).
* Includes job start/stop, inserts, and errors.
* Configurable in `logging.basicConfig()` inside each app.

---

## 🛠️ Troubleshooting

* **Scheduler not running**

  * Ensure `.start()` is called in each app's startup event.
* **No events generated**

  * Check that schedule data matches the target date(s).
* **API not responding**

  * Verify FastAPI server is running at correct port.
  * Ensure PostgreSQL connection works.

---

✅ With this setup, you can choose between **daily-only (`app_today`)** or **rolling 3-day (`app_three_days`)** scheduling, depending on your business requirements.

---