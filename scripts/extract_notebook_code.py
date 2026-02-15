from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
OUT = ROOT / "src" / "notebook_exports"
OUT.mkdir(parents=True, exist_ok=True)

for nb_path in NOTEBOOKS.glob("*.ipynb"):
    data = json.loads(nb_path.read_text(encoding="utf-8"))
    lines = [
        '"""Arquivo extraído automaticamente do notebook para rastreabilidade.\n',
        "NÃO editável manualmente sem sincronização com o notebook de origem.\n",
        '"""\n\n',
    ]
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        if src.lstrip().startswith("!") or "MEU_TOKEN" in src or "gurobipy" in src:
            continue
        lines.append("\n# %%\n")
        lines.append(src)
        if not src.endswith("\n"):
            lines.append("\n")

    out_path = OUT / f"{nb_path.stem}.py"
    out_path.write_text("".join(lines), encoding="utf-8")
    print(f"Gerado: {out_path.relative_to(ROOT)}")
