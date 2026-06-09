import pytest as pt

import json
import pathlib
import tomllib

from honk import parselib as pl


def test_parse(subtests: pt.Subtests) -> None:
    with subtests.test("Error during parsing json"):
        pl.parser("json")(json.loads)

        data = json.dumps({"name": "Alice", "age": 18})

        assert pl.parse(data, "json") == {"name": "Alice", "age": 18}

    with subtests.test("Error during parsing toml"):
        pl.parser("toml")(tomllib.loads)

        data = "name = 'Alice'\nage = 18"

        assert pl.parse(data, "toml") == {"name": "Alice", "age": 18}

    with subtests.test("Error during testing exception"):
        with pt.raises(ValueError, match="No such parsing method: bruh"):
            pl.parse("data", "bruh")


def test_split_obj_path() -> None:
    assert pl.split_obj_path(".") == ()
    assert pl.split_obj_path("path/to/obj") == ("path", "to", "obj")
    assert pl.split_obj_path("my.delim.path", ".") == ("my", "delim", "path")
    assert pl.split_obj_path("key/4/item") == ("key", 4, "item")


def test_deep_get() -> None:
    assert pl.deep_get({"key": 0}, ["key"]) == 0
    assert pl.deep_get({"key1": {"key2": 0}}, ["key1", "key2"]) == 0
    assert pl.deep_get({"key1": {"key2": 0, "key3": 1}}, ["key1", "key2"]) == 0
    assert pl.deep_get({"key1": 0}, []) == {"key1": 0}
    assert pl.deep_get(0, []) == 0  # type: ignore


def test_resolve_path() -> None:
    assert pl.resolve_path(
        {
            "files": {
                "test_bruh.py": {
                    "functions": "bruh_functions",
                    "classes": "bruh_classes",
                    "summary": "bruh_summary",
                },
                "test_dude.py": {
                    "functions": "dude_functions",
                    "classes": "dude_classes",
                    "summary": "dude_summary",
                },
            }
        },
        ["files", "*", "summary"],
    ) == {
        "test_bruh.py": {"summary": "bruh_summary"},
        "test_dude.py": {"summary": "dude_summary"},
    }

    assert pl.resolve_path(
        {"files": {"test_bruh.py": {"summary": "bruh_summary"}}},
        ["files", "test_bruh.py", "summary"],
    ) == pl.deep_get(
        {"files": {"test_bruh.py": {"summary": "bruh_summary"}}},
        ["files", "test_bruh.py", "summary"],
    )

    assert pl.resolve_path(
        {
            "files": {
                "test_bruh.py": {
                    "functions": {"missed": 10},
                    "classes": {"missed": 16},
                    "summary": {"missed": 26},
                },
                "test_dude.py": {
                    "functions": {"missed": 69},
                    "classes": {"missed": 0},
                    "summary": {"missed": 69},
                },
            }
        },
        ["files", "*", "*", "missed"],
    ) == {
        "test_bruh.py": {
            "functions": {"missed": 10},
            "classes": {"missed": 16},
            "summary": {"missed": 26},
        },
        "test_dude.py": {
            "functions": {"missed": 69},
            "classes": {"missed": 0},
            "summary": {"missed": 69},
        },
    }

    assert pl.resolve_path(
        {
            "files": {
                "test_bruh.py": {
                    "functions": "bruh_functions",
                    "classes": "bruh_classes",
                    "summary": "bruh_summary",
                },
                "test_dude.py": {
                    "functions": "dude_functions",
                    "classes": "dude_classes",
                    "summary": "dude_summary",
                },
            }
        },
        ["files", "*"],
    ) == {
        "test_bruh.py": {
            "functions": "bruh_functions",
            "classes": "bruh_classes",
            "summary": "bruh_summary",
        },
        "test_dude.py": {
            "functions": "dude_functions",
            "classes": "dude_classes",
            "summary": "dude_summary",
        },
    }


def test_match_wildcard() -> None:
    assert pl.match_wildcard("bruh", "bruh")
    assert not pl.match_wildcard("bruh", "dude")
    assert pl.match_wildcard("*_display", "percent_display")
    assert not pl.match_wildcard("*_display", "_display_stuff")
    assert pl.match_wildcard("covered_*", "covered_lines")
    assert not pl.match_wildcard("covered_*", "got_you_covered_")
    assert pl.match_wildcard("*exclude*", "that_exclude_thing")
    assert pl.match_wildcard("that*exclude*", "that_exclude_thing")
    assert pl.match_wildcard("*exclude*thing", "that_exclude_thing")
    assert pl.match_wildcard("that*thing", "that_exclude_thing")
    assert pl.match_wildcard("*", "bruh") and pl.match_wildcard("*", "dude")


def test_get_extension() -> None:
    assert pl.get_extension(pathlib.Path("coverage.json")) == "json"


def test_split_sequence() -> None:
    assert pl.split_sequence(["bruh", "*", "dude", "*", "man"], "*") == (
        ["bruh"],
        ["dude"],
        ["man"],
    )
    assert pl.split_sequence(["bruh", "*", "dude", "man"], "*") == (
        ["bruh"],
        ["dude", "man"],
    )
    assert pl.split_sequence(
        ["bruh", "*", "dude", "*", "man"], "*", maxsplit=1
    ) == (
        ["bruh"],
        ["dude", "*", "man"],
    )
