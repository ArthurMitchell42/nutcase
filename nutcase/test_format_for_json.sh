#!/usr/bin/bash
cd app
# python -m unittest discover -v -s app/tests/unit -t ./app
coverage run -m unittest -v  ./tests/unit/test_format_for_json.py
coverage report -m | tee coverage.txt
coverage html

