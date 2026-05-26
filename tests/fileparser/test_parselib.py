import pytest as pt
import pytest_mock as pm

import json
import pathlib
import tomllib

from fileparser import parselib as pl


@pt.fixture
def mock_path(mocker: pm.MockerFixture) -> pm.MockType:
	return mocker.create_autospec(pathlib.Path, spec_set=True, instance=True)


def test_parse_file_json(mock_path: pm.MockType) -> None:
	pl.parser("json")(json.loads)

	mock_path.as_posix.return_value = "mock.json"
	mock_path.read_text.return_value = json.dumps(
		{"bruh": 69, "dude": 6.7, "man": None}
	)

	assert pl.parse_file(mock_path) == {"bruh": 69, "dude": 6.7, "man": None}
	mock_path.as_posix.assert_called_once()
	mock_path.read_text.assert_called_once()


def test_parse_file_toml(mock_path: pm.MockType) -> None:
	pl.parser("toml")(tomllib.loads)

	mock_path.as_posix.return_value = "mock.toml"
	mock_path.read_text.return_value = "bruh = 69\ndude = 6.7\nman = 'shit'\n"

	assert pl.parse_file(mock_path) == {"bruh": 69, "dude": 6.7, "man": "shit"}
	mock_path.as_posix.assert_called_once()
	mock_path.read_text.assert_called_once()


def test_parse_file_unsupported(mock_path: pm.MockType) -> None:
	mock_path.as_posix.return_value = "file.mock"

	with pt.raises(pl.UnsupportedExtension):
		pl.parse_file(mock_path)

	mock_path.as_posix.assert_called_once()


def test_split_obj_path() -> None:
	assert pl.split_obj_path(".") == []
	assert pl.split_obj_path("path/to/obj") == ["path", "to", "obj"]
	assert pl.split_obj_path("my.delim.path", ".") == ["my", "delim", "path"]


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
