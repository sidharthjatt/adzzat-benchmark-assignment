#!/usr/bin/env bash
# Run the full test suite and write a JUnit report to reports/junit.xml.
cd "$(dirname "$0")/.."
python -m pytest -q --junitxml=reports/junit.xml "$@" | tail -n 15
