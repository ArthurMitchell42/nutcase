#!/usr/bin/bash

cd app
# python -m unittest discover -v -s app/tests/unit -t ./app
coverage run -m unittest discover -v -s tests/unit -t .
coverage report -m | tee coverage.txt
coverage html

