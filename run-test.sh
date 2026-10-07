#!/bin/bash
set -e

# Run this script to execute all automated tests
source venv/bin/activate
pytest -v
