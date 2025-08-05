#!/bin/bash
set -euo pipefail

# Run flake8 with bugbear and bandit plugins
if command -v flake8 >/dev/null 2>&1; then
  echo "Running flake8..."
  flake8 .
else
  echo "flake8 not installed"
fi

# Run bandit
if command -v bandit >/dev/null 2>&1; then
  echo "Running bandit..."
  bandit -r .
else
  echo "bandit not installed"
fi

# Run pylint
if command -v pylint >/dev/null 2>&1; then
  echo "Running pylint..."
  pylint app zona tests
else
  echo "pylint not installed"
fi

# Check Python dependencies for known vulnerabilities
if command -v pip-audit >/dev/null 2>&1; then
  echo "Running pip-audit..."
  pip-audit
else
  echo "pip-audit not installed"
fi

if command -v safety >/dev/null 2>&1; then
  echo "Running safety..."
  safety check
else
  echo "safety not installed"
fi
