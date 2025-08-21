"""
main.py — один запуск: читаем → чекаем → считаем → визуализируем → сохраняем → печатаем выводы.
"""

from __future__ import annotations
from src.data_loader import load_orders, load_payments, load_plan
from src.quality import print_basic_quality, make_plan_monotonic
from src.overdue import cumulative_payments, overdue_on_plan_dates, monthly_instalment_view
from src.snapshots import month_end_snapshots, monthly_clients_view
from src.visualize import plot_overdue_rate_active, plot_overdue_rate_instalments
from src.report import save_tables, print_summary


def run() -> None:
    print("Шаг 1/6: загрузка данных...")
    orders   = load_orders()
    payments = load_payments()
    plan     = load_plan()

    print("Шаг 2/6: проверки качества...")
    print_basic_quality(orders, payments, plan)
    plan = make_plan_monotonic(plan)

    print("Шаг 3/6: считаем просрочку на даты плановых платежей...")
    payments_cum = cumulative_payments(payments)
    overdue_df   = overdue_on_plan_dates(plan, payments_cum)
    instalment_month = monthly_instalment_view(overdue_df)
    print(f"  готово: {len(overdue_df):,} строк, месяцев: {instalment_month['month'].nunique()}")

    print("Шаг 4/6: строим снимки по клиентам (конец месяца, активные)...")
    snaps = month_end_snapshots(orders, plan, payments_cum)
    clients_month = monthly_clients_view(snaps)
    print(f"  готово: снимков {len(snaps):,}, месяцев: {clients_month['month_end'].nunique()}")

    print("Шаг 5/6: сохраняем графики...")
    fig1 = plot_overdue_rate_active(clients_month)
    fig2 = plot_overdue_rate_instalments(instalment_month)
    print("  сохранено:", fig1, "и", fig2)

    print("Шаг 6/6: сохраняем таблицы и печатаем краткое резюме...")
    save_tables(instalment_month, clients_month)
    print_summary(instalment_month, clients_month)


if __name__ == "__main__":
    run()
