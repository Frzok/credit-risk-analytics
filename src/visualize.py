"""
visualize.py — минималистичные и понятные графики.
"""

from __future__ import annotations
import matplotlib.pyplot as plt
from pandas import DataFrame
from src.config import FIGURES_DIR


def plot_overdue_rate_active(clients_month: DataFrame) -> str:
    path = FIGURES_DIR / "overdue_rate_active.png"
    plt.figure()
    plt.plot(clients_month["month_end"], clients_month["overdue_rate_active"])
    plt.title("Как менялась доля клиентов с долгом по месяцам (снимок на конец месяца)")
    plt.xlabel("Месяц")
    plt.ylabel("Доля клиентов с долгом")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True, alpha=0.3)
    plt.savefig(path, dpi=150)
    plt.close()
    return str(path)


def plot_overdue_rate_instalments(instalment_month: DataFrame) -> str:
    path = FIGURES_DIR / "overdue_rate_instalments.png"
    plt.figure()
    plt.plot(instalment_month["month"], instalment_month["overdue_rate"])
    plt.title("Какая доля плановых платежей входила в просрочку в месяц их наступления")
    plt.xlabel("Месяц")
    plt.ylabel("Доля просроченных плановых платежей")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True, alpha=0.3)
    plt.savefig(path, dpi=150)
    plt.close()
    return str(path)
