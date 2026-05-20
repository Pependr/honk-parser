#!/bin/bash

uv init $1
git init

uv venv
source .venv/bin/activate

uv python install $2

uv add ruff pytest pytest-cov pytest-mock --dev
uv sync --dev

unlink init.sh
