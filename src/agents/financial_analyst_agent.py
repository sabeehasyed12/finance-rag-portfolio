from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional

import duckdb

from src.agents.config import AgentConfig


@dataclass
class FinanceInsight:
    status: str
    as_of_date: str
    headline: str
    key_metrics: Dict[str, Any]
    drivers: List[Dict[str, Any]]
    notes: List[str]


def run(cfg: AgentConfig) -> FinanceInsight:
    """
    Deterministic daily finance summary.

    Reads from:
      - {cfg.gold_schema}.gold_daily_revenue

    Expected columns (based on your current model output):
      - revenue_date
      - net_revenue
      - gross_transaction_amount
      - total_refunded_amount
      - gold_loaded_at (ignored)
    """
    con = duckdb.connect(str(cfg.duckdb_path))

    q = f"""
    with d as (
      select *
      from {cfg.gold_schema}.gold_daily_revenue
      order by revenue_date desc
      limit 2
    )
    select
      max(case when rn = 1 then revenue_date end) as latest_date,
      max(case when rn = 1 then net_revenue end) as latest_net,
      max(case when rn = 2 then net_revenue end) as prev_net,
      max(case when rn = 1 then gross_transaction_amount end) as latest_gross,
      max(case when rn = 1 then total_refunded_amount end) as latest_refunds
    from (
      select *, row_number() over(order by revenue_date desc) as rn
      from d
    )
    """

    row = con.execute(q).fetchone()
    if row is None or row[0] is None:
        con.close()
        return FinanceInsight(
            status="fail",
            as_of_date="unknown",
            headline="No daily revenue data found",
            key_metrics={},
            drivers=[],
            notes=["gold_daily_revenue missing or empty"],
        )

    latest_date, latest_net, prev_net, latest_gross, latest_refunds = row

    # Compute day-over-day change on net revenue
    pct_change: Optional[float] = None
    if prev_net is not None and float(prev_net) != 0.0:
        pct_change = float((latest_net - prev_net) / prev_net)

    # Headline logic
    if pct_change is not None:
        if pct_change < -0.10:
            headline = f"Net revenue down {pct_change:.1%} versus prior day"
        elif pct_change > 0.10:
            headline = f"Net revenue up {pct_change:.1%} versus prior day"
        else:
            headline = "Net revenue stable versus prior day"
    else:
        headline = "Net revenue reported, but prior day baseline missing"

    # Refund rate (amount-based)
    refund_rate: Optional[float] = None
    if latest_gross is not None and float(latest_gross) != 0.0:
        refund_rate = float(latest_refunds / latest_gross)

    drivers: List[Dict[str, Any]] = []
    notes: List[str] = []

    if refund_rate is not None and refund_rate > 0.05:
        drivers.append(
            {"driver": "Refund pressure", "detail": f"Refund rate {refund_rate:.2%} is elevated"}
        )

    key_metrics: Dict[str, Any] = {
        "latest_date": str(latest_date),
        "net_revenue": float(latest_net),
        "gross_transaction_amount": float(latest_gross),
        "total_refunded_amount": float(latest_refunds),
        "net_revenue_change_pct": pct_change,
        "refund_rate_amount_based": refund_rate,
    }

    con.close()

    status = "pass"
    if drivers:
        status = "warn"

    return FinanceInsight(
        status=status,
        as_of_date=str(latest_date),
        headline=headline,
        key_metrics=key_metrics,
        drivers=drivers,
        notes=notes,
    )


def write_report(cfg: AgentConfig, result: FinanceInsight) -> Path:
    cfg.reports_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.reports_dir / "daily_finance_insights.json"
    out.write_text(json.dumps(result.__dict__, indent=2), encoding="utf-8")
    return out
