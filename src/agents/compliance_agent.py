from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List

import duckdb

from src.agents.config import AgentConfig

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b(\+?\d[\d\s().-]{7,}\d)\b")

PII_COLUMN_HINTS = {
    "full_name",
    "name",
    "email",
    "phone",
    "address",
}

@dataclass
class ComplianceResult:
    status: str
    checked_objects: List[str]
    findings: List[Dict[str, Any]]

def run(cfg: AgentConfig) -> ComplianceResult:
    con = duckdb.connect(str(cfg.duckdb_path))

    schemas_to_check = [cfg.gold_schema, "main_platinum"]
    findings: List[Dict[str, Any]] = []
    checked: List[str] = []

    for schema in schemas_to_check:
        tables = con.execute(
            f"""
            select table_name
            from information_schema.tables
            where table_schema = '{schema}'
            """
        ).fetchall()

        for (table_name,) in tables:
            full = f"{schema}.{table_name}"
            checked.append(full)

            cols = con.execute(
                f"""
                select column_name
                from information_schema.columns
                where table_schema = '{schema}'
                  and table_name = '{table_name}'
                """
            ).fetchall()
            col_names = [c[0] for c in cols]

            suspicious_cols = [c for c in col_names if c.lower() in PII_COLUMN_HINTS]
            if suspicious_cols:
                findings.append({
                    "object": full,
                    "type": "pii_column_name",
                    "evidence": suspicious_cols,
                    "severity": "fail",
                })
                continue

            sample_cols = [c for c in col_names if "id" not in c.lower()][:6]
            if not sample_cols:
                continue

            try:
                sample = con.execute(
                    f"select {', '.join(sample_cols)} from {full} limit 200"
                ).fetchall()
                joined = " ".join(str(x) for row in sample for x in row if x is not None)

                email_hit = EMAIL_RE.search(joined) is not None
                phone_hit = PHONE_RE.search(joined) is not None

                if email_hit or phone_hit:
                    findings.append({
                        "object": full,
                        "type": "pii_value_pattern",
                        "evidence": {
                            "email_detected": email_hit,
                            "phone_detected": phone_hit,
                            "sampled_columns": sample_cols,
                        },
                        "severity": "warn",
                    })
            except Exception as e:
                findings.append({
                    "object": full,
                    "type": "scan_error",
                    "evidence": str(e),
                    "severity": "warn",
                })

    con.close()

    status = "pass"
    if any(f["severity"] == "fail" for f in findings):
        status = "fail"
    elif findings:
        status = "warn"

    return ComplianceResult(status=status, checked_objects=checked, findings=findings)

def write_report(cfg: AgentConfig, result: ComplianceResult) -> Path:
    cfg.reports_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.reports_dir / "compliance_report.json"
    out.write_text(json.dumps(result.__dict__, indent=2), encoding="utf-8")
    return out
