#!/usr/bin/env bash
# Render build step. Runs with the persistent disk READ-ONLY, so:
#   - NO `migrate` here (it has nowhere to write). It runs at start: `bootstrap_site`.
#   - Only things that write inside the repo checkout belong here.
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
