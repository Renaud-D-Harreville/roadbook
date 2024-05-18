#! /bin/sh

# Start by giving execution rights to that file with :
# chmod +x setup.sh


# This script will create a python3.11 virtual environment,
# then update it and finally install the project in dev mode (-e and [dev] arguments)

rm -rf .venv
python3.12 -m venv .venv --prompt roadbook
. .venv/bin/activate
pip install -U pip setuptools
pip install -e .[dev]
