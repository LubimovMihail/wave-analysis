from pathlib import Path

import pandas as pd


class DataCleaner:

    def __init__(self, segments):

        self.segments = segments

        self.clean_df = None

    def clean(
        self,
        min_samples=2400,
        trim_minutes=5,
        sampling_rate=4,
        pressure_margin=2.0,
    ):

        trim = trim_minutes * 60 * sampling_rate

        valid = []

        removed_short = 0
        removed_trim = 0

        print("\n" + "=" * 60)
        print("DATA CLEANING")
        print("=" * 60)

        for i, segment in enumerate(self.segments, start=1):

            if len(segment) < min_samples:

                removed_short += len(segment)

                print(f"Сегмент {i}: удалён (слишком короткий)")

                continue

            if len(segment) <= 2 * trim:

                removed_short += len(segment)

                print(f"Сегмент {i}: удалён (недостаточно длинный после обрезки)")

                continue

            cleaned = segment.iloc[trim:-trim].copy()

            removed_trim += len(segment) - len(cleaned)

            print(
                f"Сегмент {i}: "
                f"{len(segment):,} → {len(cleaned):,}"
            )

            valid.append(cleaned)

        self.clean_df = pd.concat(
            valid,
            ignore_index=True
        )

        print("\nУдалено коротких записей :", removed_short)
        print("Удалено при обрезке      :", removed_trim)
        print("Осталось после обрезки   :", len(self.clean_df))

        # -------------------------------------------------------
        # Instrument-recovery / out-of-water artifact removal.
        # When the logger is hauled out of the water (deployment
        # start/end, mid-deployment checks), pressure drops to
        # near-atmospheric — several dbar below the normal
        # underwater reading. These samples are not real wave/tide
        # data and, if left in, get mistaken for storms with
        # absurd (near-zero-frequency) peak periods downstream.
        # -------------------------------------------------------

        removed_out_of_water = 0

        if "pressure" in self.clean_df.columns and len(self.clean_df) > 0:

            median_pressure = self.clean_df["pressure"].median()

            pressure_threshold = median_pressure - pressure_margin

            out_of_water = self.clean_df["pressure"] < pressure_threshold

            removed_out_of_water = int(out_of_water.sum())

            self.clean_df = (
                self.clean_df
                .loc[~out_of_water]
                .reset_index(drop=True)
            )

            print(
                f"Удалено (прибор не в воде, "
                f"pressure < {pressure_threshold:.2f} dbar) : "
                f"{removed_out_of_water}"
            )

        print("Итого осталось           :", len(self.clean_df))

    def save(self):

        Path("data/processed").mkdir(
            parents=True,
            exist_ok=True
        )

        self.clean_df.to_csv(
            "data/processed/clean_data.csv",
            index=False
        )

        print("\n✓ clean_data.csv сохранён.")

    def summary(self):

        print("\n" + "=" * 60)
        print("CLEAN DATA")
        print("=" * 60)

        print(self.clean_df.head())

        print()

        print(self.clean_df.describe())

    def run(self):

        self.clean()

        self.summary()

        self.save()