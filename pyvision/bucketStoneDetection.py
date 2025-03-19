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

def _detect_bucket(frame):
    # returns dict of buckets as tuples
    # returns dict{
    #              bucket1: tuple(x_coordinate, y_coordinate, width, height),
    #              ...
    #              } 
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    lower_white = np.array([0, 0, 200]) 
    upper_white = np.array([179, 50, 255])
    
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    MIN_SIZE = 150
    potential_buckets = dict()
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w < MIN_SIZE or h < MIN_SIZE or abs(w - h) < 10:
            continue
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) >= 4 and len(approx) <= 6:
            potential_buckets[f'bucket{len(potential_buckets.keys())}'] = (x, y, w, h)
    
    return potential_buckets

def _detect_stones(frame):
     # returns dict of stones as tuples
     # returns dict{ 
     #              stone1: tuple(x_coordinate, y_coordinate, diameter),
     #              ...
     #              } 
     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     lower_purple = np.array([48, 25, 52])
     upper_purple = np.array([180, 155, 250])
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

     buckets = _detect_bucket(frame=frame)
     stones = _detect_stones(frame=frame)
     objects = dict()
     
     if buckets:
          objects['buckets'] = []
          for bucket in buckets.values():
               x , y, w, h = bucket
               depth_x = (focal_length * real_life_bucket_size) / (w * pixel_factor) 
               depth_y = (focal_length * real_life_bucket_size) / (h * pixel_factor)
               true_y_depth = (depth_x + depth_y)/2
               
               if frame_height - (y+h) > 0 and true_y_depth <= 1000 :
                   bucket_x_center = x + (w/2)
                   bucket_center_from_camera_view = bucket_x_center - (frame_width/2)
                   angle = (bucket_center_from_camera_view * view_angle_per_ppx) + 60
                   cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                   cv2.imshow("detected bucket", frame)
                   cv2.waitKey(1)
                   objects[f"buckets"].append((angle, true_y_depth))

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
