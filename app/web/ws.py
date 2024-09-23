import base64
from datetime import timedelta
from flask import Flask, request, make_response, current_app, jsonify
from flask_cors import CORS, cross_origin
import cv2
import json
from functools import update_wrapper
from flask_sock import Sock

import numpy as np

from app.controllers.DetectionController import DetectionController
from app.models.ModelManager import ModelManager

from app.utils.logger import Logger

app = Flask(__name__)
sock = Sock(app)
CORS(app, support_credentials=True)

detectionController = DetectionController()

log = Logger()

class WebServer:
    def __init__(self):
        pass

    def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
        """Decorator function that allows crossdomain requests.
            Courtesy of
            https://blog.skyred.fi/articles/better-crossdomain-snippet-for-flask.html
        """
        if methods is not None:
            methods = ', '.join(sorted(x.upper() for x in methods))
        # use str instead of basestring if using Python 3.x
        if headers is not None and not isinstance(headers, basestring):
            headers = ', '.join(x.upper() for x in headers)
        # use str instead of basestring if using Python 3.x
        if not isinstance(origin, str):
            origin = ', '.join(origin)
        if isinstance(max_age, timedelta):
            max_age = max_age.total_seconds()

        def get_methods():
            """ Determines which methods are allowed
            """
            if methods is not None:
                return methods

            options_resp = current_app.make_default_options_response()
            return options_resp.headers['allow']

        def decorator(f):
            """The decorator function
            """
            def wrapped_function(*args, **kwargs):
                """Caries out the actual cross domain code
                """
                if automatic_options and request.method == 'OPTIONS':
                    resp = current_app.make_default_options_response()
                else:
                    resp = make_response(f(*args, **kwargs))
                if not attach_to_all and request.method != 'OPTIONS':
                    return resp

                h = resp.headers
                h['Access-Control-Allow-Origin'] = origin
                h['Access-Control-Allow-Methods'] = get_methods()
                h['Access-Control-Max-Age'] = str(max_age)
                h['Access-Control-Allow-Credentials'] = 'true'
                h['Access-Control-Allow-Headers'] = \
                    "Origin, X-Requested-With, Content-Type, Accept, Authorization"
                if headers is not None:
                    h['Access-Control-Allow-Headers'] = headers
                return resp

            f.provide_automatic_options = False
            return update_wrapper(wrapped_function, f)
        return decorator

    @sock.route('/predict_image/<string:collection_code>')
    def predict_image(ws, collection_code):
        try:
            ready = True
            log.info(f'Conexão websocket estabelecida para: {collection_code}')
            log.info(f'Recarregando o modelo {collection_code}')
            ModelManager.refresh_model(collection_code)
            while True:
                message = ws.receive()
                if message is None:
                    continue
                message_object = json.loads(message)
                if message_object['data'] is None:
                    continue

                message_data = message_object['data']
                event = message_data['event']
                if(event == 'predict' and ready):
                    ready = False
                    # log.info(f'mensagem recebida do client da collection {collection_code}')

                    frame_buffer_b64 = message_data['frame_buffer']
                    frame_buffer = base64.b64decode(frame_buffer_b64.split(',')[-1])
                    np_img = np.frombuffer(frame_buffer, dtype=np.uint8)
                    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)


                    predict_options = message_data['options'] if 'options' in message_data else {}

                    # log.info(f'detecçao INICIADA para a collection {collection_code}')
                    result = detectionController.predict(frame, collection_code, predict_options)
                    # log.info(f'detecçao FINALIZADA para a collection {collection_code}')
                    if result is None:
                        return_message = {
                            "data": {
                                "event": "predict",
                                "data": False,
                                "message": f'Modelo referente a {collection_code} não encontrado',
                                "status": False,
                            },
                        }
                        ready = True
                        ws.send(json.dumps(return_message))
                        continue

                    [result] = result

                    detection_data = detectionController.format_result_data(result)
                    return_message = {
                        "data": {
                            "event": "predict",
                            "data": detection_data,
                            "status": True,
                        },
                    }
                    ready = True
                    ws.send(json.dumps(return_message))

                if(event == 'check_status'):
                    return_message = {
                        "data": {
                            "event": "check_status",
                            "data": ready,
                        }
                    }
                    ws.send(json.dumps(return_message))
        except Exception as e:
            return_message = {
                "data": {
                    "event": "predict",
                    "message": str(e),
                    "status": False,
                    "data": False,
                },
            }

            log.error(f'Erro ao fazer detecção: {e}')
            ws.send(json.dumps(return_message))
        finally:
            pass

    @sock.route('/ping')
    def ping(ws):
        try:
            while True:
                message = ws.receive()
                if message is None:
                    continue
                ws.send(message)
        finally:
            pass

    @app.route('/predict_image/<string:collection_code>', methods=['POST', 'OPTIONS'])
    @cross_origin(supports_credentials=True)
    def predict_image_post(collection_code):
        data = request.get_json()
        try:
            log.info(f'mensagem recebida do client da collection {collection_code}')

            frame_buffer_b64 = data['image']
            predict_options = data['options'] if 'options' in data else {}
            frame_buffer = base64.b64decode(frame_buffer_b64.split(',')[-1])
            np_img = np.frombuffer(frame_buffer, dtype=np.uint8)
            frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

            #log.info(f'detecçao INICIADA para a collection {collection_code}')
            result = detectionController.predict(frame, collection_code, predict_options)
            log.info(f'detecçao FINALIZADA para a collection {collection_code}')
            if result is None:
                return_message = {
                    "data": {
                        "data": False,
                        "message": f'Modelo referente a {collection_code} não encontrado',
                        "status": False,
                    },
                }
                return (json.dumps(return_message)), 402

            [result] = result

            detection_data = detectionController.format_result_data(result)
            return_message = {
                "data": {
                    "data": detection_data,
                    "status": True,
                },
            }
            return (json.dumps(return_message)), 200
        except Exception as e:
            return_message = {
                "data": {
                    "message": str(e),
                    "status": False,
                },
            }
            return (json.dumps(return_message)), 402
        finally:
            pass

    @app.route('/model_info/<string:collection_code>', methods=['GET', 'OPTIONS'])
    @cross_origin(supports_credentials=True)
    def model_info(collection_code):
        try:
            log.info(f'obtendo informações do modelo {collection_code}')

            model_info = detectionController.model_info(collection_code)

            if model_info is None:
                return_message = {
                    "data": {
                        "data": False,
                        "message": f'Modelo referente a {collection_code} não encontrado',
                        "status": False,
                    },
                }
                return (jsonify(return_message)), 402

            return_message = {
                "data": {
                    "data": model_info,
                    "status": True,
                },
            }
            return (jsonify(return_message)), 200
        finally:
            pass

    @app.route('/refresh_model/<string:collection_code>', methods=['GET', 'OPTIONS'])
    @cross_origin(supports_credentials=True)
    def refresh_model(collection_code):
        try:
            log.info(f'Atualizando o modelo {collection_code}')

            status = ModelManager.refresh_model(collection_code)

            if status is None:
                return_message = {
                    "data": {
                        "data": False,
                        "message": f'Modelo referente a {collection_code} não encontrado',
                        "status": False,
                    },
                }
                return (jsonify(return_message)), 402

            return_message = {
                "data": {
                    "data": True,
                    "status": True,
                },
            }
            return (jsonify(return_message)), 200
        finally:
            pass

def getException(e):
    log.exception(e)
    if isinstance(e, Exception):
        if len(list(e.args)) == 0:
            args = [e]
        else:
            args = list(e.args)
    else:
        args = list(e)
    return args if len(args) > 1 else (args[0], 400)

def validate_parameters(*parameters):
    parameter_values = []
    if len(parameters) == 0 or parameters is None:
        return None
    for parameter in parameters:
        if parameter not in request.json or request.json[parameter] is None:
            raise Exception(f'O parâmetro `{parameter}` não foi enviado ou está vazio.', 400)
        parameter_values.append(request.json[parameter])
    return tuple(parameter_values) if len(parameter_values) > 1 else parameter_values[0]

