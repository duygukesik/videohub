import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from config import Config

class Visualizer:
    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
        # Set seaborn style for better aesthetics
        sns.set_theme(style="whitegrid", context="talk")

    def plot_time_series(self, df, column, title, ylabel, filename):
        """
        Plots a single time-series metric and saves it.
        """
        if df.empty or column not in df.columns:
            print(f"Skipping plot {title}: No data available.")
            return

        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x=df.index, y=column, marker="o" if len(df) < 100 else None, color="#2ecc71", linewidth=2.5)
        
        plt.title(title, fontsize=18, fontweight='bold', pad=15)
        plt.xlabel("Tarih / Saat", fontsize=14)
        plt.ylabel(ylabel, fontsize=14)
        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved plot: {save_path}")

    def plot_comparison(self, df_hourly, df_5min, column, title, ylabel, filename):
        """
        Plots the original hourly data and the interpolated 5-minute data together.
        """
        if df_hourly.empty or df_5min.empty or column not in df_hourly.columns:
            return

        plt.figure(figsize=(14, 7))
        
        # Plot interpolated data as a smooth line
        sns.lineplot(data=df_5min, x=df_5min.index, y=column, color="#3498db", label="Tahmin (5 Dakika Interpolasyon)", linewidth=2, alpha=0.8)
        
        # Plot original hourly data as distinct points
        sns.scatterplot(data=df_hourly, x=df_hourly.index, y=column, color="#e74c3c", label="Gerçek Veri (Saatlik)", s=80, zorder=5)
        
        plt.title(title, fontsize=18, fontweight='bold', pad=15)
        plt.xlabel("Tarih / Saat", fontsize=14)
        plt.ylabel(ylabel, fontsize=14)
        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.legend()
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved comparison plot: {save_path}")
