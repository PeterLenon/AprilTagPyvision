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

def _detect_bucket(frame):
     # returns dict of buckets as tuples
     # returns dict{
     #              bucket1: tuple(x_coordinate, y_coordinate, width, height),
     #              ...
     #              } 
     gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
     edges = cv2.Canny(blurred, 50, 150)
     contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
     MIN_SIZE = 50
     potential_buckets = dict()
     for contour in contours:
         x, y, w, h = cv2.boundingRect(contour)
         if w < MIN_SIZE or h < MIN_SIZE:
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

def _get_exif_data(frame):
    try:
        image = Image.open(frame)
        exif_data = image._getexif()
        if exif_data is None:
            logger.info("No EXIF data found in the image.")
            return None
        exif_info = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_info[tag] = value
        return exif_info 
    except Exception as e:
        logger.error(f"Error reading EXIF data: {e}")
        return None

def _get_focal_length(exif_info):
    default = 3.63
    if exif_info and 'FocalLength' in exif_info:
        focal_length = exif_info['FocalLength']
        logger.info(f"Focal Length: {focal_length} mm")
        return focal_length
    else:
        logger.info(f"Focal length not found in EXIF data. Rollback to default {default}")
        return default

def _get_photo_pixel_factor(exif_info):
     if not exif_info:
          return 25.4/640
     resolution_unit = exif_info["ResolutionUnit"]
     pixel_factor = exif_info["XResolution"]
     if resolution_unit == Unit.NO_UNIT:
        logger.warning("resolution unit is not specified")
     elif resolution_unit == Unit.INCH:
        pixel_factor = 25.4 / pixel_factor
     elif resolution_unit == Unit.CM:
         pixel_factor = 10 / pixel_factor
     return pixel_factor

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

     exif_info = _get_exif_data(frame=frame)
     pixel_factor = _get_photo_pixel_factor(exif_info=exif_info)
     focal_length = _get_focal_length(exif_info=exif_info)
     frame_height = frame.shape[0]
     frame_width = frame.shape[1]

     buckets = _detect_bucket(frame=frame)
     stones = _detect_stones(frame=frame)
     objects = dict()
     
     if buckets:
          objects['buckets'] = []
          for bucket in buckets.values():
               x , y, w, h = bucket
               cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
               depth_x = (focal_length * real_life_bucket_size) / (w * pixel_factor) 
               depth_y = (focal_length * real_life_bucket_size) / (h * pixel_factor)
               true_y_depth = (depth_x + depth_y)/2
               
               if frame_height - (y+h) >0:
                img_to_real_factor = true_y_depth / (frame_height - (y+h))

                bucket_x_center = x + (w/2)
                bucket_center_from_camera_view = bucket_x_center - (frame_width/2)
                true_x_depth = bucket_center_from_camera_view * img_to_real_factor
                objects[f"buckets"].append((true_x_depth, true_y_depth))   
     if stones:
         objects['stones'] = []
         for stone in stones.values():
             center_x , center_y , radius = stone
             cv2.circle(frame, center=(center_x, center_y), radius=radius, color=(0, 0, 255) , thickness=2)
             true_y_depth = (focal_length * real_life_stone_size) / (radius * pixel_factor)

             img_to_real_factor = true_y_depth / (frame_height - center_y - radius)
             stone_depth_from_center = center_x - (frame_width/2)
             true_x_depth = stone_depth_from_center * img_to_real_factor
             objects[f"stones"].append((true_x_depth, true_y_depth))
                 
     return objects
