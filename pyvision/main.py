import cv2
import numpy as np
from apriltag import apriltag
from picamera2 import Picamera2
from videoStreaming import video_streaming 
from videoProcessing import video_processing
from queue import Queue
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--sinkfile', required=True, help='Set filepath of the sinkfile jsonfile with the stone locations')
parser.add_argument('--frames', required=False, help="set the amount of frames the camera takes for processing. The lower the number the faster the process completes")
args = parser.parse_args()
sinkfile = args.sinkfile
frames = args.frames

if __name__ == "__main__":
	frame_queue = Queue(maxsize=frames if frames else 30)
	frame_queue = video_streaming(frame_queue=frame_queue)
	video_processing(frame_queue=frame_queue, sinkfile=sinkfile)