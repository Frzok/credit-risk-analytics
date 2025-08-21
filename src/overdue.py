"""
overdue.py — просрочка «по сумме» на даты плановых платежей и месячная агрегация.
Определение: debt = plan_sum_total(t) - paid_cum(t), просрочка если debt > 0.
"""

from __future__ import annotations
import pandas as pd
from pandas import DataFrame
from src.config import DATA_AS_OF


def cumulative_payments(payments: DataFrame) -> DataFrame:
    """Добавляет paid_cum — накопленную сумму фактических платежей внутри заявки."""
    payments = payments.sort_values(["order_id", "paid_at"]).copy()
    payments["paid_cum"] = payments.groupby("order_id")["paid_sum"].cumsum()
    return payments.reset_index(drop=True)


def overdue_on_plan_dates(plan: DataFrame, payments_cum: DataFrame) -> DataFrame:
    results = []

    for oid, plan_sub in plan.groupby("order_id", sort=False):
        plan_sub = plan_sub.sort_values("plan_at").reset_index(drop=True)

        pay_sub = payments_cum.loc[payments_cum["order_id"] == oid].sort_values("paid_at").reset_index(drop=True)
        if pay_sub.empty:
            pay_sub = pd.DataFrame({"paid_at": [pd.Timestamp.min], "paid_cum": [0.0]})

        merged = pd.merge_asof(
            left=plan_sub,
            right=pay_sub,
            left_on="plan_at",
            right_on="paid_at",
            direction="backward",
        )
        merged["order_id"] = oid
        merged["paid_cum"] = merged["paid_cum"].fillna(0)
        merged["debt"] = merged["plan_sum_total"] - merged["paid_cum"]
        merged["is_overdue"] = merged["debt"] > 0
        results.append(merged)

    out = pd.concat(results, ignore_index=True)
    out["month"] = out["plan_at"].values.astype("datetime64[M]")
    return out


def monthly_instalment_view(overdue_df: DataFrame) -> DataFrame:
    """
    Месячная динамика по «инстансам плана» (месяц наступления платежа).
    Ограничиваемся месяцами не позже месяца DATA_AS_OF.
    """
    df = overdue_df.copy()
    if "month" not in df.columns:
        df["month"] = df["plan_at"].values.astype("datetime64[M]")

    agg = (
        df.groupby("month", as_index=False)
          .agg(
              instalments=("order_id", "count"),
              overdue_instalments=("is_overdue", "sum"),
              total_debt=("debt", lambda x: x[x > 0].sum()),
              avg_debt_overdue=("debt", lambda x: x[x > 0].mean()),
          )
    )

    last_month = DATA_AS_OF.to_period("M").to_timestamp()
    agg = agg[agg["month"] <= last_month].copy()
    agg["overdue_rate"] = agg["overdue_instalments"] / agg["instalments"]
    return agg

def mark_overdue(instalments: pd.DataFrame, payments_cum: pd.DataFrame) -> pd.DataFrame:
    """
    Определение просрочки:
    Просрочка — это нарушение должником сроков и/или объёмов исполнения обязательств,
    предусмотренных договором (графиком платежей).

    В терминах данных:
    - сравниваем накопленный план (plan_sum_total) и накопленный факт (paid_cum);
    - если на дату факт < план → есть долг → просрочка;
    - если должник догнал позже → просрочка фиксируется только до момента догоняния.
    """
    merged = (instalments
              .merge(payments_cum, on=["order_id", "plan_at"], how="left")
              .fillna({"paid_cum": 0}))

    merged["debt"] = merged["plan_sum_total"] - merged["paid_cum"]
    merged["overdue"] = merged["debt"] > 0
    return merged

