"""Tests for `AbinitAboParser`."""

from worstenbrood.outputs.parsers.abinit_abo import AbinitAboParser


def test_parse_basic(files_path, robust_data_regression_check):
    """Snapshot the full parsed dict for the basic `.abo` fixture."""
    parsed = AbinitAboParser.parse_from_file(
        files_path / "abinit" / "basic" / "run.abo"
    )
    robust_data_regression_check(parsed)
