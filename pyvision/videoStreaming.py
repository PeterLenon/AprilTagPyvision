import cv2
from loguru import logger
import multiprocessing
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2
import subprocess

def video_streaming(frame_queue):
	camera = Picamera2()
	camera.preview_configuration.main.size = (640, 480)
	camera.preview_configuration.main.format = "RGB888"
	camera.configure("preview")
	camera.start()
	
	while True:
		frame = camera.capture_array()
		if not frame_queue.full():
			frame_queue.put(frame)
		
		cv2.imshow("Picamera Video stream", frame)
		if cv2.waitKey(1) & 0xFF ==ord('q'):
			break
	
	camera.stop()
	cv2.destroyAllWindows()