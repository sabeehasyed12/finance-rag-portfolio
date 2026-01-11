from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import duckdb

from src.agents.config import AgentConfig

@dataclass
class ValidationResult:
    status: str
    started_at: str
    finished_at: str
    dbt_test_summary: Dict[str, Any]
    volume_checks: List[Dict[str, Any]]
    freshness_checks: List[Dict[str, Any]]
    likely_causes: List[str]

def _run_cmd(cmd: List[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)

def _run_dbt_tests(cfg: AgentConfig) -> Dict[str, Any]:
    started = datetime.utcnow()
    cmd = [
        "dbt",
        "test",
        "--project-dir", str(cfg.dbt_dir),
        "--profiles-dir", str(cfg.profiles_dir),
        "--target", cfg.target,
    ]
    p = _run_cmd(cmd, cfg.repo_root)
    finished = datetime.utcnow()

    return {
        "command": " ".join(cmd),
        "returncode": p.returncode,
        "stdout_tail": p.stdout[-4000:],
        "stderr_tail": p.stderr[-4000:],
        "started_at": started.isoformat() + "Z",
        "finished_at": finished.isoformat() + "Z",
    }

def _volume_and_freshness_checks(cfg: AgentConfig) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    con = duckdb.connect(str(cfg.duckdb_path))

    volume_checks: List[Dict[str, Any]] = []
    freshness_checks: List[Dict[str, Any]] = []

    tables = [
        f"{cfg.gold_schema}.gold_transaction_facts",
        f"{cfg.gold_schema}.gold_daily_revenue",
        f"{cfg.gold_schema}.gold_churn",
        f"{cfg.gold_schema}.gold_mrr",
    ]

    for t in tables:
        try:
            q = f"""
            with daily as (
              select
                cast(coalesce(transaction_date, revenue_date, churn_date, month) as date) as d,
                count(*) as n
              from {t}
              group by 1
            ),
            latest as (
              select d, n
              from daily
              order by d desc
              limit 2
            )
            select * from latest
            """
            rows = con.execute(q).fetchall()
            if len(rows) < 2:
                volume_checks.append({"table": t, "status": "skip", "reason": "not enough history"})
                continue

            d0, n0 = rows[0]
            d1, n1 = rows[1]
            if n1 == 0:
                volume_checks.append({"table": t, "status": "warn", "reason": "previous day count was 0"})
                continue

            pct = (n0 - n1) / n1
            status = "pass"
            if pct < -cfg.max_volume_drop_pct:
                status = "fail"
            elif pct > cfg.max_volume_spike_pct:
                status = "warn"

            volume_checks.append({
                "table": t,
                "latest_date": str(d0),
                "latest_count": int(n0),
                "prev_date": str(d1),
                "prev_count": int(n1),
                "pct_change": float(pct),
                "status": status,
            })

        except Exception as e:
            volume_checks.append({"table": t, "status": "error", "error": str(e)})

    for t in tables:
        try:
            q = f"""
            select
              max(coalesce(transaction_date, revenue_date, churn_date, month)) as max_dt
            from {t}
            """
            max_dt = con.execute(q).fetchone()[0]
            if max_dt is None:
                freshness_checks.append({"table": t, "status": "fail", "reason": "no rows"})
                continue

            q2 = "select current_date"
            today = con.execute(q2).fetchone()[0]
            days_old = (today - max_dt).days

            status = "pass" if days_old <= cfg.max_freshness_days else "fail"
            freshness_checks.append({
                "table": t,
                "max_date": str(max_dt),
                "days_old": int(days_old),
                "status": status,
            })
        except Exception as e:
            freshness_checks.append({"table": t, "status": "error", "error": str(e)})

    con.close()
    return volume_checks, freshness_checks

def run(cfg: AgentConfig) -> ValidationResult:
    started_at = datetime.utcnow().isoformat() + "Z"

    dbt = _run_dbt_tests(cfg)
    volume_checks, freshness_checks = _volume_and_freshness_checks(cfg)

    likely_causes: List[str] = []
    if dbt["returncode"] != 0:
        likely_causes.append("dbt tests failed, likely schema or data quality regression in upstream models")
    if any(x.get("status") == "fail" for x in volume_checks):
        likely_causes.append("volume dropped sharply, likely missing ingest or incremental filter issue")
    if any(x.get("status") == "fail" for x in freshness_checks):
        likely_causes.append("freshness failure, likely pipeline did not load newest partition")

    status = "pass"
    if dbt["returncode"] != 0 or any(x.get("status") == "fail" for x in volume_checks + freshness_checks):
        status = "fail"
    elif any(x.get("status") in ["warn", "error"] for x in volume_checks + freshness_checks):
        status = "warn"

    finished_at = datetime.utcnow().isoformat() + "Z"

    return ValidationResult(
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        dbt_test_summary=dbt,
        volume_checks=volume_checks,
        freshness_checks=freshness_checks,
        likely_causes=likely_causes,
    )

def write_report(cfg: AgentConfig, result: ValidationResult) -> Path:
    cfg.reports_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.reports_dir / "validation_report.json"
    out.write_text(json.dumps(result.__dict__, indent=2), encoding="utf-8")
    return out
