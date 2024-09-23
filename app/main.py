import json
import threading
import sys
import signal
import time
from waitress import serve

from decouple import config

from app.web.ws import app
from app.utils.logger import Logger
from app.jobs import create_scheduler

HTTP_HOST = config('HTTP_HOST')
HTTP_PORT = config('HTTP_PORT')
APP_ENV = config('APP_ENV')
VERSION = config('VERSION')
RUN_JOBS = config('RUN_JOBS')
DETECTION_MODEL_TYPE = config('DETECTION_MODEL_TYPE')

log = Logger()

def startServer():
  if APP_ENV == 'development':
      app.run(host=HTTP_HOST, debug=False, port=HTTP_PORT, use_reloader=False)
  elif APP_ENV == 'production':
      app.run(host=HTTP_HOST, debug=False, port=HTTP_PORT, use_reloader=False)
      #serve(app, host=HTTP_HOST, port=HTTP_PORT)

def signal_handler(sig, frame):
    sys.exit(0)

if __name__ == 'app.main':
  print(f'''
             _____ _____ _   __ _   _ _____ _____  ___
            |_   _|  ___| | / /| \\ | |_   _/  ___|/ _ \\
              | | | |__ | |/ / |  \\| | | | \\ `--./ /_\\ \\
              | | |  __||    \\ | . ` | | |  `--. \\  _  |
              | | | |___| |\\  \\| |\\  |_| |_/\\__/ / | | |
              \\_/ \\____/\\_| \\_/\\_| \\_/\\___/\\____/\\_| |_/
                ______ _____ ___________ _   _ _____
               |___  /|  ___|  ___|  _  \\ | | |_   _|
                  / / | |__ | |__ | | | | |_| | | |
                 / /  |  __||  __|| | | |  _  | | |
               ./ /___| |___| |___| |/ /| | | |_| |_
               \\_____/\\____/\\____/|___/ \\_| |_/\\___/

  ##############################################################
  ZEEDHI RECOGNITION version {VERSION} is running on port {HTTP_PORT}
  ##############################################################
  DETECTION MODEL TYPE: {DETECTION_MODEL_TYPE}
  ##############################################################''')

  signal.signal(signal.SIGINT, signal_handler)

  with app.app_context():
    if RUN_JOBS:
      create_scheduler(app)

  startServer()

  while(True):
    pass
