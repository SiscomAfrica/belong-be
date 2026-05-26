from __future__ import annotations

import environ
from celery.schedules import crontab

env = environ.Env()

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_TIME_LIMIT, CELERY_TASK_SOFT_TIME_LIMIT = 300, 240
CELERY_BEAT_SCHEDULE_FILENAME = "/tmp/celerybeat-schedule"
CELERY_BEAT_SCHEDULE = {
    "cleanup-expired-otps": {
        "task": "apps.authentication.tasks.cleanup_expired_otps",
        "schedule": 1800,
    },
    "calculate-fund-performance": {
        "task": "apps.funds.tasks.calculate_all_fund_performance",
        "schedule": crontab(hour=6, minute=0),
    },
    "fetch-exchange-rates": {
        "task": "apps.market_data.tasks.fetch_exchange_rates",
        "schedule": 21600,
    },
    "fetch-market-tickers": {
        "task": "apps.market_data.tasks.fetch_market_tickers",
        "schedule": 300,
    },
    "snapshot-all-portfolios": {
        "task": "apps.investments.tasks.snapshot_all_portfolios",
        "schedule": crontab(hour=7, minute=0),
    },
    "reconcile-pending-payments": {
        "task": "apps.payments.tasks.reconcile_pending_payments",
        "schedule": 600,
    },
    "check-kyc-timeout": {
        "task": "apps.kyc.tasks.check_kyc_timeout",
        "schedule": crontab(hour=9, minute=0),
    },
    "execute-due-recurring-plans": {
        "task": "apps.investments.tasks.execute_due_recurring_plans",
        "schedule": crontab(hour=5, minute=0),
    },
    "check-wishlist-yield-changes": {
        "task": "apps.wishlist.tasks.check_wishlist_yield_changes",
        "schedule": crontab(hour=10, minute=0),
    },
    "generate-monthly-statements": {
        "task": "apps.compliance.tasks.generate_monthly_statements",
        "schedule": crontab(day_of_month=1, hour=2, minute=0),
    },
}
