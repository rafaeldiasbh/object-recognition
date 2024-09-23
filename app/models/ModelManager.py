from decouple import config
from app.controllers.DetectionController import DetectionController
from app.utils.logger import Logger
import os


detectionController = DetectionController()
log = Logger()

MODELS_PATH = config('MODELS_PATH')
MODELS_FILE_NAME = config('MODELS_FILE_NAME')

class ModelManager:
    _models = {}

    @staticmethod
    def get_model(collection_code):
        if collection_code in ModelManager._models and ModelManager._models[collection_code] is not None:
            return ModelManager._models[collection_code]
        
        try:
            file_path = f'{MODELS_PATH}/{collection_code}/{MODELS_FILE_NAME}'
            if os.path.exists(file_path):
                log.info(f'Carregando modelo {collection_code}')
                model = detectionController.load_model(file_path)
                log.info(f'Modelo {collection_code} carregado')
                ModelManager._models[collection_code] = model
                return model
            else:
                error = f"Erro ao carregar o modelo, arquivo do modelo nao existe para a o: {collection_code}"
                log.error(error)
                raise Exception(error)
        except Exception as e:
            raise Exception(e)

    @staticmethod
    def clear_model(collection_code):
        try:
            log.info(f'Limpando modelo {collection_code}')
            del ModelManager._models[collection_code]
            log.info(f'Modelo {collection_code} limpo')
        except Exception as e:
            # Caso não seja possível carregar o modelo
            print(f"Erro ao limpar o modelo: {e}")
            raise e

    @staticmethod
    def refresh_model(collection_code):
        try:
            file_path = f'{MODELS_PATH}/{collection_code}/{MODELS_FILE_NAME}'
            if os.path.exists(file_path):
                log.info(f'Reiniciando modelo {collection_code}')
                model = detectionController.load_model(file_path)
                ModelManager._models[collection_code] = model
                log.info(f'Modelo {collection_code} reiniciado')
                return model
            else:
                error = f"Erro ao recarregar o modelo, arquivo do modelo nao existe para a o: {collection_code}"
                raise Exception(error)

        except Exception as e:
            log.error(f"Erro ao recarregar o modelo: {e}")
            raise e

    @staticmethod
    def list_models():
        try:
            if isinstance(ModelManager._models, dict):
                return list(ModelManager._models.keys())

            return []
        except Exception as e:
            # Caso não seja possível carregar o modelo
            log.error(f"Erro ao listar os modelos: {e}")
            return []

    @staticmethod
    def get_model_size(collection_code):
        if collection_code in ModelManager._models:
            return ModelManager._models[collection_code]

        try:
            model_path = f'{MODELS_PATH}/{collection_code}/{MODELS_FILE_NAME}'
            # Tamanho do modelo em MB
            model_size = os.path.getsize(model_path) / (1024 ** 2)  # Tamanho em MB
            return model_size
        except Exception as e:
            # Caso não seja possível carregar o modelo
            print(f"Erro ao calcular tamanho do modelo: {e}")
            return None