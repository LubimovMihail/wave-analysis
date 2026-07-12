from pathlib import Path

import pandas as pd
import pyrsktools


class RBRReader:
    """
    Чтение файлов RBR (.rsk)
    """

    def __init__(self, filepath: str):

        self.filepath = Path(filepath)

        if not self.filepath.exists():
            raise FileNotFoundError(self.filepath)

        self.rsk = None
        self.df = None

    def open(self):

        print("Открытие файла...")

        self.rsk = pyrsktools.RSK(str(self.filepath))

        self.rsk.open()

        print("✓ Файл успешно открыт.")

    def close(self):

        if self.rsk is not None:
            self.rsk.close()

    def load(self):

        print("\nЧтение данных...")

        self.rsk.readdata()

        print("✓ Данные загружены.")

        self.df = pd.DataFrame(self.rsk.data)

        print(f"\nКоличество измерений: {len(self.df):,}")

        print("\nПервые строки:")

        print(self.df.head())

        return self.df