## Celery
# Terminal 1 — worker
celery -A celery_app.celery worker --loglevel=info

# Terminal 2 — scheduler (only one Beat process!)
celery -A celery_app.celery beat --loglevel=info

# Update
python scripts/sync_coingecko.py --tasks markets,top-coins,ohlc