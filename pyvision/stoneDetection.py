import cv2
from loguru import logger
import numpy as np
from picamera2 import Picamera2
from PIL import Image
from PIL.ExifTags import TAGS
from enum import Enum

class Unit(Enum):
    NO_UNIT = 1
    INCH = 2
    CM = 3
    MM = 4

def _detect_stones(frame):
     # returns dict of stones as tuples
     # returns dict{ 
     #              stone1: tuple(x_coordinate, y_coordinate, diameter),
     #              ...
     #              } 
     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     lower_purple = np.array([120, 50, 50])
     upper_purple = np.array([150, 255, 255])
     mask = cv2.inRange(hsv, lower_purple, upper_purple)
     contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
     potential_stones = dict()
     for contour in contours:
         epsilon = 0.01 * cv2.arcLength(contour, True)
         approx = cv2.approxPolyDP(contour, epsilon, True)
         if len(approx) < 6:
             continue
         (center_x, center_y) , radius = cv2.minEnclosingCircle(contour)
         center_x = int(center_x)
         center_y = int(center_y)
         radius = int(radius)
         potential_stones[f"stone{len(potential_stones.keys())}"] = (center_x, center_y, radius)
     return potential_stones

def getPos(frame):
     # returns dict{ 
     #              buckets: list[ 
     #                             tuple(depth_x, depth_y), 
     #                             ...
     #                            ],  
     #              stones: list[ tuple(depth_x, depth_y), 
     #                             ...
     #                             ]
     #              }
     inch_to_mm = 25.4
     real_life_bucket_size = 6 * inch_to_mm
     real_life_stone_size = 2 * inch_to_mm
     
     frame_height = frame.shape[0]
     frame_width = frame.shape[1]
     pixel_factor = 25.4/frame_height               # get mm per pixel
     focal_length = 3.6                             # focal length of pi camera is 3.6 mm
   
     approx_view_angle = 60
     view_angle_per_ppx = approx_view_angle/frame_width

     stones = _detect_stones(frame=frame)
     objects = dict()
     
     if stones:
         objects['stones'] = []
         for stone in stones.values():
             center_x , center_y , radius = stone
             if radius < 50:
                 continue
             cv2.circle(frame, (int(center_x), int(center_y)), int(radius), (0, 0, 255), 2)
             cv2.imshow("detected stones", frame)
             cv2.waitKey(1)
             true_y_depth = (focal_length * real_life_stone_size) / (radius * pixel_factor)

             if frame_height - center_y - radius != 0 and true_y_depth <= 400:   
                stone_depth_from_center = center_x - (frame_width/2)
                angle = (stone_depth_from_center * view_angle_per_ppx) + 60
                objects[f"stones"].append((angle, true_y_depth))

     return objects