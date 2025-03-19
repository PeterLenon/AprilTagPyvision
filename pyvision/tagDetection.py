import cv2
from apriltag import apriltag

def tag_detection(frame):
	apriltagDetector = apriltag("tag36h11")
	gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
	detections = apriltagDetector.detect(gray)
	pay_loads = []
	for detection in detections:
		pay_loads.append(detection.id)
	return pay_loads