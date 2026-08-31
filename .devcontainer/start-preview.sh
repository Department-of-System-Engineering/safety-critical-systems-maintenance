#!/usr/bin/env bash
set -e

# Avoid starting duplicate preview processes when Codespaces resumes.
if pgrep -f "quarto preview.*--port 4200" >/dev/null 2>&1; then
  exit 0
fi

nohup quarto preview --host 0.0.0.0 --port 4200 > /tmp/quarto-preview.log 2>&1 &
