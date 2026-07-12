import pandas as pd


class GapDetector:

    def __init__(self, dataframe):

        self.df = dataframe.copy()

    def find_gaps(self, threshold=1.0):
        """
        Ищет все разрывы временного ряда.

        threshold — минимальная длительность разрыва (сек).
        """

        dt = self.df["timestamp"].diff().dt.total_seconds()

        gaps = self.df.loc[dt > threshold].copy()

        gaps["gap_seconds"] = dt[dt > threshold]

        return gaps

    def report(self):

        gaps = self.find_gaps()

        print("\n" + "=" * 60)
        print("GAP DETECTION")
        print("=" * 60)

        if gaps.empty:

            print("\nРазрывов не обнаружено.")

            return

        print(f"\nНайдено разрывов: {len(gaps)}\n")

        for i, (_, row) in enumerate(gaps.iterrows(), start=1):

            print(f"Разрыв {i}")

            print(f"Время после разрыва : {row['timestamp']}")

            print(f"Длительность         : {row['gap_seconds']:.3f} сек")

            print("-" * 40)

    def export(self):

        gaps = self.find_gaps()

        gaps.to_csv(
            "output/tables/gaps.csv",
            index=False
        )

        print("\n✓ Таблица разрывов сохранена.")

    def run(self):

        self.report()

        self.export()