from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class WavePreprocessor:

    def __init__(self, dataframe):

        self.df = dataframe.copy()

    def compute_trend(self):

        print("\nВычисление медленного тренда...")

        window = 10 * 60 * 4      # 10 минут при 4 Гц

        self.df["trend"] = (
            self.df["pressure"]
            .rolling(
                window=window,
                center=True,
                min_periods=1
            )
            .mean()
        )

        self.df["wave_pressure"] = (
            self.df["pressure"]
            -
            self.df["trend"]
        )

        print("✓ Тренд вычислен.")

    def plot(self):

        Path("output/figures").mkdir(
            parents=True,
            exist_ok=True
        )

        # Берем участок далеко после установки прибора

        start = 500000

        window = 20 * 60 * 4

        sample = self.df.iloc[start:start + window]

        # ----------------------------

        plt.figure(figsize=(15,5))

        plt.plot(
            sample["timestamp"],
            sample["pressure"],
            label="Pressure"
        )

        plt.plot(
            sample["timestamp"],
            sample["trend"],
            linewidth=2,
            label="Trend"
        )

        plt.title("Pressure and slow (10-minute) trend")

        plt.xlabel("Time")

        plt.ylabel("Pressure (dbar)")

        plt.legend()

        plt.tight_layout()

        plt.savefig(
            "output/figures/pressure_and_trend.png",
            dpi=300
        )

        plt.close()

        # ----------------------------

        plt.figure(figsize=(15,5))

        plt.plot(
            sample["timestamp"],
            sample["wave_pressure"]
        )

        plt.title("Wave pressure (trend removed)")

        plt.xlabel("Time")

        plt.ylabel("Pressure anomaly (dbar)")

        plt.tight_layout()

        plt.savefig(
            "output/figures/wave_pressure.png",
            dpi=300
        )

        plt.close()

        print("✓ Графики сохранены.")

    def statistics(self):

        print("\n" + "=" * 60)
        print("WAVE PRESSURE")
        print("=" * 60)

        print(self.df["wave_pressure"].describe())

    def run(self):

        self.compute_trend()

        self.statistics()

        self.plot()