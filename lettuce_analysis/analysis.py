import pandas as pd
import numpy as np
from scipy import interpolate

class DataAnalyzer:
    def __init__(self):
        pass

    def create_dataframe(self, records):
        """
        Converts a list of dictionary records to a Pandas DataFrame.
        Sets 'timestamp' as the datetime index.
        """
        if not records:
            return pd.DataFrame()
            
        df = pd.DataFrame(records)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Round the original timestamps to the nearest 5 minutes
        df['timestamp'] = df['timestamp'].dt.round('5min')
        df = df.sort_values(by='timestamp')
        
        # Prevent ValueError: cannot reindex on an axis with duplicate labels
        df = df.drop_duplicates(subset=['timestamp'], keep='first')
        
        df = df.set_index('timestamp')
        
        return df

    def calculate_growth_rate(self, df, window=1):
        """
        Calculates the growth rate of leaf area compared to 'window' hours ago.
        Since data is hourly, diff(1) means difference from previous hour.
        """
        if df.empty:
            return df
            
        # Calculate absolute growth
        df['growth_rate_abs'] = df['leaf_area_px'].diff(periods=window)
        
        # Calculate percentage growth
        # Handle division by zero
        previous_area = df['leaf_area_px'].shift(window)
        df['growth_rate_pct'] = np.where(previous_area > 0, 
                                        (df['growth_rate_abs'] / previous_area) * 100, 
                                        0)
        return df

    def interpolate_5min(self, df):
        """
        Interpolates the hourly data into 5-minute intervals.
        """
        if df.empty or len(df) < 2:
            return df
            
        # Preserve plant_id before resampling as string columns get dropped
        plant_id = df['plant_id'].iloc[0] if 'plant_id' in df.columns else 'plant_01'
        
        # Resample to 5-minute intervals
        # 'AS' means start of the interval. We create empty rows for 5min gaps
        df_resampled = df.resample('5min').asfreq()
        
        # Perform spline or polynomial interpolation for smooth curves
        # 'pchip' (Piecewise Cubic Hermite Interpolating Polynomial) 
        # is often good for monotonic growth to prevent overshooting
        
        for col in ['leaf_area_px', 'green_index', 'brightness_value']:
            if col in df_resampled.columns:
                df_resampled[col] = df_resampled[col].interpolate(method='pchip')
                
        # Drop rows where interpolation wasn't possible (e.g. edges)
        df_resampled = df_resampled.dropna(subset=['leaf_area_px'])
        
        # Add the string columns back
        df_resampled['plant_id'] = plant_id
        
        # Re-calculate growth rate on the 5-min data if needed
        # (Difference between current 5-min and previous 5-min)
        df_resampled = self.calculate_growth_rate(df_resampled)
        
        return df_resampled
