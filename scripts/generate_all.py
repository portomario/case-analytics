# -*- coding: utf-8 -*-
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "turnover_monthly.csv"
OUT = BASE / "output"

def run(cmd):
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)

if __name__ == "__main__":
    run([sys.executable, str(BASE / "scripts" / "analyze.py"), "--input", str(DATA), "--outdir", str(OUT)])
    try:
        run([sys.executable, str(BASE / "scripts" / "create_ppt.py")])
    except Exception as e:
        print("Aviso: falha ao gerar PPT (dependência python-pptx pode estar ausente).", e)
