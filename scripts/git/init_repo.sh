
#!/usr/bin/env bash
set -euo pipefail

DEFAULT_BRANCH=${1:-main}
REMOTE_URL=${2:-}

git init
git checkout -b "$DEFAULT_BRANCH"
git add -A
git commit -m "chore(init): NexusNet v0.5.1a initial import"

if [ -n "$REMOTE_URL" ]; then
  git remote add origin "$REMOTE_URL"
  git push -u origin "$DEFAULT_BRANCH"
fi

echo "Repo initialized on branch: $DEFAULT_BRANCH"
[ -n "$REMOTE_URL" ] && echo "Remote set to: $REMOTE_URL"
