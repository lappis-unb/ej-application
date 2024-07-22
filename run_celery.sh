#!/bin/bash

export PYTHONPATH=$(pwd)/src

celery -A ej_clusters beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &

celery -A ej_clusters worker -l INFO &

wait
