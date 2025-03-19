import cv2
import multiprocessing
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2
import subprocess
from videoStreaming import video_streaming 
from videoProcessing import video_processing
from queue import Queue
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--sinkfile', help='Set filepath of the sinkfile jsonfile with the stone locations',required=True)
args = parser.parse_args()
sinkfile = args.sinkfile

if __name__ == "__main__":
	frame_queue = Queue(maxsize=50)
	frame_queue = video_streaming(frame_queue=frame_queue)
	video_processing(frame_queue=frame_queue, sinkfile=sinkfile)