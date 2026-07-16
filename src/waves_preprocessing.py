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
            label="Давление"
        )

        plt.plot(
            sample["timestamp"],
            sample["trend"],
            linewidth=2,
            label="Тренд"
        )

        plt.title("Давление и медленный (10-минутный) тренд")

        plt.xlabel("Время")

        plt.ylabel("Давление (дбар)")

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

        plt.title("Волновое давление (без тренда)")

        plt.xlabel("Время")

        plt.ylabel("Аномалия давления (дбар)")

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