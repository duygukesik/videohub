import os
import cv2
import pandas as pd
from config import Config
from data_loader import DataLoader
from image_processing import ImageProcessor
from feature_extraction import FeatureExtractor
from analysis import DataAnalyzer
from visualization import Visualizer

def main():
    print("Starting Lettuce Growth Simulation Analysis Pipeline...")
    
    # Initialize modules
    data_loader = DataLoader()
    img_processor = ImageProcessor()
    feature_extractor = FeatureExtractor()
    analyzer = DataAnalyzer()
    visualizer = Visualizer()
    
    records = []
    
    print("\n--- Step 1 & 2 & 3: Loading, Processing, and Extraction ---")
    # Process images using generator to save memory
    for timestamp, img, filepath in data_loader.load_images_generator():
        
        # 1. Get green mask for the whole image
        full_mask = img_processor.get_green_mask(img)
        
        # 2. Find the reference lettuce (closest to center)
        ref_contour, ref_bbox = img_processor.find_reference_lettuce(full_mask)
        
        if ref_contour is None or ref_bbox is None:
            print(f"Skipping {filepath}: No valid central lettuce found.")
            continue
            
        # 3. Extract ROI for the reference lettuce
        roi_img = img_processor.get_lettuce_roi(img, ref_bbox)
        roi_mask = img_processor.get_lettuce_mask_roi(full_mask, ref_bbox)
        
        # Optional: Save a debug image showing the bounded box for the first valid image
        if len(records) == 0:
            debug_img = img.copy()
            x, y, w, h = ref_bbox
            cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.imwrite(os.path.join(Config.OUTPUT_DIR, "debug_center_lettuce.jpg"), debug_img)
            print("Saved debug center lettuce image.")

        # 4. Extract features
        features = feature_extractor.extract_features(roi_img, roi_mask)
        if features:
            features['timestamp'] = timestamp
            features['plant_id'] = 'plant_01'
            features['filename'] = os.path.basename(filepath)
            records.append(features)
            
    print(f"\nSuccessfully processed {len(records)} valid images.")
    
    if not records:
        print("No valid records found. Exiting.")
        return
        
    print("\n--- Step 4: Analysis & DataFrame Creation ---")
    df_hourly = analyzer.create_dataframe(records)
    
    # Calculate initial hourly growth rate
    df_hourly = analyzer.calculate_growth_rate(df_hourly)
    
    # Save raw hourly data
    csv_path = os.path.join(Config.OUTPUT_DIR, "lettuce_hourly_data.csv")
    df_hourly.to_csv(csv_path, float_format='%.4f')
    print(f"Saved hourly data to {csv_path}")

    print("\n--- Step 5: Time Series Interpolation (5-Min) ---")
    try:
        df_5min = analyzer.interpolate_5min(df_hourly)
        
        # Save interpolated data
        csv_5min_path = os.path.join(Config.OUTPUT_DIR, "lettuce_5min_interpolated_data.csv")
        df_5min.to_csv(csv_5min_path, float_format='%.4f')
        print(f"Saved 5-min interpolated data to {csv_5min_path}")
        
        # Save exact Parquet format requested by user
        parquet_path = os.path.join(Config.OUTPUT_DIR, "cv_features.parquet")
        df_parquet = df_5min.reset_index()
        # Ensure only the exact requested columns are included
        cols_to_keep = ['timestamp', 'plant_id', 'leaf_area_px', 'green_index']
        df_parquet = df_parquet[[c for c in cols_to_keep if c in df_parquet.columns]]
        df_parquet.to_parquet(parquet_path, index=False)
        print(f"Saved required Parquet format to {parquet_path}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Interpolation/Parquet failed: {e}")
        df_5min = pd.DataFrame()

    print("\n--- Step 6: Visualization ---")
    # Hourly Plots
    visualizer.plot_time_series(df_hourly, 'leaf_area_px', 'Saatlik Yaprak Alanı Gelişimi', 'Alan (Piksel)', 'hourly_leaf_area.png')
    visualizer.plot_time_series(df_hourly, 'green_index', 'Saatlik Yeşil Renk Yoğunluğu', 'Yoğunluk (0-255)', 'hourly_green_intensity.png')
    visualizer.plot_time_series(df_hourly, 'growth_rate_abs', 'Saatlik Büyüme Hızı', 'Alan Farkı (Piksel)', 'hourly_growth_rate.png')
    
    # Comparison Plots (Hourly vs 5-Min)
    if not df_5min.empty:
        visualizer.plot_comparison(df_hourly, df_5min, 'leaf_area_px', 'Yaprak Alanı: Saatlik vs 5-Dakika Tahmin', 'Alan (Piksel)', 'comparison_leaf_area.png')
        visualizer.plot_comparison(df_hourly, df_5min, 'green_index', 'Yeşil Renk Yoğunluğu: Saatlik vs 5-Dakika Tahmin', 'Yoğunluk (0-255)', 'comparison_green_intensity.png')
        visualizer.plot_comparison(df_hourly, df_5min, 'growth_rate_abs', 'Büyüme Hızı (Mutlak Değişim)', 'Alan Farkı (Piksel)', 'comparison_growth_rate.png')
    
    print("\nPipeline Execution Complete!")

if __name__ == "__main__":
    main()
