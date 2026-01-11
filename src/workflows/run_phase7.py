from __future__ import annotations

from datetime import datetime

from src.agents.config import AgentConfig
from src.agents import data_validation_agent, financial_analyst_agent, compliance_agent

def main() -> None:
    cfg = AgentConfig()
    cfg.reports_dir.mkdir(parents=True, exist_ok=True)
    cfg.logs_dir.mkdir(parents=True, exist_ok=True)

    print("Phase 7 workflow start", datetime.utcnow().isoformat() + "Z")

    v = data_validation_agent.run(cfg)
    v_path = data_validation_agent.write_report(cfg, v)
    print("wrote", v_path)

    f = financial_analyst_agent.run(cfg)
    f_path = financial_analyst_agent.write_report(cfg, f)
    print("wrote", f_path)

    c = compliance_agent.run(cfg)
    c_path = compliance_agent.write_report(cfg, c)
    print("wrote", c_path)

    print("Phase 7 workflow complete")

if __name__ == "__main__":
    main()
