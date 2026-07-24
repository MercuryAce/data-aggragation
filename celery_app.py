import os
from celery import Celery

celery = Celery("cryptodash")

celery.config_from_object("celeryconfig", namespace="CELERY")

celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")
