import cv2
from loguru import logger
import multiprocessing
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
		frame = camera.capture_array()
		if not frame_queue.full():
			frame_queue.put(frame)
		
		cv2.imshow("Picamera Video stream", frame)
		if cv2.waitKey(1) & 0xFF ==ord('q'):
			break
	
	camera.stop()
	cv2.destroyAllWindows()

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


frame_queue = multiprocessing.Queue(maxsize=10)
streaming = multiprocessing.Process(target=video_streaming, args=(frame_queue, ))
detection = multiprocessing.Process(target=tag_detection, args=(frame_queue, ))

streaming.start()
detection.start()

streaming.join()
detection.join()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
