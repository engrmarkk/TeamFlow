#!/bin/sh
celery -A celery_config.worker worker --loglevel=info
