from pathlib import Path

from src.config import (
    RAW_DIR,
    PROCESSED_DIR,
    FIGURES_DIR,
    TABLES_DIR,
    REPORTS_DIR,
    LOGS_DIR
)


class ProjectManager:

    def create_folders(self):

        folders = [
            RAW_DIR,
            PROCESSED_DIR,
            FIGURES_DIR,
            TABLES_DIR,
            REPORTS_DIR,
            LOGS_DIR
        ]

        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)

        print("✓ Структура проекта проверена.")

    def check_file(self, filename):

        file = RAW_DIR / filename

        if not file.exists():
            raise FileNotFoundError(file)

        print("✓ Файл найден.")

        print(f"\nИмя: {file.name}")

        print(f"Размер: {file.stat().st_size/1024/1024:.2f} MB")

        return file