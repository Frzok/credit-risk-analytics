"""
quality.py — быстрые проверки качества и приведение плана к неубыванию.
"""

from __future__ import annotations
from pandas import DataFrame


def print_basic_quality(orders: DataFrame, payments: DataFrame, plan: DataFrame) -> None:
    """Мини-отчёт: дубликаты и пропуски в ключевых колонках."""
    print(" Проверки качества данных")
    print(" Дубликаты:")
    print("  orders by order_id:", orders.duplicated(["order_id"]).sum())
    print("  payments by (order_id, paid_at, paid_sum):",
          payments.duplicated(["order_id", "paid_at", "paid_sum"]).sum())
    print("  plan by (order_id, plan_at):", plan.duplicated(["order_id", "plan_at"]).sum())

    print("\n Пропуски (ключевые):")
    print("  orders:\n", orders[["order_id", "put_at", "closed_at", "issued_sum"]].isna().sum())
    print("  payments:\n", payments[["order_id", "paid_at", "paid_sum"]].isna().sum())
    print("  plan:\n", plan[["order_id", "plan_at", "plan_sum_total"]].isna().sum())
    print()


def make_plan_monotonic(plan: DataFrame) -> DataFrame:
    """
    Делаем неубывающим по каждой заявке.
    """
    plan = plan.sort_values(["order_id", "plan_at"]).copy()
    plan["plan_sum_total"] = plan.groupby("order_id")["plan_sum_total"].cummax()
    return plan
