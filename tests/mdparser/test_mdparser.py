import subprocess as sp


def test_mdparser() -> None:
	assert sp.check_output(["mdparser", "report.json"]) == b"report.json\n"
