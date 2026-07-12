import pandas as pd


class DataPreparation:

    def __init__(self, reader):

        self.reader = reader
        self.df = reader.df.copy()

    def derive_channels(self):

        print("\nВычисление производных каналов...")

        self.reader.rsk.deriveseapressure()
        self.reader.rsk.derivedepth()

        self.reader.rsk.readdata()

        self.df = pd.DataFrame(self.reader.rsk.data)

        print("✓ Производные каналы рассчитаны.")

    def sampling_information(self):

        dt = self.df["timestamp"].diff().dt.total_seconds()

        print("\nПроверка временного шага")

        print(f"Средний шаг: {dt.mean():.6f} сек")

        print(f"Минимальный: {dt.min():.6f}")

        print(f"Максимальный: {dt.max():.6f}")

        print(f"Частота: {1 / dt.mean():.3f} Hz")

    def show_columns(self):

        print("\nКолонки DataFrame")

        print(self.df.columns)

    def export(self):

        self.df.to_csv(
            "data/processed/processed_data.csv",
            index=False
        )

        print("\n✓ CSV сохранён.")

    def run(self):

        self.derive_channels()

        self.show_columns()

        self.sampling_information()

        self.export()