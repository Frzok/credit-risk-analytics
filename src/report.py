"""
report.py — сохраняем таблицы и печатаем короткие выводы.
"""

from __future__ import annotations
from pandas import DataFrame
from src.config import TABLES_DIR


def save_tables(instalment_month: DataFrame, clients_month: DataFrame) -> None:
    instalment_month.to_csv(TABLES_DIR / "instalment_month.csv", index=False)
    clients_month.to_csv(TABLES_DIR / "clients_month.csv", index=False)


def print_summary(instalment_month: DataFrame, clients_month: DataFrame) -> None:
    """
    Финальное резюме.
    Числа подтягиваем из агрегатов, чтобы не было «захардкоженных» процентов.
    """

    # --- метрики по клиентам ---
    first_rate = last_rate = None
    if not clients_month.empty and "overdue_rate_active" in clients_month.columns:
        first_rate = clients_month["overdue_rate_active"].iloc[0]
        last_rate = clients_month["overdue_rate_active"].iloc[-1]

    # --- метрики по плановым платежам ---
    peak_rate = None
    peak_month = None
    if not instalment_month.empty and "overdue_rate" in instalment_month.columns:
        idx = instalment_month["overdue_rate"].idxmax()
        row = instalment_month.loc[idx]
        peak_rate = row["overdue_rate"]
        peak_month = row["month"].strftime("%Y-%m")

    print("\n Итоги анализа просрочек\n")

    # определение просрочки
    print(" Просрочку считаем по графику: если на дату факт < план — это просрочка.")
    print("   Если клиент догнал позже — долг обнуляется, просрочка снимается.\n")

    if first_rate is not None and last_rate is not None:
        print(f"🔹 По клиентам: доля с долгом выросла с {first_rate:.1%} до {last_rate:.1%}.")
    if peak_rate is not None and peak_month is not None:
        print(f"🔹 По плановым платежам: самый тяжёлый месяц — {peak_month}, "
              f"просрочено до {peak_rate:.1%}.")

    print("🔹 Честно обрезаем данные по дате актуальности (08.12.2022), "
          "чтобы не накрутить просрочку там, где выгрузка уже закончилась.")

    print("\n Учтённые несостыковки в данных:")
    print("- closed_at часто пустой → считаем заявку активной")
    print("- plan_sum_total накопительный → долг = план − факт")
    print("- платежи после 2022-12-08 отбрасываем")
    print("- заявки без платежей трактуем как полная просрочка")

    print("\n Готово! Можно смотреть графики и таблицы.\n")
