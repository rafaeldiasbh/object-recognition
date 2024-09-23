from decouple import config

from app.services.YOLOv8Service import YOLOv8Service
from app.utils.logger import Logger

DETECTION_MODEL_TYPE = config('DETECTION_MODEL_TYPE')

if DETECTION_MODEL_TYPE == 'YOLOv8':
    detectionService = YOLOv8Service()
elif DETECTION_MODEL_TYPE == 'YOLOv88':
    detectionService = YOLOv8Service()
else:
    detectionService = YOLOv8Service()

class DetectionController:

    def __init__(self):
        pass

    def predict(self, frame, collection_code, options):
        try:
            return detectionService.predict(frame, collection_code, options)
        except Exception as e:
            raise Exception(e)
        return None

    def draw_rect(self, frame, rect, collection_code):
        try:
            return detectionService.draw_rect(frame, rect, collection_code)
        except Exception as e:
            raise Exception(e)
        return None

    def format_result_data(self, result):
        try:
            return detectionService.format_result_data(result)
        except Exception as e:
            raise Exception(e)
        return None

    def load_model(self, model_path):
        try:
            return detectionService.load_model(model_path)
        except Exception as e:
            raise Exception(e)
        return None

    def model_info(self, collection_code):
        try:
            return detectionService.model_info(collection_code)
        except Exception as e:
            raise Exception(e)
        return None

    def ping(self):
        try:
            print("Detection Controller")

            return True
        except Exception as e:
            raise Exception(e)
        return None