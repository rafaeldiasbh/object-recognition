
from decouple import config
import ast

from ultralytics import YOLO

from ultralytics.utils.plotting import Annotator

DEFAULT_PREDICT_OPTIONS = {
    'confidence' : float(config('DEFAULT_PREDICT_CONFIDENCE')),
    'iou' : float(config('DEFAULT_PREDICT_IOU')),
    'imageSize' : ast.literal_eval(config('DEFAULT_PREDICT_IMAGE_SIZE')),
    'half' : ast.literal_eval(config('DEFAULT_PREDICT_HALF')),
    'maxDetections' : int(config('DEFAULT_PREDICT_MAX_DETECTIONS')),
    'augment' : ast.literal_eval(config('DEFAULT_PREDICT_AUGMENT')),
    'agnosticNMS' : ast.literal_eval(config('DEFAULT_PREDICT_AGNOSTIC_NMS')),
    'classesFilter' : ast.literal_eval(config('DEFAULT_PREDICT_CLASSES_FILTER')),
}

class YOLOv8Service:
    def __init__(self):
        pass

    def predict(self, frame, collection_code, options):
        from app.models.ModelManager import ModelManager

        try:
            model = ModelManager.get_model(collection_code)
            formattedOptions = self.getOptionsValues(options)
            result = model(
                frame,
                verbose = False,
                **formattedOptions,
            )
            return result
        except Exception as e:
            raise Exception(e)

    def getOptionsValues(self, options):
        if options is None: options = {}

        formattedOptions = {
            'conf' :  options['confidence'] if 'confidence' in options else DEFAULT_PREDICT_OPTIONS['confidence'],
            'iou' : options['iou'] if 'iou' in options else DEFAULT_PREDICT_OPTIONS['iou'],
            'imgsz' : options['imageSize'] if 'imageSize' in options else DEFAULT_PREDICT_OPTIONS['imageSize'],
            'half' : options['half'] if 'half' in options else DEFAULT_PREDICT_OPTIONS['half'],
            'max_det' : options['maxDetections'] if 'maxDetections' in options else DEFAULT_PREDICT_OPTIONS['maxDetections'],
            'augment' : options['augment'] if 'augment' in options else DEFAULT_PREDICT_OPTIONS['augment'],
            'agnostic_nms' : options['agnosticNMS'] if 'agnosticNMS' in options else DEFAULT_PREDICT_OPTIONS['agnosticNMS'],
            'classes' : options['classesFilter'] if 'classesFilter' in options else DEFAULT_PREDICT_OPTIONS['classesFilter'],
        }

        return formattedOptions

    def draw_rect(self, frame, rect, collection_code):
        from app.models.ModelManager import ModelManager
        try:
            model = ModelManager.get_model(collection_code)
            annotator = Annotator(frame)
            for box in rect:
                b = box.xyxy[0]  # get box coordinates in (left, top, right, bottom) format
                c = box.cls
                annotator.box_label(b, model.names[int(c)])
            frame = annotator.result()
            return frame
        except Exception as e:
            raise Exception(e)
        return None

    def format_result_data(self, result):
        try:
            formatted_data = []
            detection_count = result.boxes.shape[0]

            for i in range(detection_count):
                cls = int(result.boxes.cls[i].item())
                name = result.names[cls]
                confidence = float(result.boxes.conf[i].item())
                bounding_box = result.boxes.xyxy[i].cpu().numpy().tolist()
                image_height, image_width = result.orig_shape

                x = int(bounding_box[0])
                y = int(bounding_box[1])
                width = int(bounding_box[2] - x)
                height = int(bounding_box[3] - y)
                data = {
                    "class": cls,
                    "name": name,
                    "confidence": confidence,
                    "bounding_box": bounding_box,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "image_height": image_height,
                    "image_width": image_width,
                }
                formatted_data.append(data)
            return formatted_data
        except Exception as e:
            raise Exception(e)
        return None

    def load_model(self, model_path):
        model = YOLO(model= model_path)
        model.fuse()
        return model

    def model_info(self, collection_code):
        from app.models.ModelManager import ModelManager
        import os

        try:
            # Carregar o modelo usando o código da coleção
            model = ModelManager.get_model(collection_code)
            result = {}
            print(model)
            return result
        except Exception as e:
            raise Exception(f"Erro ao obter informações do modelo: {str(e)}")

        return None

    def ping(self):
        try:
            print("Local - FaceService")
            return True
        except Exception as e:
            raise Exception(e)
        return None