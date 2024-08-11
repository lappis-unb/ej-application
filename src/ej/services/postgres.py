import importlib
import os
import time

import logging

log = logging.getLogger("ej")


def start_postgres():
    settings_path = os.environ["DJANGO_SETTINGS_MODULE"]
    settings = importlib.import_module(settings_path)

    db = settings.DATABASES["default"]
    dbname = db["NAME"]
    user = db["USER"]
    password = db["PASSWORD"]
    host = db["HOST"]
    port = db["PORT"]

    for _ in range(10):
        if can_connect(dbname, user, password, host, port):
            log.info("Postgres is available. Continuing...")
            return
        log.warning("Postgres is unavailable. Retrying in 0.5 seconds")
        time.sleep(0.5)

    log.critical("Maximum number of attempts connecting to postgres database")
    raise RuntimeError("could not connect to database")


def can_connect(dbname, user, password, host, port):
    import psycopg2

    try:
        psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port
        )
    except psycopg2.OperationalError:
        return False
    return True
