import pytest

from greeter.cli import main


def test_default_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert capsys.readouterr().out == "Hello, world!\n"


def test_named_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--name", "Ada"]) == 0
    assert capsys.readouterr().out == "Hello, Ada!\n"
