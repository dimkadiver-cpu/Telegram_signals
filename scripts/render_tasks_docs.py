#!/usr/bin/env python3
"""Renderizza una vista sintetica di TASKS.md a partire da docs/tasks/master.yaml.

Nota: script minimale senza dipendenze esterne (richiede PyYAML installato).
"""

from pathlib import Path
import sys

try:
    import yaml
except Exception as exc:  # pragma: no cover
    print(f"Errore: PyYAML non disponibile ({exc}). Installa con: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "docs" / "tasks" / "master.yaml"
TASKS_MD = ROOT / "TASKS.md"


def main() -> int:
    data = yaml.safe_load(MASTER.read_text(encoding="utf-8"))
    lines = [
        "# TASKS – Sistema Telegram Signals (vista sintetica)",
        "",
        "> Questo file è una **vista leggibile**. La fonte autoritativa di task/stato/check è `docs/tasks/master.yaml`.",
        "",
        "## Regole",
        "- Modificare task, stati e dipendenze **solo** in `docs/tasks/master.yaml`.",
        "- Usare `agents/UNIFIED_AGENT_PROMPT.md` come istruzione operativa unica per gli agenti.",
        "",
        "## Fasi",
        "",
    ]

    for phase in data.get("phases", []):
        lines.append(f"### {phase['id']} – {phase['name']}")
        for task in phase.get("tasks", []):
            lines.append(f"- {task['id']} {task['title']} — `{task['status']}`")
        lines.append("")

    TASKS_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Generato: {TASKS_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
