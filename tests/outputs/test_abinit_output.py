"""Integration tests for the AbinitOutput class."""

from pathlib import Path

import pytest

from worstenbrood.outputs import AbinitOutput

FIXTURES = Path(__file__).parent / "fixtures" / "abinit"


@pytest.mark.parametrize("fixture", ["basic", "magnetic"])
def test_from_dir(robust_data_regression_check, fixture):
    """End-to-end: ``AbinitOutput.from_dir`` parses each fixture into the expected outputs."""
    abinit_out = AbinitOutput.from_dir(FIXTURES / fixture)

    robust_data_regression_check({"base_outputs": abinit_out.get_output_dict()})


def test_basic_skips_magnetization():
    """The basic fixture has no spin density; magnetization outputs are unavailable."""
    abinit_out = AbinitOutput.from_dir(FIXTURES / "basic")

    available = abinit_out.list_outputs()
    assert "total_magnetization" not in available
    assert "magnetization_per_site" not in available


def test_magnetic_outputs():
    """The magnetic fixture surfaces total + per-site magnetization."""
    abinit_out = AbinitOutput.from_dir(FIXTURES / "magnetic")

    available = abinit_out.list_outputs()
    assert "total_magnetization" in available
    assert "magnetization_per_site" in available

    assert abinit_out.outputs.total_magnetization == pytest.approx(2.22)
    assert abinit_out.outputs.magnetization_per_site == pytest.approx([2.22])


def test_job_done_default_when_stdout_missing(tmp_path):
    """Without an ``.abo`` file, ``job_done`` falls back to ``False`` instead of raising."""
    # Copy only the GSR.nc into a fresh dir.
    src = FIXTURES / "basic" / "run.abo_GSR.nc"
    (tmp_path / "run.abo_GSR.nc").write_bytes(src.read_bytes())

    abinit_out = AbinitOutput.from_dir(tmp_path)

    assert abinit_out.outputs.job_done is False
