"""Integration tests for the AbinitOutput class."""

import pytest

from worstenbrood import CONSTANTS
from worstenbrood.outputs import AbinitOutput


def test_from_dir_basic(files_path):
    """`AbinitOutput.from_dir` parses the basic fixture."""
    out = AbinitOutput.from_dir(files_path / "abinit" / "basic")

    assert out.outputs.completed is True
    assert out.outputs.code_version == "10.4.0"
    assert out.outputs.n_scf_steps == 8
    assert out.outputs.total_energy == pytest.approx(
        -7.83412345678900 * CONSTANTS.hartree_to_ev
    )


def test_completed_default_when_stdout_missing(tmp_path):
    """Without an `.abo` file, `completed` falls back to `False`."""
    out = AbinitOutput.from_dir(tmp_path)

    assert out.outputs.completed is False
