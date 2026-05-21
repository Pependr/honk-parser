import pathlib
import argparse

from mdparser import parse_utils as pu


# TEMPLATES: dict[tuple[str, ...], dict[str, Any]] = {}


def make_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="mdparser",
		description="A tool that parses your data to beautiful markdowns",
	)

	parser.add_argument(
		"path",
		help="Path to the source file.",
		type=pathlib.Path,
		nargs="?",
	)

	parser.add_argument(
		"target",
		help="The target object in the source file. Defaults to the root object.",
		nargs="?",
		default=".",
	)

	parser.add_argument(
		*["-d", "--delim"],
		help="The delimiter symbol in the target path.",
		nargs="?",
		default="/",
		metavar="char",
	)

	# template_group = parser.add_argument_group(
	# 	"template", description="The desired template of output markdown"
	# ).add_mutually_exclusive_group(required=True)

	# for tmpt, opts in TEMPLATES.items():
	# 	template_group.add_argument(*tmpt, **opts)

	return parser


def main() -> None:
	parser = make_parser()

	args = parser.parse_args()

	data = pu.deep_get(
		pu.parse_file(args.path), pu.split_obj_path(args.target, args.delim)
	)


if __name__ == "__main__":
	main()
