"""Parse ABINIT `GSR.nc` (NetCDF ground-state results)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dough.outputs.parsers.base import BaseBinaryFileParser

# Variables read from GSR.nc. Names follow the ETSF-IO conventions used by
# ABINIT and abipy. Units are ABINIT-native (Hartree, Bohr, Ha/Bohr,
# Ha/Bohr³); Specs convert to eV/Å/GPa.
_SCALAR_VARS = ("etotal", "e_fermie")
_ARRAY_VARS = (
    "primitive_vectors",
    "reduced_atom_positions",
    "atom_species",
    "atomic_numbers",
    "cartesian_forces",
    "cartesian_stress_tensor",
    "intgden",
)


class GsrParser(BaseBinaryFileParser):
    """Parse ABINIT `GSR.nc`."""

    @staticmethod
    def parse(path: Path) -> dict[str, Any]:
        from netCDF4 import Dataset  # lazy: keep import-time cost off text-only paths

        result: dict[str, Any] = {}
        with Dataset(path, "r") as ds:
            for name in _SCALAR_VARS:
                if name in ds.variables:
                    result[name] = float(ds.variables[name][...])
            for name in _ARRAY_VARS:
                if name in ds.variables:
                    result[name] = ds.variables[name][...].tolist()
        return result
