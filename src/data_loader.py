"""
data_loader.py — чтение CSV.
- правильные типы дат/чисел
- удаляем точные дубликаты платежей
- отсекаем «будущее» по as-of
"""

from __future__ import annotations
import pandas as pd
from pandas import DataFrame
from src.config import ORDERS_CSV, PAYMENTS_CSV, PLAN_CSV, DATA_AS_OF


def load_orders() -> DataFrame:
    """orders.csv: даты, суммы, единый тип order_id."""
    df = pd.read_csv(ORDERS_CSV, parse_dates=["created_at", "put_at", "closed_at"])
    df["order_id"]   = pd.to_numeric(df["order_id"], errors="coerce").astype("Int64")
    df["issued_sum"] = pd.to_numeric(df.get("issued_sum"), errors="coerce")
    return df


def load_payments() -> DataFrame:
    """payments.csv: чистка дублей, типы, отрезаем строки позже as-of."""
    df = pd.read_csv(PAYMENTS_CSV)
    df["order_id"] = pd.to_numeric(df["order_id"], errors="coerce").astype("Int64")
    df["paid_at"]  = pd.to_datetime(df["paid_at"], errors="coerce")
    df["paid_sum"] = pd.to_numeric(df.get("paid_sum"), errors="coerce")

    df = df.drop_duplicates(subset=["order_id", "paid_at", "paid_sum"])
    df = df.dropna(subset=["order_id", "paid_at", "paid_sum"])
    df = df[df["paid_at"] <= DATA_AS_OF]
    return df


def load_plan() -> DataFrame:
    """plan.csv: накопительный план, типы, отрезаем строки позже as-of."""
    df = pd.read_csv(PLAN_CSV)
    df["order_id"]       = pd.to_numeric(df["order_id"], errors="coerce").astype("Int64")
    df["plan_at"]        = pd.to_datetime(df["plan_at"], errors="coerce")
    df["plan_sum_total"] = pd.to_numeric(df.get("plan_sum_total"), errors="coerce")

    df = df.dropna(subset=["order_id", "plan_at"])
    df = df[df["plan_at"] <= DATA_AS_OF]
    return df
