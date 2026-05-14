"""ABINIT-side conversion constants.

ABINIT uses atomic units (Hartree, Bohr) internally. The values below convert
to the documented user-facing units (eV, Å).
"""

from types import SimpleNamespace

__all__ = ("DEFAULT",)

DEFAULT = SimpleNamespace(
    hartree_to_ev=27.2113834506,
)
