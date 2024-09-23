import cv2
from app.controllers.DetectionController import DetectionController

print("Ligando camera 0")
video = cv2.VideoCapture(0)

detectionController = DetectionController()

while True:
    _ , frame  = video.read()
    result = detectionController.predict(frame, '20')

    cv2.imshow("Live Camera", result[0].plot())

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break