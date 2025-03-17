import cv2
from loguru import logger
import multiprocessing
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2
import subprocess

from videoStreaming import video_streaming 
from videoProcessing import video_processing

if __name__ == "__main__":
	result = subprocess.run(["libcamera-hello"])
	
	frame_queue = multiprocessing.Queue(maxsize=10)
	streaming = multiprocessing.Process(target=video_streaming, args=(frame_queue, ))
	processing = multiprocessing.Process(target=video_processing, args=(frame_queue, ))

	streaming.start()
	processing.start()

	streaming.join()
	processing.join()