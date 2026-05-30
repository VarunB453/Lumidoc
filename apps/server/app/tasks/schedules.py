"""Celery Beat schedule definitions."""
from __future__ import annotations

# Beat schedule configuration — add to celery_app.conf.beat_schedule
BEAT_SCHEDULE: dict = {
    # Example: cleanup expired sessions every hour
    # "cleanup-expired-sessions": {
    #     "task": "app.tasks.maintenance.cleanup_sessions",
    #     "schedule": crontab(minute=0),
    # },
    # Example: generate daily usage report at midnight
    # "daily-usage-report": {
    #     "task": "app.tasks.reports.generate_daily_report",
    #     "schedule": crontab(hour=0, minute=0),
    # },
}
