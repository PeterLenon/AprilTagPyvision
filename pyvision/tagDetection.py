import cv2
from loguru import logger
import multiprocessing
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2

def tag_detection(frame_queue):
	detector = apriltag("tag36h11")
	
	while True:
		if not frame_queue.empty():
			frame = frame_queue.get()
			gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
			detections = detector.detect(gray)
			
			for detection in detections:
				pay_load = detection.id
				logger.info(f"Detected apriltag information: {pay_load}")
			
			cv2.imshow("Apriltag detection", gray)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
