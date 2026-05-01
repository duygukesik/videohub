import cv2
import numpy as np
from config import Config

class ImageProcessor:
    def __init__(self):
        pass

    def get_green_mask(self, image):
        """
        Creates a binary mask isolating the green parts of the image.
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Apply slight blur to reduce noise
        hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
        mask = cv2.inRange(hsv, Config.HSV_LOWER_GREEN, Config.HSV_UPPER_GREEN)
        
        # Morphological operations to clean up small noise
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        return mask

    def find_reference_lettuce(self, mask):
        """
        Finds the contour of the lettuce closest to the center of the image.
        Returns the selected contour and its bounding box.
        """
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, None
            
        h, w = mask.shape
        image_center = (w // 2, h // 2)
        
        min_dist = float('inf')
        reference_contour = None
        ref_bbox = None
        
        for contour in contours:
            # Filter out very small contours
            if cv2.contourArea(contour) < Config.MIN_GREEN_PIXELS:
                continue
                
            # Calculate moments to find the center of the contour
            M = cv2.moments(contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
            else:
                continue
                
            # Calculate Euclidean distance to image center
            dist = np.sqrt((cx - image_center[0])**2 + (cy - image_center[1])**2)
            
            if dist < min_dist:
                min_dist = dist
                reference_contour = contour
                ref_bbox = cv2.boundingRect(contour) # x, y, w, h
                
        return reference_contour, ref_bbox

    def get_lettuce_roi(self, image, bbox):
        """
        Extracts the Region of Interest (ROI) containing the reference lettuce.
        """
        if bbox is None:
            return None
            
        x, y, w, h = bbox
        return image[y:y+h, x:x+w]
        
    def get_lettuce_mask_roi(self, mask, bbox):
        """
        Extracts the Region of Interest (ROI) from the mask.
        """
        if bbox is None:
            return None
            
        x, y, w, h = bbox
        return mask[y:y+h, x:x+w]
