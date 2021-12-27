#!/usr/bin/env bash

set -e

VERSION=$(python3 -c 'import hypy_utils; print(hypy_utils.__version__)')
echo "$VERSION"

rm dist/*

# Build
python3 setup.py sdist bdist_wheel

# Check
python3 -m twine check dist/*

# Upload
python3 -m twine upload dist/*
