import pathlib
import argparse

from typing import Callable, Protocol


class Subparsers(Protocol):
	def add_parser(
		self,
		name: str,
		*,
		description: str | None = ...,
		help: str | None = ...,
	) -> argparse.ArgumentParser: ...


type EntryFn = Callable[[Subparsers], None]


ENTRIES: list[EntryFn] = []


def entry(fn: EntryFn) -> EntryFn:
	ENTRIES.append(fn)
	return fn


def add_parse(commands: Subparsers) -> argparse.ArgumentParser:
	parse = commands.add_parser(
		"parse",
		description="Parse data from a file into a markdown",
		help="Parse data from a file into a markdown",
	)

	parse.add_argument(
		*["-p", "--path"],
		help="Path to the source file",
		type=pathlib.Path,
		nargs="?",
	)

	parse.add_argument(
		*["-f", "--from"],
		help="The target object in the source file. Defaults to the root object",
		nargs="?",
		default=".",
		metavar="string",
		dest="target",
	)

	parse.add_argument(
		*["-d", "--delim"],
		help="The delimiter symbol in the target path",
		nargs="?",
		default="/",
		metavar="char",
	)

	return parse


def make_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="mdparser",
		description="A tool that parses your data to beautiful markdowns",
	)

	commands = parser.add_subparsers(
		title="commands",
		description="Available commands:",
		dest="command",
		required=True,
	)

	parse = add_parse(commands)

	templates = parse.add_subparsers(
		title="templates",
		description="Available templates:",
		dest="template",
		required=True,
	)

	for register in ENTRIES:
		register(templates)

	return parser
