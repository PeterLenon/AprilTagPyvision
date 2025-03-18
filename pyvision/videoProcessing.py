import cv2
from loguru import logger
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2
from bucketStoneDetection import getPos

def video_processing(frame_queue):
	apriltagDetector = apriltag("tag36h11")
	logged_bucket_false = False
	logged_stones_false = False
	while True:
		if not frame_queue.empty():
			frame = frame_queue.get()

			payloads = _tag_detection(frame=frame, detector=apriltagDetector)
			for info in payloads:
				logger.info(info)
			
			buckets_and_stones = getPos(frame=frame)
			if "buckets" in buckets_and_stones.keys():
				for bucket in buckets_and_stones["buckets"]:
					x, y = bucket
					logger.info(f"Bucket x_angle --> {x} degrees, Bucket y_depth --> {y} mm")
					logged_bucket_false = False
			else:
				if not logged_bucket_false:
					logger.info("No buckets detected!")
					logged_bucket_false = True

			
			if "stones" in buckets_and_stones.keys():
				for stone in buckets_and_stones["stones"]:
					x, y = stone
					logger.info(f"Stone x_angle --> {x} degress, Stone y_depth --> {y} mm")
					logged_stones_false = False
			else:
				if not logged_stones_false:
					logger.info("No stones detected!")
					logged_stones_false = True
				

def _tag_detection(frame, detector):
	detector = apriltag("tag36h11")
	gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
	detections = detector.detect(gray)
	pay_loads = []
	for detection in detections:
		pay_loads.append(detection.id)
	return pay_loads