#!/bin/bash

# Run unit tests with coverage reporting
python -m pytest tests/unit -v --cov=src --cov-report=term --cov-report=html:coverage_report
