from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class TemperatureAnalysis:

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        self.output_fig = Path("output/figures")
        self.output_tab = Path("output/tables")

        self.output_fig.mkdir(parents=True, exist_ok=True)
        self.output_tab.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------

    def statistics(self):

        stats = self.df["temperature"].describe()

        stats.to_csv(
            self.output_tab / "temperature_statistics.csv"
        )

        print("\n" + "=" * 60)
        print("TEMPERATURE STATISTICS")
        print("=" * 60)
        print(f"Минимум : {self.df['temperature'].min():.2f} °C")
        print(f"Максимум: {self.df['temperature'].max():.2f} °C")
        print(f"Средняя : {self.df['temperature'].mean():.2f} °C")
        print(f"Медиана : {self.df['temperature'].median():.2f} °C")
        print(f"σ       : {self.df['temperature'].std():.2f} °C")
        print(f"Размах  : {(self.df['temperature'].max()-self.df['temperature'].min()):.2f} °C")

        print(stats)

    # --------------------------------------------------------

    def full_plot(self):

        plt.figure(figsize=(16,5))

        plt.plot(
            self.df["timestamp"],
            self.df["temperature"],
            linewidth=0.4
        )

        plt.title("Temperature during deployment")

        plt.xlabel("Time")

        plt.ylabel("Temperature (°C)")

        plt.tight_layout()

        plt.savefig(
            self.output_fig / "temperature_full.png",
            dpi=300
        )

        plt.close()

        print("✓ temperature_full.png")

    # --------------------------------------------------------

    def hourly_plot(self):

        hourly = (
            self.df
            .set_index("timestamp")
            .resample("1h")
            .mean(numeric_only=True)
        )

        plt.figure(figsize=(16,5))

        plt.plot(
            hourly.index,
            hourly["temperature"],
            linewidth=2
        )

        plt.title("Hourly averaged temperature")

        plt.xlabel("Time")

        plt.ylabel("Temperature (°C)")

        plt.tight_layout()

        plt.savefig(
            self.output_fig / "temperature_hourly.png",
            dpi=300
        )

        plt.close()

        hourly.to_csv(
            self.output_tab / "temperature_hourly.csv"
        )

        print("✓ temperature_hourly.png")

    # --------------------------------------------------------

    def histogram(self):

        plt.figure(figsize=(8,5))

        plt.hist(
            self.df["temperature"],
            bins=40
        )

        plt.xlabel("Temperature (°C)")

        plt.ylabel("Count")

        plt.title("Temperature distribution")

        plt.tight_layout()

        plt.savefig(
            self.output_fig / "temperature_histogram.png",
            dpi=300
        )

        plt.close()

        print("✓ temperature_histogram.png")

    # --------------------------------------------------------

    def boxplot(self):

        plt.figure(figsize=(4,6))

        plt.boxplot(
            self.df["temperature"],
            vert=True,
            tick_labels=["Whole deployment"]
        )

        plt.ylabel("Temperature (°C)")

        plt.title("Temperature distribution")

        plt.tight_layout()

        plt.savefig(
            self.output_fig / "temperature_boxplot.png",
            dpi=300
        )

        plt.close()

        print("✓ temperature_boxplot.png")

    # --------------------------------------------------------

    def daily_cycle(self):

        tmp = self.df.copy()

        tmp["hour"] = tmp["timestamp"].dt.hour

        cycle = (
            tmp
            .groupby("hour")
            ["temperature"]
            .mean()
        )

        plt.figure(figsize=(10,5))

        plt.plot(
            cycle.index,
            cycle.values,
            marker="o"
        )

        plt.xticks(range(24))

        plt.xlabel("Hour")

        plt.ylabel("Temperature (°C)")

        plt.title("Mean daily cycle")

        plt.grid(True)

        plt.tight_layout()

        plt.savefig(
            self.output_fig / "temperature_daily_cycle.png",
            dpi=300
        )

        plt.close()

        cycle.to_csv(
            self.output_tab / "temperature_daily_cycle.csv"
        )

        print("✓ temperature_daily_cycle.png")

    # --------------------------------------------------------

    def gradient(self):

        tmp = self.df.copy()

        tmp["dT"] = tmp["temperature"].diff()

        plt.figure(figsize=(16,4))

        plt.plot(
            tmp["timestamp"],
            tmp["dT"],
            linewidth=0.4
        )

        plt.title("Temperature gradient")

        plt.xlabel("Time")

        plt.ylabel("ΔT between samples (°C)")

        plt.tight_layout()

        plt.savefig(
            self.output_fig / "temperature_gradient.png",
            dpi=300
        )

        plt.close()

        print("✓ temperature_gradient.png")

    # --------------------------------------------------------

    def run(self):

        self.statistics()

        self.full_plot()

        self.hourly_plot()

        self.histogram()

        self.boxplot()

        self.daily_cycle()

        self.gradient()