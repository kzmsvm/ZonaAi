#!/usr/bin/env bash
# Run static code analysis and dependency security scans

set -euo pipefail

# Static analysis tools
if command -v flake8 >/dev/null 2>&1; then
  echo "Running flake8..."
  flake8 app zona tests
else
  echo "flake8 not installed" >&2
fi

if command -v bandit >/dev/null 2>&1; then
  echo "Running bandit..."
  bandit -r app zona tests
else
  echo "bandit not installed" >&2
fi

if command -v pylint >/dev/null 2>&1; then
  echo "Running pylint..."
  pylint app zona tests
else
  echo "pylint not installed" >&2
fi

# Dependency scanning tools
if command -v pip-audit >/dev/null 2>&1; then
  echo "Running pip-audit..."
  pip-audit
else
  echo "pip-audit not installed" >&2
fi

if command -v safety >/dev/null 2>&1; then
  echo "Running safety..."
  safety check || true
else
  echo "safety not installed" >&2
fi

