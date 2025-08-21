"""
config.py — все пути и общие настройки в одном месте.
Меняешь здесь — работает везде.
"""

from pathlib import Path
import pandas as pd

# Укажи путь к данным под свою машину:
DATA_DIR = Path(r"C:\Users\anige\PycharmProjects\Devim\Data")

# Файлы-источники
ORDERS_CSV   = DATA_DIR / "orders.csv"
PAYMENTS_CSV = DATA_DIR / "payments.csv"
PLAN_CSV     = DATA_DIR / "plan.csv"

# Куда складывать результаты
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR   = PROJECT_ROOT / "output"
TABLES_DIR   = OUTPUT_DIR / "tables"
FIGURES_DIR  = OUTPUT_DIR / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Дата актуальности выгрузки (всё позже игнорируем)
DATA_AS_OF_STR = "2022-12-08"
DATA_AS_OF     = pd.to_datetime(DATA_AS_OF_STR)
