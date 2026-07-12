from src.reader import RBRReader
from src.quality import QualityControl
from src.preprocessing import DataPreparation
from src.gaps import GapDetector
from src.segmentation import Segmenter
from src.data_cleaner import DataCleaner

from src.waves_preprocessing import WavePreprocessor
from src.wave_overview import WaveAnalysis
from src.wave_spectra import WaveSpectra
from src.storm_analysis import StormAnalysis
from src.windwaveanalysis import WindWaveAnalysis
from src.temperature_analysis import TemperatureAnalysis

from src.inspector import RSKInspector
from src.summary_statistics import SummaryStatistics

def main():

    # =====================================================
    # Reading RBR file
    # =====================================================

    reader = RBRReader(
        "data/raw/214818_20260625_1432.rsk"
    )

    spectra = None
    storm = None
    wind = None

    try:

        reader.open()
        reader.load()

        # =====================================================
        # Quality Control
        # =====================================================

        qc = QualityControl(
            reader.df
        )

        qc.run()

        # =====================================================
        # Basic preprocessing
        # =====================================================

        prep = DataPreparation(
            reader
        )

        prep.run()

        # =====================================================
        # Gap detection
        # =====================================================

        gaps = GapDetector(
            reader.df
        )

        gaps.run()

        # =====================================================
        # Segmentation
        # =====================================================

        segmenter = Segmenter(
            reader.df
        )

        segmenter.run()

        # =====================================================
        # Data cleaning
        # =====================================================

        cleaner = DataCleaner(
            segmenter.segments
        )

        cleaner.run()

        clean_df = cleaner.clean_df

        # =====================================================
        # Wave preprocessing
        # =====================================================

        wave = WavePreprocessor(
            clean_df
        )

        wave.run()

        wave_df = wave.df

        # =====================================================
        # Wave overview
        # =====================================================

        overview = WaveAnalysis(
            wave_df
        )

        overview.run()

        # =====================================================
        # Spectral analysis
        # =====================================================

        spectra = WaveSpectra(
            wave_df
        )

        spectra.run()

        # =====================================================
        # Storm analysis
        # =====================================================

        storm = StormAnalysis(
            spectra
        )

        storm.run()

        # =====================================================
        # Wind-Wave analysis
        # =====================================================

        wind = WindWaveAnalysis(
            spectra=spectra,
            storm=storm,
            wind_csv="data/wind/wind.csv"
        )

        wind.run()

        # =====================================================
        # Temperature analysis
        # =====================================================

        temperature = TemperatureAnalysis(
            clean_df
        )

        temperature.run()

        # =====================================================
        # Instrument information
        # =====================================================

        inspector = RSKInspector(
            reader
        )

        inspector.run()

    finally:

        if spectra is not None and storm is not None and wind is not None:

            summary = SummaryStatistics(
                reader=reader,
                spectra=spectra,
                storm=storm,
                wind=wind
            )

            summary.run()

        # =====================================================
        # Close RSK
        # =====================================================

        reader.close()


if __name__ == "__main__":

    main()