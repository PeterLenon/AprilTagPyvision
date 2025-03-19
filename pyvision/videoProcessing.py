from loguru import logger
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2
from stoneDetection import getPos
from tagDetection import tag_detection
import json

def video_processing(frame_queue, sinkfile):
	logged_stones_false = False
	while not frame_queue.empty():
		frame = frame_queue.get()
		payloads = tag_detection(frame=frame)
		for info in payloads:
			logger.info(info)

		stones = getPos(frame=frame)
		if "stones" in stones.keys():
			_writeToFile(sinkfile, repr(stones))
			for stone in stones["stones"]:
				x, y = stone
				logger.info(f"Stone x_angle --> {x} degress, Stone y_depth --> {y} mm")
				logged_stones_false = False
			
		else:
			if not logged_stones_false:
				logger.info("No stones detected!")
				logged_stones_false = True

def _writeToFile(filepath, content):
	with open(file=filepath, mode="w") as file:
		file.write(content)
		file.close()