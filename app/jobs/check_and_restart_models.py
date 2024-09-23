from decouple import config
import os
from app.models.ModelManager import ModelManager
from app.utils.logger import Logger
from flask import current_app as app

log = Logger()

MODELS_PATH = config('MODELS_PATH')
MODELS_FILE_NAME = config('MODELS_FILE_NAME')

class check_and_restart_models:
    def __init__(self):
        self.last_mod_times = {}

    def check_and_restart_models(self):
        with app.app_context():
            collection_code_list = ModelManager.list_models()
            if len(collection_code_list) == 0:
                log.info("Sem modelos a ser verificados")
                return
            for collection_code in collection_code_list:
                file_path = f'{MODELS_PATH}/{collection_code}/{MODELS_FILE_NAME}'
                if os.path.exists(file_path):
                    last_mod_time = os.path.getmtime(file_path)
                    if collection_code not in self.last_mod_times:
                        log.info("Registrando ultima modificação do modelo: " + collection_code)
                        self.last_mod_times[collection_code] = last_mod_time

                    if last_mod_time != self.last_mod_times[collection_code]:
                        log.info("Recarregando modelo: " + collection_code)
                        ModelManager.refresh_model(collection_code)
                        self.last_mod_times[collection_code] = last_mod_time
                else:
                    log.info(f"Arquivo do modelo não encontrado: {file_path}")