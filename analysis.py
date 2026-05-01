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
        df = df.sort_values(by='timestamp')
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
        df['growth_rate_abs'] = df['leaf_area'].diff(periods=window)
        
        # Calculate percentage growth
        # Handle division by zero
        previous_area = df['leaf_area'].shift(window)
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
            
        # Resample to 5-minute intervals
        # 'AS' means start of the interval. We create empty rows for 5min gaps
        df_resampled = df.resample('5min').asfreq()
        
        # Perform spline or polynomial interpolation for smooth curves
        # 'pchip' (Piecewise Cubic Hermite Interpolating Polynomial) 
        # is often good for monotonic growth to prevent overshooting
        
        for col in ['leaf_area', 'green_intensity', 'brightness_value']:
            if col in df_resampled.columns:
                df_resampled[col] = df_resampled[col].interpolate(method='pchip')
                
        # Drop rows where interpolation wasn't possible (e.g. edges)
        df_resampled = df_resampled.dropna()
        
        # Re-calculate growth rate on the 5-min data if needed
        # (Difference between current 5-min and previous 5-min)
        df_resampled = self.calculate_growth_rate(df_resampled)
        
        return df_resampled
