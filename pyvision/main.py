import cv2
from loguru import logger
import multiprocessing
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2
import subprocess

from videoStreaming import video_streaming 
from tagDetection import tag_detection

if __name__ == "__main__":
	result = subprocess.run(["libcamera-hello"])
	
	frame_queue = multiprocessing.Queue(maxsize=10)
	streaming = multiprocessing.Process(target=video_streaming, args=(frame_queue, ))
	apriltagDetection = multiprocessing.Process(target=tag_detection, args=(frame_queue, ))

	streaming.start()
	apriltagDetection.start()

	streaming.join()
	apriltagDetection.join()