"""
snapshots.py — «снимки» на конец каждого месяца: доля клиентов с долгом среди активных.
Активный на дату d: put_at <= d и (closed_at > d или closed_at отсутствует).
"""

from __future__ import annotations
import pandas as pd
from pandas import DataFrame
from src.config import DATA_AS_OF


def build_month_grid(plan: DataFrame) -> DataFrame:
    """Сетка: конец каждого месяца от min(plan_at) до месяца DATA_AS_OF."""
    start = plan["plan_at"].min().to_period("M").start_time
    end   = DATA_AS_OF.to_period("M").end_time
    months = pd.date_range(start, end, freq="ME")  # MonthEnd
    return pd.DataFrame({"month_end": months})


def is_active_on(orders: DataFrame, date: pd.Timestamp) -> DataFrame:
    """Активный кредит на дату: put_at <= date и (closed_at > date или NaT)."""
    closed = orders["closed_at"].fillna(pd.Timestamp.max)
    mask = (orders["put_at"] <= date) & (closed > date)
    return orders.loc[mask, ["order_id"]].copy()


def month_end_snapshots(
    orders: DataFrame,
    plan: DataFrame,
    payments_cum: DataFrame,
    sample_n: int | None = None
) -> DataFrame:
    """
    Для каждого order_id и каждого month_end считаем:
      - план к дате (asof)
      - факт к дате (asof)
      - долг и признак просрочки
    Помечаем активные заявки на дату.
    """
    calendar  = build_month_grid(plan)
    plan_asof = plan.sort_values(["order_id", "plan_at"])[["order_id", "plan_at", "plan_sum_total"]]
    pay_asof  = payments_cum.sort_values(["order_id", "paid_at"])[["order_id", "paid_at", "paid_cum"]]

    order_ids = plan_asof["order_id"].unique()
    if sample_n is not None:
        order_ids = order_ids[:sample_n]

    snapshots = []

    for idx, oid in enumerate(order_ids, 1):
        if idx % 2000 == 0:
            print(f"  обработано заявок: {idx}/{len(order_ids)}")

        psub = plan_asof[plan_asof["order_id"] == oid].rename(columns={"plan_at": "date"})
        fsub = pay_asof [pay_asof ["order_id"] == oid].rename(columns={"paid_at": "date"})

        left = calendar.rename(columns={"month_end": "date"})
        snap_plan = pd.merge_asof(left, psub[["date", "plan_sum_total"]], on="date", direction="backward")
        snap_pay  = pd.merge_asof(left, fsub[["date", "paid_cum"]],      on="date", direction="backward")

        snap = pd.DataFrame({
            "order_id": oid,
            "month_end": left["date"],
            "plan_sum_total": snap_plan["plan_sum_total"].fillna(0),
            "paid_cum":      snap_pay["paid_cum"].fillna(0),
        })
        snapshots.append(snap)

    snaps = pd.concat(snapshots, ignore_index=True)
    snaps["debt"] = snaps["plan_sum_total"] - snaps["paid_cum"]
    snaps["is_overdue"] = snaps["debt"] > 0

    # помечаем активных на дату
    marks = []
    for d in snaps["month_end"].drop_duplicates():
        active = is_active_on(orders, d)
        if not active.empty:
            active["month_end"] = d
            active["active"] = True
            marks.append(active)

    if marks:
        active_df = pd.concat(marks, ignore_index=True)
        snaps = snaps.merge(active_df, on=["order_id", "month_end"], how="left")
    else:
        snaps["active"] = False

    snaps["active"] = snaps["active"].fillna(False).infer_objects(copy=False)

    return snaps


def monthly_clients_view(snaps: DataFrame) -> DataFrame:
    """Агрегация по активным клиентам на конец месяца."""
    active = snaps[snaps["active"]].copy()
    agg = (
        active.groupby("month_end", as_index=False)
              .agg(
                  active_clients=("order_id", "nunique"),
                  overdue_active=("is_overdue", "sum"),
                  total_debt_active=("debt", lambda x: x[x > 0].sum()),
                  avg_debt_overdue_active=("debt", lambda x: x[x > 0].mean()),
              )
    )
    agg["overdue_rate_active"] = agg["overdue_active"] / agg["active_clients"]
    return agg
