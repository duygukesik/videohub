import os
import glob
import cv2
import numpy as np
from datetime import datetime
import re
from config import Config

class DataLoader:
    def __init__(self):
        self.data_dir = Config.DATA_DIR
        # Match common image formats
        self.valid_extensions = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')

    def get_image_files(self):
        """
        Scans the data directory for image files, sorts them by timestamp.
        """
        all_files = [
            os.path.join(self.data_dir, f) for f in os.listdir(self.data_dir)
            if f.lower().endswith(self.valid_extensions)
        ]
        
        # Sort files. We try to extract timestamp from filename, fallback to modification time.
        all_files.sort(key=self._extract_timestamp)
        
        if Config.TEST_MODE:
            print(f"TEST MODE: Processing only {Config.TEST_SAMPLE_SIZE} images.")
            all_files = all_files[:Config.TEST_SAMPLE_SIZE]
            
        return all_files

    def _extract_timestamp(self, filepath):
        """
        Attempts to extract a datetime object from the filename.
        Assuming formats like YYYYMMDD_HHMMSS or similar.
        Falls back to file modification time if no timestamp is found.
        """
        filename = os.path.basename(filepath)
        # Look for 14 consecutive digits (YYYYMMDDHHMMSS) or numbers separated by _/-
        match = re.search(r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})', filename)
        if match:
            try:
                return datetime(
                    int(match.group(1)), int(match.group(2)), int(match.group(3)),
                    int(match.group(4)), int(match.group(5)), int(match.group(6))
                )
            except ValueError:
                pass
        
        # Fallback to modification time
        return datetime.fromtimestamp(os.path.getmtime(filepath))

    def is_valid_image(self, image):
        """
        Filters out dark images and images without significant green content.
        """
        if image is None:
            return False

        # Convert to HSV once
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 1. Darkness Check (using V channel)
        avg_brightness = np.mean(hsv[:,:,2])
        if avg_brightness < Config.DARKNESS_THRESHOLD:
            return False

        # 2. Green Pixel Check
        mask = cv2.inRange(hsv, Config.HSV_LOWER_GREEN, Config.HSV_UPPER_GREEN)
        green_pixel_count = cv2.countNonZero(mask)
        
        if green_pixel_count < Config.MIN_GREEN_PIXELS:
            return False

        return True

    def load_images_generator(self):
        """
        Generator that yields (timestamp, valid_image) tuples.
        Useful for processing large datasets without blowing up RAM.
        """
        files = self.get_image_files()
        print(f"Found {len(files)} files to process.")
        
        for filepath in files:
            timestamp = self._extract_timestamp(filepath)
            
            # Read image
            img = cv2.imread(filepath)
            
            if img is not None and Config.RESIZE_DIM is not None:
                img = cv2.resize(img, Config.RESIZE_DIM)
                
            if self.is_valid_image(img):
                yield timestamp, img, filepath
            else:
                print(f"Skipping invalid/dark/no-lettuce image: {filepath}")

if __name__ == "__main__":
    # Simple test
    loader = DataLoader()
    files = loader.get_image_files()
    print(f"Found {len(files)} potential files.")
