from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import welch
from scipy.signal import find_peaks


class WaveSpectra:

    """
    Spectral analysis of sea surface waves.

    Input:
    - dataframe: pandas.DataFrame with columns 'timestamp' and 'wave_pressure'.
      Timestamps should be in datetime64 format.
    Output:
    - CSV files with spectra statistics.
    - PNG figures of spectra and energy plots.
    Attributes:
    - self.df
    - self.signal
    - self.fs
    - self.window_minutes
    - self.window_samples
    - self.output_fig, self.output_tab
    - self.windows
    - self.window_results
    - self.mean_psd
    - self.frequency
    - self.fp, self.tp, self.peaks
    """

    # =====================================================
    def __init__(self, dataframe):

        self.df = dataframe.copy()

        self.df["timestamp"] = pd.to_datetime(
            self.df["timestamp"]
        )

        self.df = self.df.sort_values(
            "timestamp"
        ).reset_index(drop=True)

        self.signal = (
            self.df["wave_pressure"]
            .astype(float)
            .to_numpy()
        )

        self.fs = 4.0
        self.window_minutes = 20

        # Lower bound of the wind-wave/swell band (Hz). Spectral energy
        # below this frequency is tide/mooring-trend leakage, not surface
        # gravity waves, and must be excluded before picking a "peak".
        self.min_wave_frequency = 0.05

        self.window_samples = (
            self.window_minutes
            * 60
            * int(self.fs)
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

        self.frequency = None
        self.mean_psd = None
        self.statistics = []
        self.number_of_windows = 0
        self.sum_psd = None

    #1111111 =====================================================
    def information(self):

        print()
        print("=" * 60)
        print("SPECTRAL ANALYSIS")
        print("=" * 60)
        print()

        duration_seconds = len(self.signal) / self.fs
        duration_hours = duration_seconds / 3600
        duration_days = duration_hours / 24

        print(f"Sampling frequency : {self.fs:.2f} Hz")
        print(f"Samples            : {len(self.signal):,}")
        print(f"Duration           : {duration_hours:.2f} hours")
        print(f"Duration           : {duration_days:.2f} days")
        print(f"Window length      : {self.window_minutes} minutes")
        print(f"Samples / window   : {self.window_samples:,}")

        expected_windows = len(self.signal) // self.window_samples

        print(f"Expected windows   : {expected_windows:,}")
        print()

    # =====================================================
    def split_into_windows(self):
        print()
        print(
            "Splitting signal into windows..."
        )
        total = len(self.signal)
        step = self.window_samples
        self.windows = []

        for start in range(0, total, step):
            stop = start + step
            if stop > total:
                break
            self.windows.append(self.signal[start:stop])

        self.number_of_windows = len(self.windows)
        print(
            f"{self.number_of_windows} windows created."
        )
        print()

    # =====================================================
    def dominant_index(
        self,
        psd,
        frequency
    ):
        """
        Index of the highest PSD value restricted to the
        wind-wave/swell band (frequency >= min_wave_frequency).

        The raw spectrum is dominated by tide/mooring-trend energy
        at the lowest few frequency bins (near DC); a plain argmax
        would lock onto that instead of the real wave peak.
        """

        valid = frequency >= self.min_wave_frequency

        if not np.any(valid):
            return int(np.argmax(psd[1:]) + 1)

        candidate_indices = np.flatnonzero(valid)

        return int(
            candidate_indices[
                np.argmax(psd[candidate_indices])
            ]
        )

    # =====================================================
    def analyse_single_window(
        self,
        signal
    ):

        frequency, psd = welch(
            signal,
            fs=self.fs,
            window="hann",
            nperseg=4096,
            noverlap=2048,
            detrend="constant",
            scaling="density"
        )

        peak_index = self.dominant_index(
            psd,
            frequency
        )

        peak_frequency = frequency[peak_index]
        peak_period = (
            np.nan
            if peak_frequency == 0
            else
            1 / peak_frequency
        )

        energy = np.trapz(
            psd,
            frequency
        )

        variance = np.var(signal)

        rms = np.sqrt(
            variance
        )

        return {
            "frequency": frequency,
            "psd": psd,
            "peak_frequency": peak_frequency,
            "peak_period": peak_period,
            "energy": energy,
            "variance": variance,
            "rms": rms
        }

    # =====================================================
    def compute_all_spectra(self):
        print()
        print(
            "Computing spectra..."
        )

        self.window_results = []

        for i, window in enumerate(
            self.windows,
            start=1
        ):
            result = self.analyse_single_window(
                window
            )
            self.window_results.append(
                result
            )
            if i % 20 == 0:
                print(
                    f"{i} windows processed..."
                )

        print()
        print(
            "Finished."
        )

    # =====================================================
    def mean_spectrum(self):
        print()
        print(
            "Computing mean spectrum..."
        )

        # Stack all PSD arrays from windows
        psd_stack = []
        for result in self.window_results:
            psd_stack.append(
                result["psd"]
            )

        # Frequency vector from first window
        self.frequency = (
            self.window_results[0][
                "frequency"
            ]
        )

        # Compute mean PSD across windows
        self.mean_psd = np.mean(
            np.vstack(
                psd_stack
            ),
            axis=0
        )

        print(
            "Mean spectrum ready."
        )

    # =====================================================
    def dominant_wave(self):
        # Find index of peak in mean PSD, restricted to the
        # wind-wave/swell band (excludes tide/trend leakage).
        index = self.dominant_index(
            self.mean_psd,
            self.frequency
        )

        self.fp = self.frequency[index]
        self.tp = (
            np.nan
            if self.fp == 0
            else
            1 / self.fp
        )

        print()
        print(
            f"Peak frequency : {self.fp:.4f} Hz"
        )
        print(
            f"Peak period    : {self.tp:.2f} s"
        )
        print(
            f"Peak PSD       : {self.mean_psd[index]:.6e}"
        )

    # =====================================================
    def save_window_statistics(self):

        print()
        print("Saving window statistics...")

        rows = []

        start_time = self.df["timestamp"].iloc[0]

        delta = pd.Timedelta(
            minutes=self.window_minutes
        )

        for i, result in enumerate(
            self.window_results
        ):

            window_start = (
                start_time +
                i * delta
            )

            window_end = (
                start_time +
                (i + 1) * delta
            )

            rows.append({

                "window":
                    i + 1,

                "timestamp":
                    window_start,

                "start":
                    window_start,

                "end":
                    window_end,

                "peak_frequency":
                    result["peak_frequency"],

                "peak_period":
                    result["peak_period"],

                "energy":
                    result["energy"],

                "variance":
                    result["variance"],

                "rms":
                    result["rms"]

            })

        table = pd.DataFrame(rows)

        self.statistics = rows

        self.statistics_table = table

        table.to_csv(
            self.output_tab /
            "window_statistics.csv",
            index=False
        )

        print("✓ window_statistics.csv")

    # =====================================================
    def save_summary(self):
        summary = pd.DataFrame({
            "parameter": [
                "sampling_frequency",
                "window_minutes",
                "number_of_windows",
                "peak_frequency",
                "peak_period"
            ],
            "value": [
                self.fs,
                self.window_minutes,
                len(self.windows),
                self.fp,
                self.tp
            ]
        })
        summary.to_csv(
            self.output_tab /
            "spectra_summary.csv",
            index=False
        )
        print(
            "✓ spectra_summary.csv"
        )

    # =====================================================
    def plot_mean_spectrum(self):
        print()
        print(
            "Plotting mean spectrum..."
        )
        plt.figure(
            figsize=(12,6)
        )
        plt.semilogy(
            self.frequency,
            self.mean_psd,
            linewidth=2
        )
        # Mark the dominant wind-wave/swell frequency
        dominant_idx = self.dominant_index(
            self.mean_psd,
            self.frequency
        )
        plt.scatter(
            self.fp,
            self.mean_psd[dominant_idx],
            s=80,
            c="red",
            zorder=5,
            label=f"Peak: {self.tp:.1f} s ({self.fp:.3f} Hz)"
        )
        plt.axvspan(
            0,
            self.min_wave_frequency,
            color="gray",
            alpha=0.15,
            label="Excluded (tide / trend leakage)"
        )
        plt.xlabel(
            "Frequency (Hz)"
        )
        plt.ylabel(
            "PSD"
        )
        plt.title(
            "Mean Welch Spectrum"
        )
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(
            self.output_fig /
            "mean_spectrum.png",
            dpi=300
        )
        plt.close()
        print(
            "✓ mean_spectrum.png"
        )

    # =====================================================
    def plot_fft(self):
        print()
        print(
            "Computing FFT..."
        )
        fft = np.fft.rfft(
            self.signal
        )
        freq = np.fft.rfftfreq(
            len(self.signal),
            d=1/self.fs
        )
        amplitude = np.abs(
            fft
        )
        plt.figure(
            figsize=(12,6)
        )
        plt.plot(
            freq,
            amplitude,
            linewidth=0.7
        )
        plt.xlim(
            0,
            1
        )
        plt.xlabel(
            "Frequency (Hz)"
        )
        plt.ylabel(
            "Amplitude"
        )
        plt.title(
            "FFT Spectrum"
        )
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(
            self.output_fig /
            "fft_spectrum.png",
            dpi=300
        )
        plt.close()
        print(
            "✓ fft_spectrum.png"
        )

    # =====================================================
    def plot_cumulative_energy(self):
        print()
        print(
            "Computing cumulative energy..."
        )
        cumulative = np.cumsum(
            self.mean_psd
        )
        if cumulative[-1] != 0:
            cumulative = cumulative / cumulative[-1]
        plt.figure(
            figsize=(12,6)
        )
        plt.plot(
            self.frequency,
            cumulative,
            linewidth=2
        )
        plt.xlabel(
            "Frequency (Hz)"
        )
        plt.ylabel(
            "Normalized energy"
        )
        plt.title(
            "Cumulative Spectral Energy"
        )
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(
            self.output_fig /
            "cumulative_energy.png",
            dpi=300
        )
        plt.close()
        print(
            "✓ cumulative_energy.png"
        )

    # =====================================================
    def detect_spectral_peaks(self):
        print()
        print(
            "Searching spectral peaks..."
        )
        peaks, properties = find_peaks(
            self.mean_psd,
            prominence=np.max(
                self.mean_psd
            ) * 0.05
        )

        # Drop any peak in the tide/trend band — only wind-wave/swell
        # frequencies are meaningful "spectral peaks" for this analysis.
        keep = self.frequency[peaks] >= self.min_wave_frequency
        peaks = peaks[keep]
        for key in properties:
            properties[key] = np.asarray(properties[key])[keep]

        self.peaks = peaks
        self.peak_properties = properties
        print(
            "Peaks found:",
            len(peaks)
        )

    # =====================================================
    def plot_peak_spectrum(self):
        print()
        print(
            "Plotting spectral peaks..."
        )
        plt.figure(
            figsize=(12,6)
        )
        plt.semilogy(
            self.frequency,
            self.mean_psd,
            linewidth=2,
            label="Mean spectrum"
        )
        plt.scatter(
            self.frequency[self.peaks],
            self.mean_psd[self.peaks],
            s=50,
            c="red",
            zorder=5,
            label="Detected peaks"
        )
        plt.axvspan(
            0,
            self.min_wave_frequency,
            color="gray",
            alpha=0.15,
            label="Excluded (tide / trend leakage)"
        )
        plt.xlabel(
            "Frequency (Hz)"
        )
        plt.ylabel(
            "PSD"
        )
        plt.title(
            "Detected Spectral Peaks"
        )
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(
            self.output_fig /
            "peak_spectrum.png",
            dpi=300
        )
        plt.close()
        print(
            "✓ peak_spectrum.png"
        )

    # =====================================================
    def save_mean_spectrum(self):
        table = pd.DataFrame({
            "frequency":
                self.frequency,
            "psd":
                self.mean_psd
        })
        table.to_csv(
            self.output_tab /
            "mean_spectrum.csv",
            index=False
        )
        print(
            "✓ mean_spectrum.csv"
        )

    # =====================================================
    def save_all_spectra(self):
        folder = (
            self.output_tab /
            "individual_spectra"
        )
        folder.mkdir(
            parents=True,
            exist_ok=True
        )
        for i, result in enumerate(
            self.window_results,
            start=1
        ):
            table = pd.DataFrame({
                "frequency":
                    result["frequency"],
                "psd":
                    result["psd"]
            })
            table.to_csv(
                folder /
                f"spectrum_{i:04d}.csv",
                index=False
            )
        print(
            "✓ Individual spectra saved"
        )

    # =====================================================
    def energy_statistics(self):
        energy = np.array([
            item["energy"]
            for item in
            self.window_results
        ])
        print()
        print("=" * 60)
        print("ENERGY STATISTICS")
        print("=" * 60)
        print()
        print(
            f"Minimum : {energy.min():.6f}"
        )
        print(
            f"Maximum : {energy.max():.6f}"
        )
        print(
            f"Mean    : {energy.mean():.6f}"
        )
        print(
            f"Median  : {np.median(energy):.6f}"
        )
        print(
            f"Std     : {energy.std():.6f}"
        )

    # =====================================================
    def plot_energy_timeseries(self):
        energy = np.array([
            item["energy"]
            for item in
            self.window_results
        ])
        time = self.statistics_table["timestamp"]
        plt.figure(
            figsize=(14,5)
        )
        plt.plot(
            time,
            energy,
            linewidth=1.5
        )
        plt.xlabel(
            "Time"
        )
        plt.ylabel(
            "Integrated energy"
        )
        plt.title(
            "Wave Energy Time Series"
        )
        plt.gcf().autofmt_xdate()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(
            self.output_fig /
            "energy_timeseries.png",
            dpi=300
        )
        plt.close()
        print(
            "✓ energy_timeseries.png"
        )

    # =====================================================
    def plot_peak_period_timeseries(self):
        periods = np.array([
            item["peak_period"]
            for item in
            self.window_results
        ])
        time = self.statistics_table["timestamp"]
        plt.figure(
            figsize=(14,5)
        )
        plt.plot(
            time,
            periods,
            linewidth=1,
            marker=".",
            markersize=3
        )
        plt.xlabel(
            "Time"
        )
        plt.ylabel(
            "Peak period (s)"
        )
        plt.title(
            "Peak Wave Period (wind-wave/swell band only)"
        )
        plt.gcf().autofmt_xdate()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(
            self.output_fig /
            "peak_period_timeseries.png",
            dpi=300
        )
        plt.close()
        print(
            "✓ peak_period_timeseries.png"
        )

    # =====================================================
    def plot_peak_frequency_timeseries(self):
        frequency = np.array([
            item["peak_frequency"]
            for item in
            self.window_results
        ])
        time = self.statistics_table["timestamp"]
        plt.figure(
            figsize=(14,5)
        )
        plt.plot(
            time,
            frequency,
            linewidth=1,
            marker=".",
            markersize=3
        )
        plt.xlabel(
            "Time"
        )
        plt.ylabel(
            "Peak frequency (Hz)"
        )
        plt.title(
            "Peak Wave Frequency (wind-wave/swell band only)"
        )
        plt.gcf().autofmt_xdate()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(
            self.output_fig /
            "peak_frequency_timeseries.png",
            dpi=300
        )
        plt.close()
        print(
            "✓ peak_frequency_timeseries.png"
        )

    # =====================================================
    def plot_window_example(self, index=0):
        if index >= len(self.windows):
            return
        signal = self.windows[index]
        t = np.arange(
            len(signal)
        ) / self.fs
        plt.figure(
            figsize=(14,5)
        )
        plt.plot(
            t,
            signal,
            linewidth=0.8
        )
        plt.xlabel(
            "Time (s)"
        )
        plt.ylabel(
            "Pressure anomaly (dbar)"
        )
        plt.title(
            f"Window {index + 1}"
        )
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(
            self.output_fig /
            "window_example.png",
            dpi=300
        )
        plt.close()
        print(
            "✓ window_example.png"
        )

    # =====================================================
    def compare_first_last(self):
        if len(self.window_results) < 2:
            return
        plt.figure(
            figsize=(12,6)
        )
        plt.semilogy(
            self.window_results[0]["frequency"],
            self.window_results[0]["psd"],
            label="First window"
        )
        plt.semilogy(
            self.window_results[-1]["frequency"],
            self.window_results[-1]["psd"],
            label="Last window"
        )
        plt.xlabel(
            "Frequency (Hz)"
        )
        plt.ylabel(
            "PSD"
        )
        plt.title(
            "First vs Last Spectrum"
        )
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(
            self.output_fig /
            "first_last_spectrum.png",
            dpi=300
        )
        plt.close()
        print(
            "✓ first_last_spectrum.png"
        )

    # =====================================================
    def frequency_resolution(self):
        df = (
            self.frequency[1]
            -
            self.frequency[0]
        )
        print()
        print("=" * 60)
        print("FREQUENCY RESOLUTION")
        print("=" * 60)
        print()
        print(
            f"Δf = {df:.6f} Hz"
        )
        print(
            f"Nyquist = {self.fs/2:.2f} Hz"
        )

    # =====================================================
    def save_peak_table(self):
        table = pd.DataFrame({
            "frequency":
                self.frequency[
                    self.peaks
                ],
            "period":
                1 /
                self.frequency[
                    self.peaks
                ],
            "psd":
                self.mean_psd[
                    self.peaks
                ]
        })
        table.to_csv(
            self.output_tab /
            "spectral_peaks.csv",
            index=False
        )
        print(
            "✓ spectral_peaks.csv"
        )

    # =====================================================
    def report(self):
        print()
        print("=" * 60)
        print("SPECTRAL REPORT")
        print("=" * 60)
        print()
        print(
            "Windows analysed :",
            len(self.windows)
        )
        print(
            "Dominant frequency:",
            f"{self.fp:.4f} Hz"
        )
        print(
            "Dominant period   :",
            f"{self.tp:.2f} s"
        )
        print(
            "Spectral peaks    :",
            len(self.peaks)
        )
        print(
            "Frequency range   :",
            f"{self.frequency[0]:.4f} - {self.frequency[-1]:.4f} Hz"
        )

    # =====================================================
    def run(self):
        self.information()
        self.split_into_windows()
        if len(self.windows) == 0:
            print("No windows to analyze. Exiting.")
            return
        self.compute_all_spectra()
        self.mean_spectrum()
        self.dominant_wave()
        self.save_window_statistics()
        self.save_summary()
        self.plot_mean_spectrum()
        self.plot_fft()
        self.plot_cumulative_energy()
        self.detect_spectral_peaks()
        self.plot_peak_spectrum()
        self.plot_window_example()
        self.compare_first_last()
        self.frequency_resolution()
        self.energy_statistics()
        self.plot_energy_timeseries()
        self.plot_peak_period_timeseries()
        self.plot_peak_frequency_timeseries()
        self.save_peak_table()
        self.save_mean_spectrum()
        self.save_all_spectra()
        self.report()
