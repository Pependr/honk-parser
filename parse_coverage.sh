#/bin/bash
pytest -q --cov --cov-report json
honk parse -p coverage.json -t $1 -d ${2:-"/"} json | uv run -m json.tool | less
unlink coverage.json