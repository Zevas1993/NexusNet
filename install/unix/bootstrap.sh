
#!/usr/bin/env bash
set -e
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
[ -f requirements.txt ] && pip install -r requirements.txt
echo "Done."
