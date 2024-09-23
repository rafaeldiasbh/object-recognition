import os
import datetime
import logging
from decouple import config
import sys

LOG_PATH = config('LOG_PATH')
LOG_FORMAT = config('LOG_FORMAT')
LOG_ENABLED = bool(config('LOG_ENABLED'))

class Logger:
    def log_enabled(func):
        def wrapper(*args, **kwargs):
            if LOG_ENABLED is True:
                return func(*args, **kwargs)
        return wrapper

    def __init__(self,level=10):

        date  = datetime.datetime.now()
        date_string = date.strftime("%Y-%m-%d")

        logging.basicConfig(
            level = level,
            format = LOG_FORMAT,
            handlers=[
                logging.FileHandler(f"{LOG_PATH}/log_{date_string}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger()
    
    @log_enabled
    def info(self,message):
        self.logger.info(message)

    @log_enabled
    def debug(self,message):
        self.logger.debug(message)

    @log_enabled
    def error(self,message):
        self.logger.error(message)

    @log_enabled
    def exception(self,message):
        self.logger.exception(message)