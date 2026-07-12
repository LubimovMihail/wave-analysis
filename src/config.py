from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"

PROCESSED_DIR = DATA_DIR / "processed"

OUTPUT_DIR = PROJECT_ROOT / "output"

FIGURES_DIR = OUTPUT_DIR / "figures"

TABLES_DIR = OUTPUT_DIR / "tables"

REPORTS_DIR = OUTPUT_DIR / "reports"

LOGS_DIR = OUTPUT_DIR / "logs"