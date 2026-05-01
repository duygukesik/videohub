import cv2
import numpy as np

class FeatureExtractor:
    def __init__(self):
        pass

    def extract_features(self, roi_image, roi_mask):
        """
        Extracts morphological and color features from the lettuce ROI.
        """
        if roi_image is None or roi_mask is None:
            return None

        # 1. Leaf Area (Number of green pixels)
        leaf_area_pixels = cv2.countNonZero(roi_mask)
        
        # 2. Green Color Intensity
        # Extract the green channel and apply mask
        # OpenCV uses BGR format
        green_channel = roi_image[:, :, 1]
        
        # Calculate average green intensity using numpy boolean indexing
        if leaf_area_pixels > 0:
            mask_bool = roi_mask > 0
            mean_green_intensity = float(np.mean(green_channel[mask_bool]))
        else:
            mean_green_intensity = 0.0
            
        # Alternative: average HSV Hue or Value
        hsv_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
        v_channel = hsv_roi[:, :, 2]
        
        if leaf_area_pixels > 0:
            mean_brightness = float(np.mean(v_channel[mask_bool]))
        else:
            mean_brightness = 0.0

        return {
            'leaf_area': leaf_area_pixels,
            'green_intensity': mean_green_intensity,
            'brightness_value': mean_brightness
        }
