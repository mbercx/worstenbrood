"""ABINIT-side conversion constants.

ABINIT uses atomic units (Hartree, Bohr) internally. The values below convert
to the documented user-facing units (eV, Å, eV/Å, GPa).

Values match `qe_tools._constants.DEFAULT` so that mixed-code workflows agree
to round-off.
"""

from types import SimpleNamespace

__all__ = ("DEFAULT",)

DEFAULT = SimpleNamespace(
    bohr_to_ang=0.52917720859,
    ang_to_m=1.0e-10,
    ry_to_ev=13.6056917253,
    ha_si=4.3597447222071e-18,  # J
    bohr_si=0.529177210903e-10,  # m
)

DEFAULT.hartree_to_ev = DEFAULT.ry_to_ev * 2.0
DEFAULT.au_gpa = DEFAULT.ha_si / (DEFAULT.bohr_si**3.0) / 1.0e9
