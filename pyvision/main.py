import cv2
import multiprocessing
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2
import subprocess
from videoStreaming import video_streaming 
from videoProcessing import video_processing
from queue import Queue
import sys

if __name__ == "__main__":
	# result = subprocess.run(["libcamera-hello"])
	frame_queue = Queue(maxsize=600)
	frame_queue = video_streaming(frame_queue=frame_queue)
	video_processing(frame_queue=frame_queue)
		


