# src/wave_analysis.py

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class WaveAnalysis:

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        self.output = Path("output/figures")
        self.output.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------

    def prepare_signal(self):

        print()
        print("=" * 60)
        print("WAVE ANALYSIS")
        print("=" * 60)

        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])

        self.df = (
            self.df
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        print()

        print("Количество измерений :", f"{len(self.df):,}")

        print("Начало записи        :", self.df.timestamp.iloc[0])

        print("Конец записи         :", self.df.timestamp.iloc[-1])

        print(
            "Продолжительность    :",
            self.df.timestamp.iloc[-1] - self.df.timestamp.iloc[0]
        )

    # --------------------------------------------------------

    def pressure_statistics(self):

        print()
        print("=" * 60)
        print("PRESSURE STATISTICS")
        print("=" * 60)

        print()

        print(self.df["pressure"].describe())

    # --------------------------------------------------------

    def full_pressure_plot(self):

        print()
        print("Построение полного графика давления...")

        plt.figure(figsize=(15,5))

        plt.plot(
            self.df["timestamp"],
            self.df["pressure"],
            lw=0.5
        )

        plt.title("Давление за период наблюдений")

        plt.xlabel("Время")

        plt.ylabel("Давление (дбар)")

        plt.grid(True)

        plt.tight_layout()

        plt.savefig(
            self.output / "pressure_full.png",
            dpi=300
        )

        plt.close()

        print("✓ pressure_full.png")

    # --------------------------------------------------------

    def zoom_pressure_plot(self, minutes=20):

        print()
        print(f"Построение участка {minutes} минут...")

        start = len(self.df) // 2

        fs = 4

        count = minutes * 60 * fs

        sample = self.df.iloc[start:start + count]

        plt.figure(figsize=(15,5))

        plt.plot(
            sample["timestamp"],
            sample["pressure"],
            lw=1
        )

        plt.title(
            f"Давление ({minutes} мин)"
        )

        plt.xlabel("Время")

        plt.ylabel("Давление (дбар)")

        plt.grid(True)

        plt.tight_layout()

        plt.savefig(
            self.output / "pressure_zoom.png",
            dpi=300
        )

        plt.close()

        print("✓ pressure_zoom.png")

    # --------------------------------------------------------

    def wave_pressure_statistics(self):

        if "wave_pressure" not in self.df.columns:
            return

        print()

        print("=" * 60)
        print("WAVE PRESSURE")
        print("=" * 60)

        print()

        print(self.df["wave_pressure"].describe())

    # --------------------------------------------------------

    def wave_pressure_plot(self, minutes=20):

        if "wave_pressure" not in self.df.columns:
            return

        print()

        print("Построение сигнала волн...")

        start = len(self.df) // 2

        fs = 4

        count = minutes * 60 * fs

        sample = self.df.iloc[start:start + count]

        plt.figure(figsize=(15,5))

        plt.plot(
            sample["timestamp"],
            sample["wave_pressure"],
            lw=1
        )

        plt.title("Волновое давление")

        plt.xlabel("Время")

        plt.ylabel("Аномалия давления (дбар)")

        plt.grid(True)

        plt.tight_layout()

        plt.savefig(
            self.output / "wave_pressure_zoom.png",
            dpi=300
        )

        plt.close()

        print("✓ wave_pressure_zoom.png")

    # --------------------------------------------------------

    def save_wave_data(self):

        if "wave_pressure" not in self.df.columns:
            return

        wave = self.df[
            [
                "timestamp",
                "wave_pressure"
            ]
        ]

        wave.to_csv(
            "output/wave_signal.csv",
            index=False
        )

        print()
        print("✓ wave_signal.csv сохранён")

    # --------------------------------------------------------

    def run(self):

        self.prepare_signal()

        self.pressure_statistics()

        self.full_pressure_plot()

        self.zoom_pressure_plot()

        self.wave_pressure_statistics()

        self.wave_pressure_plot()

        self.save_wave_data()