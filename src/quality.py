from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class QualityControl:

    def __init__(self, dataframe: pd.DataFrame):

        self.df = dataframe.copy()

    def basic_statistics(self):

        print("\n" + "=" * 60)
        print("QUALITY CONTROL")
        print("=" * 60)

        print(f"Количество измерений : {len(self.df):,}")

        print(f"Количество столбцов  : {len(self.df.columns)}")

        print(f"Начало записи        : {self.df.timestamp.min()}")

        print(f"Конец записи         : {self.df.timestamp.max()}")

        duration = (
            self.df.timestamp.max()
            - self.df.timestamp.min()
        )

        print(f"Продолжительность    : {duration}")

    def check_duplicates(self):

        duplicates = self.df.duplicated().sum()

        print(f"\nДубликатов : {duplicates}")

    def check_missing(self):

        print("\nПропущенные значения")

        print(self.df.isna().sum())

    def statistics(self):

        print("\nСтатистика")

        print(self.df.describe())

    def plot_temperature(self):

        Path("output/figures").mkdir(
            parents=True,
            exist_ok=True
        )

        plt.figure(figsize=(16,5))

        plt.plot(
            self.df["timestamp"],
            self.df["temperature"],
            linewidth=0.3
        )

        plt.title("Температура")

        plt.xlabel("Время")

        plt.ylabel("Температура (°C)")

        plt.tight_layout()

        plt.savefig(
            "output/figures/temperature_timeseries.png",
            dpi=300
        )

        plt.close()

    def plot_pressure(self):

        plt.figure(figsize=(16,5))

        plt.plot(
            self.df["timestamp"],
            self.df["pressure"],
            linewidth=0.3
        )

        plt.title("Давление")

        plt.xlabel("Время")

        plt.ylabel("Давление (дбар)")

        plt.tight_layout()

        plt.savefig(
            "output/figures/pressure_timeseries.png",
            dpi=300
        )

        plt.close()

    def run(self):

        self.basic_statistics()

        self.check_duplicates()

        self.check_missing()

        self.statistics()

        self.plot_temperature()

        self.plot_pressure()

        print("\n✓ Контроль качества завершён.")