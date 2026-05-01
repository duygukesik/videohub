import os

class Config:
    # --- Paths ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data', 'images')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
    
    # --- Image Filtering Thresholds ---
    # Darkness threshold (0-255). Images with average brightness below this are excluded.
    DARKNESS_THRESHOLD = 30
    
    # Minimum green pixel count threshold to ensure lettuce is present
    MIN_GREEN_PIXELS = 500

    # --- Color Spaces (HSV) ---
    # Define the range for green color in HSV to mask the lettuce
    # These values might need tuning depending on lighting conditions
    HSV_LOWER_GREEN = (35, 40, 40)
    HSV_UPPER_GREEN = (85, 255, 255)
    
    # --- Processing ---
    # If True, processes only a subset of images for testing purposes
    TEST_MODE = False
    TEST_SAMPLE_SIZE = 100
    
    # Image resize dimension for faster processing (optional, set to None for original size)
    # e.g., (800, 600)
    RESIZE_DIM = None

    @classmethod
    def setup_dirs(cls):
        """Ensure necessary directories exist."""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)

# Run setup on import
Config.setup_dirs()
