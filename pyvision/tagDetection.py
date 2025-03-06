import cv2
from loguru import logger
import multiprocessing
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2
from bucketStoneDetection import getPos

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
			
			buckets_and_stones = getPos(frame=frame)
			for bucket in buckets_and_stones["buckets"]:
				x, y = bucket
				logger.info(f"Bucket x_depth --> {x} mm, Bucket y_depth --> {y} mm")
			
			for stone in buckets_and_stones["stones"]:
				x, y = stone
				logger.info(f"Stone x_depth --> {x} mm, Stone y_depth --> {y} mm")
