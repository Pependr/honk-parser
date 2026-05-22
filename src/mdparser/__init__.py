import json
import tomllib
import argparse

from enum import StrEnum, auto

from typing import Any

from mdparser import buildlib, parselib, templatelib


parselib.parser("json")(json.loads)
parselib.parser("toml")(tomllib.loads)


class Align(StrEnum):
	RIGHT = auto()
	CENTER = auto()
	LEFT = auto()


@buildlib.entry
def table(subparsers: buildlib.Subparsers) -> None:
	parser = subparsers.add_parser("table", help="--exclude --align")

	parser.add_argument(
		*["-e", "--exclude"],
		nargs="*",
		default=(),
		help="Excluded keys from the object",
		metavar="strings",
	)

	parser.add_argument(
		*["-a", "--align"],
		nargs="?",
		default=Align.RIGHT,
		type=Align,
		choices=Align,
		help="The aligning of the table",
		metavar="right|center|left",
	)


def table_headers(
	namespace: argparse.Namespace, data: dict[str, Any]
) -> list[str]:
	return [f"|{"|".join(k for k in data if k not in namespace.exclude)}|"]


table_pipe = templatelib.compose(table_headers)

templatelib.template("table")(table_pipe)


def main() -> None:
	parser = buildlib.make_parser()

	args = parser.parse_args()

	if args.command == "parse":
		data = parselib.deep_get(
			parselib.parse_file(args.path),
			parselib.split_obj_path(args.target, args.delim),
		)

		pipe = templatelib.resolve(args.template)

		print(templatelib.merge(pipe(args, data)))


if __name__ == "__main__":
	main()
