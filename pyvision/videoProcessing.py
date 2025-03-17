import cv2
from loguru import logger
import multiprocessing
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2
from bucketStoneDetection import getPos

def video_processing(frame_queue):
	apriltagDetector = apriltag("tag36h11")
	while True:
		if not frame_queue.empty():
			frame = frame_queue.get()

			payloads = tag_detection(frame=frame, detector=apriltagDetector)
			for info in payloads:
				logger.info(info)
			
			buckets_and_stones = getPos(frame=frame)
			for bucket in buckets_and_stones["buckets"]:
				x, y = bucket
				logger.info(f"Bucket x_depth --> {x} mm, Bucket y_depth --> {y} mm")
			
			for stone in buckets_and_stones["stones"]:
				x, y = stone
				logger.info(f"Stone x_depth --> {x} mm, Stone y_depth --> {y} mm")

def tag_detection(frame, detector):
	detector = apriltag("tag36h11")
	gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
	detections = detector.detect(gray)
	pay_loads = []
	for detection in detections:
		pay_loads.append(detection.id)
	return pay_loads