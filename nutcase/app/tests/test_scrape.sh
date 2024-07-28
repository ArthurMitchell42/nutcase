#!/usr/bin/bash
cd app
coverage run -m unittest -v  ./tests/unit/test_scrape.py
# coverage report -m | tee coverage.txt
coverage html

