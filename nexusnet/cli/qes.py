
from __future__ import annotations
import sys, subprocess
def main():
    args = sys.argv[1:] or []
    subprocess.call([sys.executable, "scripts/qes/run_evolution.py", *args])
