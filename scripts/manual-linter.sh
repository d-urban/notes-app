#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

PASS=0
FAIL=0

run_check() {
    local name="$1"
    shift
    echo "--- $name ---"
    if "$@"; then
        echo "[PASS] $name"
    else
        echo "[FAIL] $name"
        FAIL=$((FAIL + 1))
        return 0
    fi
    PASS=$((PASS + 1))
    echo ""
}

cd "$ROOT_DIR"

run_check "flake8 (Python)" \
    flake8 main.py database.py scripts/migrate_from_long_short_to_one_type.py

run_check "shellcheck (Shell)" \
    shellcheck scripts/create_systemd_service.sh

run_check "eslint (JavaScript in HTML)" \
    npx --no-install eslint index.html

run_check "markdownlint (Markdown)" \
    npx --no-install markdownlint README.md

run_check "htmlhint (HTML)" \
    npx --no-install htmlhint index.html

echo "==============================="
echo "Results: $PASS passed, $FAIL failed"
echo "==============================="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
