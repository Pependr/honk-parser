import pytest as pt
import pytest_mock as pm

import json
import pathlib

from mdparser import parse_utils as pu


@pt.fixture
def mock_path(mocker: pm.MockerFixture) -> pm.MockType:
	return mocker.create_autospec(pathlib.Path, spec_set=True, instance=True)


def test_parse_file_json(mock_path: pm.MockType) -> None:
	mock_path.as_posix.return_value = "mock.json"
	mock_path.read_text.return_value = json.dumps(
		{"bruh": 69, "dude": 6.7, "man": None}
	)

	assert pu.parse_file(mock_path) == {"bruh": 69, "dude": 6.7, "man": None}
	mock_path.as_posix.assert_called_once()
	mock_path.read_text.assert_called_once()


def test_parse_file_toml(mock_path: pm.MockType) -> None:
	mock_path.as_posix.return_value = "mock.toml"
	mock_path.read_text.return_value = (
		"""bruh = 69\ndude = 6.7\nman = 'shit'\n"""
	)

	assert pu.parse_file(mock_path) == {"bruh": 69, "dude": 6.7, "man": "shit"}
	mock_path.as_posix.assert_called_once()
	mock_path.read_text.assert_called_once()


def test_parse_file_unsupported(mock_path: pm.MockType) -> None:
	mock_path.as_posix.return_value = "file.mock"

	with pt.raises(pu.UnsupportedExtension):
		pu.parse_file(mock_path)

	mock_path.as_posix.assert_called_once()


def test_split_obj_path() -> None:
	assert pu.split_obj_path(".") == []
	assert pu.split_obj_path("path/to/obj") == ["path", "to", "obj"]
	assert pu.split_obj_path("my.delim.path", ".") == ["my", "delim", "path"]


def test_deep_get() -> None:
	assert pu.deep_get({"key": 0}, ["key"]) == 0
	assert pu.deep_get({"key1": {"key2": 0}}, ["key1", "key2"]) == 0
	assert pu.deep_get({"key1": {"key2": 0, "key3": 1}}, ["key1", "key2"]) == 0
