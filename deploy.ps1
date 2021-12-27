$ErrorActionPreference = "Stop"

$VERSION = $(python -c 'import hypy_utils; print(hypy_utils.__version__)')
Write-Output "$VERSION"

Remove-Item dist/*

# Build
python setup.py sdist bdist_wheel

# Check
python -m twine check dist/*

# Upload
python -m twine upload dist/*
