import cv2
from loguru import logger
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2

def video_streaming(frame_queue):
	camera = Picamera2()
	camera.preview_configuration.main.size = (640, 480)
	camera.preview_configuration.main.format = "RGB888"
	camera.configure("preview")
	camera.start()
	
	while True:
		if frame_queue.full():
			break
		frame = camera.capture_array()
		frame_queue.put(frame)

	camera.stop()
	cv2.destroyAllWindows()
	return frame_queue
	