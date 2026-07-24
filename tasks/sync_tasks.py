from flask_caching import logger
from celery_app import celery
from app import app
from scripts.sync_coingecko import (
    sync_markets,
    sync_trending,
    sync_categories,
    sync_exchanges,
    sync_top_coin_details,
    sync_ohlc,
    sync__popular_searches,
)

def _run_sync(func, *args, **kwargs):
    try:
        with app.app_context():
            func(*args, **kwargs)
            logger.info(f"Synced {func.__name__}")
    except Exception as e:
        logger.error(f"Error syncing {func.__name__}: {e}")
        raise e

@celery.task(name="tasks.sync_tasks.sync_markets")
def sync_markets_task():
    _run_sync(sync_markets)

@celery.task(name="tasks.sync_tasks.sync_trending")
def sync_trending_task():
    _run_sync(sync_trending)

@celery.task(name="tasks.sync_tasks.sync_categories")
def sync_categories_task():
    _run_sync(sync_categories)

@celery.task(name="tasks.sync_tasks.sync_exchanges")
def sync_exchanges_task():
    _run_sync(sync_exchanges)

@celery.task(name="tasks.sync_tasks.sync_top_coin_details")
def sync_top_coin_details_task():
    _run_sync(sync_top_coin_details)

@celery.task(name="tasks.sync_tasks.sync_ohlc")
def sync_ohlc_task():
    _run_sync(sync_ohlc)