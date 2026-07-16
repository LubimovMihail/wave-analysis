from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class StormAnalysis:
    """
    Detection and analysis of storm events
    from wave-energy time series.
    """

    # =====================================================

    def __init__(self, spectra):

        self.spectra = spectra

        self.statistics = pd.DataFrame(
            spectra.statistics
        )

        self.output_fig = Path(
            "output/figures"
        )

        self.output_tab = Path(
            "output/tables"
        )

        self.output_fig.mkdir(
            parents=True,
            exist_ok=True
        )

        self.output_tab.mkdir(
            parents=True,
            exist_ok=True
        )

        self.energy = None

        self.threshold = None

        self.mask = None

        self.events = []

        self.events_table = None

    # =====================================================

    def information(self):

        print()
        print("=" * 60)
        print("STORM ANALYSIS")
        print("=" * 60)
        print()

        print(
            f"Spectral windows : {len(self.statistics):,}"
        )

    # =====================================================

    def prepare_energy(self):

        self.energy = (
            self.statistics["energy"]
            .astype(float)
            .to_numpy()
        )

        print()

        print(
            "Energy series prepared."
        )

    # =====================================================

    def compute_threshold(
        self,
        percentile=90
    ):

        self.threshold = np.percentile(
            self.energy,
            percentile
        )

        print()

        print(
            f"Storm threshold ({percentile}%) : "
            f"{self.threshold:.6f}"
        )

    # =====================================================

    def build_mask(self):

        self.mask = (
            self.energy
            >=
            self.threshold
        )

        print()

        print(
            f"Storm windows : "
            f"{self.mask.sum()}"
        )

    # =====================================================

    def detect_events(self):

        print()
        print(
            "Searching storm events..."
        )

        start = None

        for i, value in enumerate(
            self.mask
        ):

            if value and start is None:

                start = i

            elif (not value) and (
                start is not None
            ):

                self.events.append(
                    (start, i - 1)
                )

                start = None

        if start is not None:

            self.events.append(
                (
                    start,
                    len(self.mask) - 1
                )
            )

        print(
            f"Storm events : "
            f"{len(self.events)}"
        )

    # =====================================================

    def build_table(self):

        rows = []

        for i, (a, b) in enumerate(
            self.events,
            start=1
        ):

            subset = self.statistics.iloc[
                a:b + 1
            ]

            # Report the peak period/frequency of the window where the
            # storm was strongest, rather than max()/mean() across the
            # whole event — a single mis-detected window would otherwise
            # skew the reported "storm period" even though the energy
            # itself is aggregated correctly.
            peak_row = subset.loc[
                subset.energy.idxmax()
            ]

            rows.append({

                "storm":

                    i,

                "first_window":

                    a,

                "last_window":

                    b,

                "duration_windows":

                    b - a + 1,

                "duration_hours":

                    (b - a + 1)
                    * 20
                    / 60,

                "max_energy":

                    subset.energy.max(),

                "mean_energy":

                    subset.energy.mean(),

                "peak_period":

                    peak_row.peak_period,

                "peak_frequency":

                    peak_row.peak_frequency

            })

        self.events_table = pd.DataFrame(
            rows
        )

        print()

        print(
            self.events_table
        )
        # =====================================================

    def get_events_table(self):

            """
            Return table with all detected storms.
            """

            return self.events_table.copy()
        # =====================================================

    def get_events(self):

            """
            Return list of storm windows.
            """

            return self.events.copy()        
        # =====================================================

    def energy_statistics(self):

        if self.events_table.empty:

            return

        print()

        print("=" * 60)
        print("STORM STATISTICS")
        print("=" * 60)

        print()

        print(
            self.events_table.describe(
                include="all"
            )
        )

    # =====================================================

    def plot_energy(self):

        print()

        print(
            "Plotting energy time series..."
        )

        time = pd.to_datetime(self.statistics["timestamp"])

        plt.figure(
            figsize=(15,5)
        )

        plt.plot(

            time,

            self.energy,

            linewidth=1.2,

            label="Wave energy"

        )

        plt.axhline(

            self.threshold,

            color="red",

            linestyle="--",

            linewidth=2,

            label="Storm threshold (90th percentile)"

        )

        plt.xlabel(
            "Time"
        )

        plt.ylabel(
            "Integrated spectral energy"
        )

        plt.title(
            "Wave energy"
        )

        plt.grid(True)

        plt.legend()

        plt.gcf().autofmt_xdate()

        plt.tight_layout()

        plt.savefig(

            self.output_fig /
            "storm_energy.png",

            dpi=300

        )

        plt.close()

        print(
            "✓ storm_energy.png"
        )

    # =====================================================

    def plot_detected_events(self):

        print()

        print(
            "Plotting detected storms..."
        )

        time = pd.to_datetime(self.statistics["timestamp"])

        plt.figure(
            figsize=(15,5)
        )

        plt.plot(

            time,

            self.energy,

            linewidth=1.2,

            color="black",

            label="Wave energy"

        )

        plt.axhline(

            self.threshold,

            color="red",

            linestyle="--",

            label="Storm threshold"

        )

        for j, (start, stop) in enumerate(self.events):

            plt.axvspan(

                time.iloc[start],

                time.iloc[stop],

                color="tab:blue",

                alpha=0.3,

                label="Detected storm" if j == 0 else None

            )

        plt.xlabel(
            "Time"
        )

        plt.ylabel(
            "Energy"
        )

        plt.title(
            "Detected storm events"
        )

        plt.grid(True)

        plt.legend(loc="upper right")

        plt.gcf().autofmt_xdate()

        plt.tight_layout()

        plt.savefig(

            self.output_fig /
            "storm_events.png",

            dpi=300

        )

        plt.close()

        print(
            "✓ storm_events.png"
        )

    # =====================================================

    def plot_event_histogram(self):

        if self.events_table.empty:

            return

        plt.figure(
            figsize=(10,5)
        )

        plt.hist(

            self.events_table[
                "max_energy"
            ],

            bins=20

        )

        plt.xlabel(
            "Maximum storm energy"
        )

        plt.ylabel(
            "Count"
        )

        plt.title(
            "Storm energy distribution"
        )

        plt.grid(True)

        plt.tight_layout()

        plt.savefig(

            self.output_fig /
            "storm_histogram.png",

            dpi=300

        )

        plt.close()

        print(
            "✓ storm_histogram.png"
        )

    # =====================================================

    def save_table(self):

        self.events_table.to_csv(

            self.output_tab /
            "storm_events.csv",

            index=False

        )

        print()

        print(
            "✓ storm_events.csv"
        )

    # =====================================================

    def summary(self):

        print()

        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)

        print()

        print(
            f"Detected storms : "
            f"{len(self.events)}"
        )

        if self.events_table.empty:

            return

        print(
            f"Longest storm : "
            f"{self.events_table['duration_hours'].max():.2f} h"
        )

        print(
            f"Maximum energy : "
            f"{self.events_table['max_energy'].max():.6f}"
        )

        print(
            f"Average energy : "
            f"{self.events_table['mean_energy'].mean():.6f}"
        )

        print(
            f"Maximum peak period : "
            f"{self.events_table['peak_period'].max():.2f} s"
        )

    # =====================================================

    def run(self):

        self.information()

        self.prepare_energy()

        self.compute_threshold()

        self.build_mask()

        self.detect_events()

        self.build_table()

        self.energy_statistics()

        self.plot_energy()

        self.plot_detected_events()

        self.plot_event_histogram()

        self.save_table()

        self.summary()