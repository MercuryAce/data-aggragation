import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery = Celery("cryptodash")

celery.config_from_object("celeryconfig", namespace="CELERY")

# Only override when explicitly set — avoid wiping celeryconfig defaults with None
broker_url = os.getenv("CELERY_BROKER_URL")
result_backend = os.getenv("CELERY_RESULT_BACKEND")
if broker_url:
    celery.conf.broker_url = broker_url
if result_backend:
    celery.conf.result_backend = result_backend
