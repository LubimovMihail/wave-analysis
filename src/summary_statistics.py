from pathlib import Path

import pandas as pd


class SummaryStatistics:

    """
    Final statistical summary
    of the whole project.
    """

    # =====================================================

    def __init__(
        self,
        reader,
        spectra,
        storm,
        wind
    ):

        self.reader = reader
        self.spectra = spectra
        self.storm = storm
        self.wind = wind

        self.output = Path(
            "output/tables"
        )

        self.output.mkdir(
            parents=True,
            exist_ok=True
        )

        self.table = None

    # =====================================================

    def build_table(self):

        df = self.reader.df

        duration_days = (

            (
                df["timestamp"].iloc[-1]
                -
                df["timestamp"].iloc[0]
            )

            .total_seconds()

            / 86400

        )

        rows = [

            {
                "Parameter":
                    "Observation period (days)",
                "Value":
                    round(duration_days, 2)
            },

            {
                "Parameter":
                    "Measurements",
                "Value":
                    len(df)
            },

            {
                "Parameter":
                    "Sampling frequency (Hz)",
                "Value":
                    round(
                        self.spectra.fs,
                        3
                    )
            },

            {
                "Parameter":
                    "Mean pressure (dbar)",
                "Value":
                    round(
                        df["pressure"].mean(),
                        4
                    )
            },

            {
                "Parameter":
                    "Mean wave energy",
                "Value":
                    self.spectra.statistics_table[
                        "energy"
                    ].mean()
            },

            {
                "Parameter":
                    "Maximum wave energy",
                "Value":
                    self.spectra.statistics_table[
                        "energy"
                    ].max()
            },

            {
                "Parameter":
                    "Dominant period (s)",
                "Value":
                    self.spectra.tp
            },

            {
                "Parameter":
                    "Dominant frequency (Hz)",
                "Value":
                    self.spectra.fp
            },

            {
                "Parameter":
                    "Detected storms",
                "Value":
                    len(
                        self.storm.events_table
                    )
            },

            {
                "Parameter":
                    "Longest storm (hours)",
                "Value":
                    self.storm.events_table[
                        "duration_hours"
                    ].max()
            },

            {
                "Parameter":
                    "Mean wind speed (m/s)",
                "Value":
                    self.wind.data[
                        "wind_speed"
                    ].mean()
            },

            {
                "Parameter":
                    "Maximum wind speed (m/s)",
                "Value":
                    self.wind.data[
                        "wind_speed"
                    ].max()
            },

            {
                "Parameter":
                    "Pearson correlation",
                "Value":
                    self.wind.correlation[
                        "pearson"
                    ]
            },

            {
                "Parameter":
                    "Spearman correlation",
                "Value":
                    self.wind.correlation[
                        "spearman"
                    ]
            }

        ]

        self.table = pd.DataFrame(
            rows
        )

    # =====================================================

    def print_summary(self):

        print()
        print("=" * 60)
        print("SUMMARY STATISTICS")
        print("=" * 60)
        print()

        print(self.table)

    # =====================================================

    def save(self):

        self.table.to_csv(

            self.output /
            "summary_statistics.csv",

            index=False

        )

        print()
        print(
            "✓ summary_statistics.csv"
        )

    # =====================================================

    def run(self):

        self.build_table()

        self.print_summary()

        self.save()