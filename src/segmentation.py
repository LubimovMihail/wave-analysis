from pathlib import Path
import pandas as pd


class Segmenter:

    def __init__(self, dataframe, threshold=1.0):
        self.df = dataframe.copy()
        self.threshold = threshold
        self.segments = []

    def split(self):

        dt = self.df["timestamp"].diff().dt.total_seconds()

        self.df["segment"] = (dt > self.threshold).cumsum()

        self.segments = [
            group.copy()
            for _, group in self.df.groupby("segment")
        ]

        return self.segments

    def summary(self):

        print("\n" + "=" * 60)
        print("SEGMENTS")
        print("=" * 60)

        for i, segment in enumerate(self.segments, start=1):

            start = segment["timestamp"].iloc[0]
            end = segment["timestamp"].iloc[-1]

            duration = end - start

            print(
                f"{i:2d} | "
                f"{len(segment):9,d} измерений | "
                f"{start} → {end} | "
                f"{duration}"
            )

    def export(self):

        out = Path("output/segments")
        out.mkdir(parents=True, exist_ok=True)

        for i, segment in enumerate(self.segments, start=1):
            segment.to_csv(
                out / f"segment_{i}.csv",
                index=False
            )

        print(f"\n✓ Сохранено {len(self.segments)} сегментов.")

    def run(self):

        self.split()

        self.summary()

        self.export()