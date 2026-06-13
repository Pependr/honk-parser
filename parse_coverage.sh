#/bin/bash
pytest -q --cov --cov-report json
honk parse -p coverage.json -t $1 -d ${2:-"/"} json  | honk parse -m json group | honk parse -m json map-map --header "file name" >> missinglines.md
unlink coverage.json