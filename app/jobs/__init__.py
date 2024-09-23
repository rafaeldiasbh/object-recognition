from app.utils.logger import Logger
from decouple import config
from datetime import datetime
from flask_apscheduler import APScheduler

from app.jobs.check_and_restart_models import check_and_restart_models

check_and_restart_models_instance = check_and_restart_models()

log = Logger()

CHECK_MODELS_INTERVAL = int(config('CHECK_MODELS_INTERVAL'))

def create_scheduler(app):
    scheduler = APScheduler()
    with app.app_context():
        scheduler.init_app(app)
        scheduler.start()

    @scheduler.task("interval", id="check_and_restart_models", seconds = CHECK_MODELS_INTERVAL)
    def check_and_restart_models_job():
        log.info(f'Checking and Restarting Models')
        with app.app_context():
            check_and_restart_models_instance.check_and_restart_models()
