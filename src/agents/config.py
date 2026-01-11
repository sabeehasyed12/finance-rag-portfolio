from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class AgentConfig:
    repo_root: Path = Path(".")
    dbt_dir: Path = Path("dbt")
    profiles_dir: Path = Path("dbt")
    target: str = "dev"

    reports_dir: Path = Path("artifacts/reports")
    logs_dir: Path = Path("artifacts/logs")

    duckdb_path: Path = Path("dbt/dev.duckdb")

    gold_schema: str = "main_gold"
    silver_schema: str = "main_silver"
    bronze_schema: str = "main_bronze"

    max_volume_drop_pct: float = 0.35
    max_volume_spike_pct: float = 0.60
    max_freshness_days: int = 2
