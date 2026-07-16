from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class WindWaveAnalysis:
    """
    Analysis of relationship between
    wind and sea waves.

    Input

    spectra  -> WaveSpectra object
    wind_csv -> path to csv file
    """

    def __init__(
        self,
        spectra,
        storm,
        wind_csv
    ):

        self.spectra = spectra

        # Новый объект StormAnalysis
        self.storm = storm

        self.wind_csv = Path(
            wind_csv
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

        self.wind = None

        self.wave = None

        self.data = None

        self.correlation = {}

        self.lag_table = pd.DataFrame()

    def information(self):
        print()
        print("=" * 60)
        print("WIND - WAVE ANALYSIS")
        print("=" * 60)
        print()
        print("Wind file :", self.wind_csv)

    def load_wind(self):
        print()
        print("Loading wind data...")

        self.wind = pd.read_csv(self.wind_csv)
        self.wind.columns = [c.strip() for c in self.wind.columns]

        required = ["datetime", "Wind Speed", "Wind Dir"]
        missing = [c for c in required if c not in self.wind.columns]
        if missing:
            raise RuntimeError(
                "Wind CSV is missing required columns: " + ", ".join(missing)
            )

        self.wind["datetime"] = pd.to_datetime(self.wind["datetime"], errors="coerce")
        self.wind = self.wind.sort_values("datetime").reset_index(drop=True)

        print("✓ Wind data loaded.")

    def quality_control(self):
        print()
        print("=" * 60)
        print("WIND QUALITY")
        print("=" * 60)
        print()
        print("Records :", len(self.wind))
        print()
        print(self.wind.isna().sum())

        duplicates = self.wind.duplicated().sum()

        print()
        print("Duplicates :", duplicates)
        print()
        print(self.wind.describe(include="all"))

    def prepare_wave_table(self):
        print()
        print("Preparing wave table...")

        table = pd.DataFrame(self.spectra.statistics)
        if len(table) == 0:
            raise RuntimeError("WaveSpectra statistics are empty.")

        required = ["timestamp", "energy"]
        missing = [c for c in required if c not in table.columns]
        if missing:
            raise RuntimeError(
                "WaveSpectra statistics are missing required columns: "
                + ", ".join(missing)
            )

        table["timestamp"] = pd.to_datetime(table["timestamp"], errors="coerce")
        for column in ["peak_period", "peak_frequency"]:
            if column not in table.columns:
                table[column] = np.nan

        self.wave = table.sort_values("timestamp").reset_index(drop=True)

        print()
        print("Wave windows :", len(self.wave))

    def prepare_wind_table(self):
        self.wind = self.wind.rename(
            columns={"Wind Speed": "wind_speed", "Wind Dir": "wind_direction"}
        )
        self.wind = self.wind[["datetime", "wind_speed", "wind_direction"]]
        self.wind["wind_speed"] = pd.to_numeric(self.wind["wind_speed"], errors="coerce")
        self.wind["wind_direction"] = pd.to_numeric(
            self.wind["wind_direction"], errors="coerce"
        )
        self.wind["wind_direction"] = self.wind["wind_direction"] % 360
        self.wind = self.wind.dropna(
            subset=["datetime", "wind_speed", "wind_direction"]
        ).sort_values("datetime").reset_index(drop=True)

        print()
        print("Wind table prepared.")

    def synchronize(self):
        print()
        print("Synchronizing wind and wave data...")

        wind = self.wind.dropna(
            subset=["datetime", "wind_speed", "wind_direction"]
        ).sort_values("datetime").reset_index(drop=True)
        wave = self.wave.dropna(subset=["timestamp", "energy"]).sort_values(
            "timestamp"
        ).reset_index(drop=True)

        self.data = pd.merge_asof(
            wave,
            wind,
            left_on="timestamp",
            right_on="datetime",
            direction="nearest",
            tolerance=pd.Timedelta("1h"),
        )

        before = len(self.data)
        self.data = self.data.dropna(
            subset=["wind_speed", "wind_direction", "energy"]
        ).reset_index(drop=True)
        after = len(self.data)

        print()
        print("Wave windows :", before)
        print("Matched      :", after)
        print("Dropped      :", before - after)

        if after == 0:
            raise RuntimeError(
                "No synchronized wind-wave records were found within merge_asof tolerance."
            )

    def merged_statistics(self):
        print()
        print("=" * 60)
        print("MERGED DATA")
        print("=" * 60)
        print()

        columns = [
            c
            for c in ["wind_speed", "energy", "peak_period", "peak_frequency"]
            if c in self.data.columns
        ]
        print(self.data[columns].describe())

    def save_merged_table(self):
        self.data.to_csv(self.output_tab / "wind_wave_table.csv", index=False)
        print()
        print("✓ wind_wave_table.csv")

    def time_series_plot(self):
        print()
        print("Plotting time series...")

        fig, ax = plt.subplots(2, 1, figsize=(15, 8), sharex=True)
        ax[0].plot(self.data["datetime"], self.data["wind_speed"], lw=1.5)
        ax[0].set_ylabel("Wind speed (m/s)")
        ax[0].grid(True)
        ax[0].set_title("Wind speed")

        ax[1].plot(self.data["timestamp"], self.data["energy"], lw=1.5)
        ax[1].set_ylabel("Wave energy")
        ax[1].set_xlabel("Time")
        ax[1].grid(True)
        ax[1].set_title("Wave energy")

        plt.tight_layout()
        plt.savefig(self.output_fig / "wind_wave_timeseries.png", dpi=300)
        plt.close(fig)

        print("✓ wind_wave_timeseries.png")

    def compute_correlations(self):
        print()
        print("=" * 60)
        print("CORRELATION ANALYSIS")
        print("=" * 60)

        subset = self.data[["wind_speed", "energy"]].dropna()
        if len(subset) < 2:
            pearson = np.nan
            spearman = np.nan
            kendall = np.nan
        else:
            energy = subset["energy"]
            wind = subset["wind_speed"]
            pearson = wind.corr(energy, method="pearson")
            spearman = wind.corr(energy, method="spearman")
            kendall = wind.corr(energy, method="kendall")

        self.correlation = {
            "pearson": pearson,
            "spearman": spearman,
            "kendall": kendall,
        }

        print()
        print(f"Pearson  : {pearson:.4f}")
        print(f"Spearman : {spearman:.4f}")
        print(f"Kendall  : {kendall:.4f}")

    def scatter_plot(self):
        print()
        print("Plotting scatter...")

        subset = self.data[["wind_speed", "energy"]].dropna()
        subset = subset[subset["energy"] > 0]
        x = subset["wind_speed"]
        y = subset["energy"]

        plt.figure(figsize=(8, 6))
        plt.scatter(x, y, s=15, alpha=0.35, edgecolor="none")

        # Wave energy is strictly positive and spans several orders of
        # magnitude (heavily right-skewed), so a linear-space OLS fit is
        # dominated by a handful of outliers and looks like a flat,
        # meaningless line. A log-linear fit (linear regression of
        # log(energy) vs wind speed) respects the data's shape and
        # renders as a straight line on the log-y axis used below.
        log_r2 = np.nan
        if len(subset) >= 2 and x.nunique() > 1:
            coef = np.polyfit(x, np.log(y), 1)
            xx = np.linspace(x.min(), x.max(), 100)
            plt.plot(xx, np.exp(np.polyval(coef, xx)), linewidth=2, color="tab:red",
                     label="Log-linear fit")

            fitted = np.polyval(coef, x)
            residual = np.log(y) - fitted
            ss_res = np.sum(residual ** 2)
            ss_tot = np.sum((np.log(y) - np.log(y).mean()) ** 2)
            log_r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan

        r = self.correlation["pearson"]
        title = "Wind vs Wave Energy"
        subtitle_parts = []
        if np.isfinite(r):
            subtitle_parts.append(f"linear R² = {r ** 2:.3f}")
        if np.isfinite(log_r2):
            subtitle_parts.append(f"log-linear R² = {log_r2:.3f}")
        if subtitle_parts:
            title += "\n" + ", ".join(subtitle_parts)
            title += "  (weak relationship — energy is driven by more than local wind)"

        plt.yscale("log")
        plt.xlabel("Wind speed (m/s)")
        plt.ylabel("Wave energy (log scale)")
        plt.title(title)
        plt.legend(loc="lower right")
        plt.grid(True, which="both", alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_fig / "wind_vs_energy.png", dpi=300)
        plt.close()

        print("✓ wind_vs_energy.png")

    def correlation_matrix(self):
        print()
        print("Computing correlation matrix...")

        columns = [
            c
            for c in [
                "wind_speed",
                "wind_direction",
                "energy",
                "peak_period",
                "peak_frequency",
            ]
            if c in self.data.columns
        ]
        matrix = self.data[columns].corr(numeric_only=True)

        matrix.to_csv(self.output_tab / "correlation_matrix.csv")

        plt.figure(figsize=(8, 7))
        image = plt.imshow(matrix, aspect="auto", cmap="coolwarm", vmin=-1, vmax=1)
        plt.xticks(range(len(matrix.columns)), matrix.columns, rotation=45, ha="right")
        plt.yticks(range(len(matrix.columns)), matrix.columns)

        for i in range(len(matrix.columns)):
            for j in range(len(matrix.columns)):
                value = matrix.iloc[i, j]
                text_color = "white" if abs(value) > 0.6 else "black"
                plt.text(
                    j, i, f"{value:.2f}",
                    ha="center", va="center",
                    color=text_color, fontsize=10
                )

        plt.title("Wind / wave correlation matrix")
        cbar = plt.colorbar(image)
        cbar.set_label("Pearson correlation")
        plt.tight_layout()
        plt.savefig(self.output_fig / "correlation_matrix.png", dpi=300)
        plt.close()

        print("✓ correlation_matrix.png")

    def save_summary(self):
        summary = pd.DataFrame(
            {
                "parameter": ["Pearson", "Spearman", "Kendall"],
                "value": [
                    self.correlation["pearson"],
                    self.correlation["spearman"],
                    self.correlation["kendall"],
                ],
            }
        )
        summary.to_csv(self.output_tab / "wind_wave_summary.csv", index=False)
        print()
        print("✓ wind_wave_summary.csv")

        # =====================================================
    def lag_analysis(
        self,
        max_lag_hours=8,
        window_hours=24
    ):

        print()
        print("=" * 60)
        print("STORM LAG ANALYSIS")
        print("=" * 60)

    # ---------------------------------------------
    # Проверяем наличие результатов StormAnalysis
    # ---------------------------------------------

        if (
            self.storm is None
            or self.storm.events_table is None
            or self.storm.events_table.empty
        ):

            print("Storm table is empty.")
            return

        storm_table = self.storm.events_table.copy()

        wave = self.wave.copy()
        wind = self.wind.copy()

        wave["timestamp"] = pd.to_datetime(
            wave["timestamp"]
        )

        wind["datetime"] = pd.to_datetime(
            wind["datetime"]
        )

        lag_rows = []

        self.storm_correlations = []

        self.storm_lags = []

    # ---------------------------------------------
    # Анализ каждого шторма отдельно
    # ---------------------------------------------
        for _, storm in storm_table.iterrows():

            first_window = int(
                storm["first_window"]
            )

            last_window = int(
                storm["last_window"]
            )

            storm_start = wave.iloc[
                first_window
            ]["timestamp"]

            storm_end = wave.iloc[
                last_window
            ]["timestamp"]

            left = storm_start - pd.Timedelta(
                hours=window_hours
            )

            right = storm_end + pd.Timedelta(
                hours=window_hours
            )

            wave_part = wave[
                (wave["timestamp"] >= left)
                &
                (wave["timestamp"] <= right)
            ].copy()

            wind_part = wind[
                (wind["datetime"] >= left)
                &
                (wind["datetime"] <= right)
            ].copy()

            if (
                len(wave_part) < 30
                or
                len(wind_part) < 5
            ):
                continue

            merged = pd.merge_asof(

                wave_part.sort_values(
                    "timestamp"
                ),

                wind_part.sort_values(
                    "datetime"
                ),

                left_on="timestamp",

                right_on="datetime",

                direction="nearest",

                tolerance=pd.Timedelta(
                    "1H"
                )

            ).dropna()

            if len(merged) < 30:
                continue

            # -------------------------------------------------
            # Подготавливаем сигналы
            # -------------------------------------------------

            wind_signal = (
                merged["wind_speed"]
                .to_numpy(dtype=np.float64)
                .copy()
            )

            wave_signal = (
                merged["energy"]
                .to_numpy(dtype=np.float64)
                .copy()
            )

            wind_signal = (
                wind_signal -
                np.mean(wind_signal)
            )

            wave_signal = (
                wave_signal -
                np.mean(wave_signal)
            )

            wind_std = np.std(
                wind_signal
            )

            wave_std = np.std(
                wave_signal
            )

            if (
                wind_std == 0
                or
                wave_std == 0
            ):
                continue

            # -------------------------------------------------
            # Кросс-корреляция
            # -------------------------------------------------

            corr = np.correlate(

                wave_signal,

                wind_signal,

                mode="full"

            )

            corr = corr / (

                wind_std

                *

                wave_std

                *

                len(wind_signal)

            )

            lags = np.arange(

                -len(wind_signal) + 1,

                len(wind_signal)

            )

            minutes = (
                self.spectra.window_minutes
            )

            hours = (
                lags * minutes / 60
            )

            mask = (
                np.abs(hours)
                <=
                max_lag_hours
            )

            hours = hours[mask]

            corr = corr[mask]

            if len(corr) == 0:
                continue

            best = np.argmax(
                corr
            )

            best_lag = float(
                hours[best]
            )

            best_corr = float(
                corr[best]
            )

            lag_rows.append({

                "storm":
                    int(storm["storm"]),

                "storm_start":
                    storm_start,

                "storm_end":
                    storm_end,

                "lag_hours":
                    best_lag,

                "correlation":
                    best_corr

            })

            self.storm_lags.append(
                best_lag
            )

            self.storm_correlations.append({

                "storm":
                    int(storm["storm"]),

                "lag":
                    hours,

                "corr":
                    corr

            })

        self.lag_table = pd.DataFrame(
            lag_rows
        )

        print()

        print(
            "Storms analysed :",
            len(self.lag_table)
        )

        print()

        print(
            self.lag_table
        )
        
        # =====================================================
    def plot_storm_lag_curves(self):

        if len(self.storm_correlations) == 0:
            return

        print()
        print("Plotting storm lag curves...")

        plt.figure(figsize=(14, 7))

        for storm in self.storm_correlations:

            plt.plot(
                storm["lag"],
                storm["corr"],
                linewidth=2,
                alpha=0.7,
                label=f"Storm {storm['storm']}"
            )

        plt.axvline(
            0,
            color="black",
            linestyle="--",
            linewidth=2
        )

        plt.xlabel("Lag (hours)")
        plt.ylabel("Pearson correlation")
        plt.title("Wind-wave lag for each storm")

        plt.grid(True)

        plt.legend(
            fontsize=8,
            ncol=2
        )

        plt.tight_layout()

        plt.savefig(
            self.output_fig /
            "storm_lag_curves.png",
            dpi=300
        )

        plt.close()

        print("✓ storm_lag_curves.png")
        # =====================================================
    def plot_mean_lag_curve(self):

        if len(self.storm_correlations) == 0:
            return

        print()
        print("Computing mean lag curve...")

        common_lag = self.storm_correlations[0]["lag"]

        curves = []

        for storm in self.storm_correlations:

            curves.append(
                storm["corr"]
            )

        curves = np.vstack(curves)

        mean_corr = np.mean(
            curves,
            axis=0
        )

        std_corr = np.std(
            curves,
            axis=0
        )

        best = np.argmax(
            mean_corr
        )

        self.mean_best_lag = float(
            common_lag[best]
        )

        self.mean_best_corr = float(
            mean_corr[best]
        )

        plt.figure(figsize=(14, 7))

        plt.plot(
            common_lag,
            mean_corr,
            linewidth=3,
            label="Mean correlation"
        )   

        plt.fill_between(
            common_lag,
            mean_corr - std_corr,
            mean_corr + std_corr,
            alpha=0.25
        )

        plt.axvline(
            0,
            color="black",
            linestyle="--"
        )

        plt.axvline(
            self.mean_best_lag,
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"Maximum = {self.mean_best_lag:.2f} h"
        )

        plt.xlabel("Lag (hours)")
        plt.ylabel("Pearson correlation")
        plt.title("Mean storm lag")

        plt.grid(True)

        plt.legend()

        plt.tight_layout()

        plt.savefig(
            self.output_fig /
            "storm_mean_lag.png",
            dpi=300
        )

        plt.close()

        print("✓ storm_mean_lag.png")

        print()

        print(
            f"Mean lag : {self.mean_best_lag:.2f} h"
        )

        print(
            f"Correlation : {self.mean_best_corr:.3f}"
        )

    def compare_timeseries(self):
        print()
        print("Plotting synchronized series...")

        wind_color = "tab:blue"
        energy_color = "tab:orange"

        fig, ax1 = plt.subplots(figsize=(15, 6))
        line1, = ax1.plot(
            self.data["datetime"], self.data["wind_speed"],
            color=wind_color, linewidth=1.2, label="Wind speed"
        )
        ax1.set_ylabel("Wind speed (m/s)", color=wind_color)
        ax1.tick_params(axis="y", labelcolor=wind_color)
        ax1.set_xlabel("Time")
        ax1.grid(True, alpha=0.3)

        ax2 = ax1.twinx()
        line2, = ax2.plot(
            self.data["datetime"], self.data["energy"],
            color=energy_color, linewidth=1.5, label="Wave energy"
        )
        ax2.set_ylabel("Wave energy", color=energy_color)
        ax2.tick_params(axis="y", labelcolor=energy_color)

        ax1.legend(handles=[line1, line2], loc="upper right")

        plt.title("Wind and wave energy")
        fig.autofmt_xdate()
        fig.tight_layout()
        plt.savefig(self.output_fig / "wind_wave_comparison.png", dpi=300)
        plt.close(fig)

        print("✓ wind_wave_comparison.png")

    def classify_wind(self):
        print()
        print("Classifying wind speed...")

        bins = [0, 2, 4, 6, 8, np.inf]
        labels = ["0-2", "2-4", "4-6", "6-8", "8+"]

        self.data["wind_class"] = pd.cut(
            self.data["wind_speed"], bins=bins, labels=labels, include_lowest=True
        )

        print("✓ Wind classes created.")

    def energy_boxplot(self):
        print()
        print("Plotting boxplot...")

        groups = []
        labels = []
        for name, group in self.data.groupby("wind_class", observed=False):
            values = group["energy"].dropna().values
            if len(values) == 0:
                continue
            groups.append(values)
            labels.append(str(name))

        plt.figure(figsize=(10, 6))
        if groups:
            plt.boxplot(groups, tick_labels=labels, showfliers=False)

        plt.xlabel("Wind speed (m/s)")
        plt.ylabel("Wave energy")
        plt.title("Wave energy vs wind speed")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(self.output_fig / "energy_boxplot.png", dpi=300)
        plt.close()

        print("✓ energy_boxplot.png")

    def classify_direction(self):
        print()
        print("Grouping wind directions...")

        direction = (self.data["wind_direction"] % 360 + 22.5) % 360
        bins = np.arange(0, 361, 45)
        labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

        self.data["wind_sector"] = pd.cut(
            direction,
            bins=bins,
            labels=labels,
            include_lowest=True,
            right=False,
        )

        print("✓ Wind sectors created.")

    def energy_by_direction(self):
        print()
        print("Computing energy by direction...")

        table = (
            self.data.groupby("wind_sector", observed=False)["energy"]
            .mean()
            .reset_index()
        )
        table.to_csv(self.output_tab / "energy_by_direction.csv", index=False)

        plt.figure(figsize=(10, 5))
        plt.bar(table["wind_sector"].astype(str), table["energy"])
        plt.xlabel("Wind direction")
        plt.ylabel("Mean wave energy")
        plt.title("Wave energy by wind direction")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(self.output_fig / "energy_by_direction.png", dpi=300)
        plt.close()

        print("✓ energy_by_direction.png")

    def dominant_direction(self):
        mean_energy = (
            self.data.groupby("wind_sector", observed=False)["energy"]
            .mean()
            .dropna()
        )

        if len(mean_energy) == 0:
            idx = np.nan
            value = np.nan
        else:
            idx = mean_energy.idxmax()
            value = mean_energy.max()

        print()
        print("=" * 60)
        print("DOMINANT WAVE GENERATING WIND")
        print("=" * 60)
        print()
        print("Direction :", idx)
        print(f"Mean energy : {value:.6f}")

    def scientific_report(self):

        print()
        print("=" * 60)
        print("SCIENTIFIC REPORT")
        print("=" * 60)
        print()

        print(
            "Number of synchronized records :",
            len(self.data)
        )

        print()

        print(
            f"Mean wind speed      : {self.data['wind_speed'].mean():.2f} m/s"
        )

        print(
            f"Maximum wind speed   : {self.data['wind_speed'].max():.2f} m/s"
        )

        print()

        print(
            f"Mean wave energy     : {self.data['energy'].mean():.6f}"
        )

        print(
            f"Maximum wave energy  : {self.data['energy'].max():.6f}"
        )

        print()

        print(
            f"Pearson correlation  : {self.correlation['pearson']:.3f}"
        )

        print(
            f"Spearman correlation : {self.correlation['spearman']:.3f}"
        )

        print(
            f"Kendall correlation  : {self.correlation['kendall']:.3f}"
            )

        print()

        if (
            hasattr(self, "lag_table")
            and
            not self.lag_table.empty
        ):

            print(
                f"Storms analysed      : {len(self.lag_table)}"
            )

            print(
                f"Mean lag             : {self.lag_table['lag_hours'].mean():.2f} hours"
            )

            print(
                f"Median lag           : {self.lag_table['lag_hours'].median():.2f} hours"
            )

            print(
                f"Minimum lag          : {self.lag_table['lag_hours'].min():.2f} hours"
            )

            print(
                f"Maximum lag          : {self.lag_table['lag_hours'].max():.2f} hours"
            )

            print()

            print(
                f"Mean storm correlation : {self.lag_table['correlation'].mean():.3f}"
            )

            print(
                f"Maximum correlation    : {self.lag_table['correlation'].max():.3f}"
            )

        else:

            print(
                "Storm lag analysis was not performed."
            )
            
    def export_report(self):

        has_lag = not self.lag_table.empty

        report = pd.DataFrame(

            {

                "Parameter": [

                    "Records",

                    "Mean wind speed",

                    "Maximum wind speed",

                    "Mean wave energy",

                    "Maximum wave energy",

                    "Pearson",

                    "Spearman",

                    "Kendall",

                    "Mean lag (hours)",

                    "Median lag (hours)",

                    "Minimum lag (hours)",

                    "Maximum lag (hours)",

                    "Mean storm correlation",

                    "Maximum storm correlation"

                ],

                "Value": [

                    len(self.data),

                    self.data["wind_speed"].mean(),

                    self.data["wind_speed"].max(),

                    self.data["energy"].mean(),

                    self.data["energy"].max(),

                    self.correlation["pearson"],

                    self.correlation["spearman"],

                    self.correlation["kendall"],

                    self.lag_table["lag_hours"].mean() if has_lag else np.nan,

                    self.lag_table["lag_hours"].median() if has_lag else np.nan,

                    self.lag_table["lag_hours"].min() if has_lag else np.nan,

                    self.lag_table["lag_hours"].max() if has_lag else np.nan,

                    self.lag_table["correlation"].mean() if has_lag else np.nan,

                    self.lag_table["correlation"].max() if has_lag else np.nan

                ]

            }

        )

        report.to_csv(

            self.output_tab /
            "wind_wave_report.csv",

            index=False

        )

        print()

        print(
            "✓ wind_wave_report.csv"
        )    

    def beaufort_scale(self):
        print()
        print("Applying Beaufort scale...")

        limits = [
            0,
            0.3,
            1.6,
            3.4,
            5.5,
            8.0,
            10.8,
            13.9,
            17.2,
            20.8,
            24.5,
            28.5,
            32.7,
            np.inf,
        ]
        names = [
            "0 Calm",
            "1 Light Air",
            "2 Light Breeze",
            "3 Gentle Breeze",
            "4 Moderate Breeze",
            "5 Fresh Breeze",
            "6 Strong Breeze",
            "7 Near Gale",
            "8 Gale",
            "9 Strong Gale",
            "10 Storm",
            "11 Violent Storm",
            "12 Hurricane",
        ]

        self.data["beaufort"] = pd.cut(
            self.data["wind_speed"], bins=limits, labels=names, include_lowest=True
        )

        print("✓ Beaufort classes created.")

    def beaufort_statistics(self):
        table = (
            self.data.groupby("beaufort", observed=False)
            .agg(
                mean_energy=("energy", "mean"),
                max_energy=("energy", "max"),
                count=("energy", "count"),
            )
            .reset_index()
        )
        table.to_csv(self.output_tab / "beaufort_statistics.csv", index=False)

        plt.figure(figsize=(12, 5))
        plt.bar(table["beaufort"].astype(str), table["mean_energy"], color="tab:blue")
        plt.xticks(rotation=45, ha="right")
        plt.xlabel("Beaufort class")
        plt.ylabel("Mean wave energy")
        plt.title("Wave energy by Beaufort class")
        plt.grid(True, axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_fig / "beaufort_energy.png", dpi=300)
        plt.close()

        print("✓ beaufort_energy.png")

    def diurnal_cycle(self):
        print()
        print("Computing diurnal cycle...")

        self.data["hour"] = self.data["datetime"].dt.hour
        hourly = self.data.groupby("hour").agg(
            wind=("wind_speed", "mean"), energy=("energy", "mean")
        )
        hourly.reset_index().to_csv(self.output_tab / "hourly_cycle.csv", index=False)

        fig, ax1 = plt.subplots(figsize=(12, 5))

        wind_color = "tab:blue"
        energy_color = "tab:orange"

        line1, = ax1.plot(
            hourly.index, hourly["wind"],
            linewidth=2, color=wind_color, label="Wind speed"
        )
        ax1.set_ylabel("Wind speed (m/s)", color=wind_color)
        ax1.tick_params(axis="y", labelcolor=wind_color)
        ax1.set_xlabel("Hour of day")
        ax1.set_xticks(range(0, 24, 2))
        ax1.grid(True, alpha=0.3)

        ax2 = ax1.twinx()
        line2, = ax2.plot(
            hourly.index, hourly["energy"],
            linewidth=2, color=energy_color, label="Wave energy"
        )
        ax2.set_ylabel("Wave energy", color=energy_color)
        ax2.tick_params(axis="y", labelcolor=energy_color)

        ax1.legend(handles=[line1, line2], loc="upper right")

        plt.title("Average diurnal cycle")
        plt.tight_layout()
        plt.savefig(self.output_fig / "diurnal_cycle.png", dpi=300)
        plt.close(fig)

        print("✓ diurnal_cycle.png")

    def wind_rose(self):
        print()
        print("Building wind rose...")

        subset = self.data[["wind_direction", "wind_speed"]].dropna()
        direction = np.deg2rad(subset["wind_direction"] % 360)
        speed = subset["wind_speed"].to_numpy(dtype=float)

        sectors = 16
        bins = np.linspace(0, 2 * np.pi, sectors + 1)
        values = np.zeros(sectors)
        counts = np.zeros(sectors)

        for angle, v in zip(direction, speed):
            index = np.digitize(angle, bins, right=False) - 1
            if index == sectors:
                index = 0
            values[index] += v
            counts[index] += 1

        mean_speed = np.divide(
            values, counts, out=np.zeros_like(values), where=counts > 0
        )
        theta = np.linspace(0, 2 * np.pi, sectors, endpoint=False)
        width = 2 * np.pi / sectors

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection="polar")
        ax.bar(
            theta, mean_speed, width=width, bottom=0,
            color="tab:blue", alpha=0.85, edgecolor="white", linewidth=0.5
        )
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_rlabel_position(135)
        ax.set_title("Wind Rose — mean wind speed by direction (m/s)")

        plt.tight_layout()
        plt.savefig(self.output_fig / "wind_rose.png", dpi=300)
        plt.close(fig)

        print("✓ wind_rose.png")

    def wave_energy_rose(self):
        print()
        print("Building wave-energy rose...")

        subset = self.data[["wind_direction", "energy"]].dropna()
        sectors = np.arange(0, 360, 22.5)
        energy = np.zeros(len(sectors))
        count = np.zeros(len(sectors))

        for d, e in zip(subset["wind_direction"] % 360, subset["energy"]):
            idx = int(d // 22.5)
            idx %= len(sectors)
            energy[idx] += e
            count[idx] += 1

        mean_energy = np.divide(
            energy, count, out=np.zeros_like(energy), where=count > 0
        )
        theta = np.deg2rad(sectors)

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection="polar")
        ax.bar(
            theta, mean_energy, width=np.deg2rad(22.5),
            color="tab:orange", alpha=0.85, edgecolor="white", linewidth=0.5
        )
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_rlabel_position(135)
        ax.set_title("Wave energy by wind direction (mean energy)")

        plt.tight_layout()
        plt.savefig(self.output_fig / "wave_energy_rose.png", dpi=300)
        plt.close(fig)

        print("✓ wave_energy_rose.png")

    def wind_distribution(self):
        print()
        print("Computing wind distribution...")

        distribution = (
            self.data.groupby("wind_sector", observed=False)
            .agg(
                observations=("wind_speed", "count"),
                mean_speed=("wind_speed", "mean"),
                max_speed=("wind_speed", "max"),
                mean_energy=("energy", "mean"),
            )
            .reset_index()
        )
        distribution.to_csv(self.output_tab / "wind_distribution.csv", index=False)

        print("✓ wind_distribution.csv")

    def run(self):
        self.information()
        self.load_wind()
        self.quality_control()
        self.prepare_wave_table()
        self.prepare_wind_table()
        self.synchronize()
        self.merged_statistics()
        self.save_merged_table()
        self.time_series_plot()
        self.compute_correlations()
        self.scatter_plot()
        self.correlation_matrix()
        self.classify_wind()
        self.energy_boxplot()
        self.beaufort_scale()
        self.beaufort_statistics()
        self.classify_direction()
        self.energy_by_direction()
        self.dominant_direction()
        self.diurnal_cycle()
        self.wind_rose()
        self.wave_energy_rose()
        self.wind_distribution()
        self.lag_analysis()
        self.plot_storm_lag_curves()
        self.plot_mean_lag_curve()
        self.compare_timeseries()
        self.save_summary()
        self.export_report()
        self.scientific_report()