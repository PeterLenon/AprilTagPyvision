from loguru import logger
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2
from stoneDetection import getPos
from tagDetection import tag_detection

def video_processing(frame_queue, sinkfile):
	stones_and_apriltags = dict()
	_writeToFile(filepath=sinkfile)

	while not frame_queue.empty():
		frame = frame_queue.get()
		payloads = tag_detection(frame=frame)
		if payloads:
			stones_and_apriltags["stones"] = set()
			for info in payloads:
				logger.info(info)
				stones_and_apriltags["apriltags"].add(info)

		stones = getPos(frame=frame)
		if "stones" in stones.keys():
			stones_and_apriltags["apriltags"] = set()
			for stone in stones["stones"]:
				x, y = stone
				logger.info(f"Stone x_angle --> {x} degrees, Stone y_depth --> {y} mm")
				stones_and_apriltags["stones"].add(stone)
		else:
			logger.info("No stones detected!")

	if "apriltags" in stones_and_apriltags.keys():
		stones_and_apriltags["apriltags"] = list(stones_and_apriltags["apriltags"])
	if "stones" in stones_and_apriltags.keys():
		stones_and_apriltags["stones"] = list(stones_and_apriltags["stones"])
	if stones_and_apriltags.keys():
		_writeToFile(filepath=sinkfile, content=repr(stones_and_apriltags))

def _writeToFile(filepath, content='{"stones" : [], "apriltags": []}'):
	with open(file=filepath, mode="w") as file:
		file.write(content)
		file.close()