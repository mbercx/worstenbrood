"""Generate synthetic ABINIT GSR.nc + .abo fixtures.

These are NOT real ABINIT outputs. Numbers are physics-plausible but fudged
(see CLAUDE.md fixture trim policy). The goal is to exercise the parser, not
to produce reproducible DFT.

Variable names follow the ETSF-IO conventions used by abipy / ABINIT:
- `primitive_vectors`   — real-space cell vectors (Bohr), shape (3, 3)
- `reduced_atom_positions` — fractional positions, shape (n_atoms, 3)
- `atom_species`        — per-atom species index (1-based), shape (n_atoms,)
- `atomic_numbers`      — species → Z mapping, shape (n_species,)
- `etotal`              — total energy in Hartree
- `e_fermie`            — Fermi energy in Hartree
- `cartesian_forces`    — forces in Ha/Bohr, shape (n_atoms, 3)
- `cartesian_stress_tensor` — symmetric 3×3 in Ha/Bohr³, shape (3, 3)
- `intgden`             — integrated spin density (atom-resolved spin moments
                          for collinear runs, shape (n_spden, n_atoms))

Run with: python tests/outputs/fixtures/abinit/_make_fixtures.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from netCDF4 import Dataset

HERE = Path(__file__).resolve().parent


def write_gsr(
    path: Path,
    *,
    cell_bohr: np.ndarray,
    positions_frac: np.ndarray,
    atom_species: np.ndarray,
    atomic_numbers: np.ndarray,
    etotal_ha: float,
    e_fermie_ha: float,
    forces_ha_per_bohr: np.ndarray,
    stress_ha_per_bohr3: np.ndarray,
    intgden: np.ndarray | None = None,
) -> None:
    """Write a minimal GSR.nc with the variables `worstenbrood` reads."""
    n_atoms = positions_frac.shape[0]
    n_species = atomic_numbers.shape[0]

    with Dataset(path, "w", format="NETCDF4") as ds:
        ds.createDimension("number_of_atoms", n_atoms)
        ds.createDimension("number_of_atom_species", n_species)
        ds.createDimension("number_of_cartesian_directions", 3)
        ds.createDimension("number_of_reduced_dimensions", 3)
        ds.createDimension("number_of_vectors", 3)

        v = ds.createVariable(
            "primitive_vectors",
            "f8",
            ("number_of_vectors", "number_of_cartesian_directions"),
        )
        v[:] = cell_bohr

        v = ds.createVariable(
            "reduced_atom_positions",
            "f8",
            ("number_of_atoms", "number_of_reduced_dimensions"),
        )
        v[:] = positions_frac

        v = ds.createVariable("atom_species", "i4", ("number_of_atoms",))
        v[:] = atom_species

        v = ds.createVariable("atomic_numbers", "f8", ("number_of_atom_species",))
        v[:] = atomic_numbers

        v = ds.createVariable("etotal", "f8")
        v[...] = etotal_ha

        v = ds.createVariable("e_fermie", "f8")
        v[...] = e_fermie_ha

        v = ds.createVariable(
            "cartesian_forces",
            "f8",
            ("number_of_atoms", "number_of_cartesian_directions"),
        )
        v[:] = forces_ha_per_bohr

        v = ds.createVariable(
            "cartesian_stress_tensor",
            "f8",
            ("number_of_cartesian_directions", "number_of_cartesian_directions"),
        )
        v[:] = stress_ha_per_bohr3

        if intgden is not None:
            ds.createDimension("number_of_components", intgden.shape[0])
            v = ds.createVariable(
                "intgden", "f8", ("number_of_components", "number_of_atoms")
            )
            v[:] = intgden


ABO_BASIC = """\
.Version 10.4.0 of ABINIT
.(MPI version, prepared for a x86_64_darwin_gnu13.2 computer)

.Copyright (C) 1998-2024 ABINIT group .

------------- Echo of variables that govern the present computation ------------

 outvars: echo of selected default values
-   iomode0 =  0 , fftalg0 =312 , wfoptalg0 =  0

================================================================================
== DATASET  1 ==================================================================

 ITER STEP NUMBER     1
 ETOT  1  -7.8123456789012E+00 -7.812E+00  4.5E-04  3.2E-03

--- Removed: 6 SCF iterations ---

 ITER STEP NUMBER     8
 ETOT  8  -7.8341234567890E+00 -1.234E-08  2.1E-11  4.5E-09

 At SCF step    8       vres2   =  4.45E-09 < tolvrs=  1.00E-08 =>converged.

================================================================================

 Calculation completed.
.Delivered    0 WARNINGs and   0 COMMENTs to log file.
+Overall time at end (sec) :     cpu=          1.2  wall=          1.3
"""


ABO_MAGNETIC = """\
.Version 10.4.0 of ABINIT
.(MPI version, prepared for a x86_64_darwin_gnu13.2 computer)

.Copyright (C) 1998-2024 ABINIT group .

------------- Echo of variables that govern the present computation ------------

 outvars: echo of selected default values
-   iomode0 =  0 , fftalg0 =312 , wfoptalg0 =  0
            nsppol           2
            nspden           2

================================================================================
== DATASET  1 ==================================================================

 ITER STEP NUMBER     1
 ETOT  1  -2.5012345678901E+01 -2.501E+01  3.2E-03  1.8E-02

--- Removed: 10 SCF iterations ---

 ITER STEP NUMBER    12
 ETOT 12  -2.5345678901234E+01 -7.890E-09  1.5E-11  3.2E-09

 At SCF step   12       vres2   =  3.21E-09 < tolvrs=  1.00E-08 =>converged.

================================================================================

 Calculation completed.
.Delivered    0 WARNINGs and   0 COMMENTs to log file.
+Overall time at end (sec) :     cpu=          5.4  wall=          5.6
"""


def make_basic() -> None:
    """Bulk Si, primitive 2-atom cell, non-magnetic."""
    out = HERE / "basic"
    out.mkdir(exist_ok=True)

    a = 10.262  # Bohr (~5.43 Å)
    cell = np.array([[0.0, a / 2, a / 2], [a / 2, 0.0, a / 2], [a / 2, a / 2, 0.0]])
    positions = np.array([[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]])
    atom_species = np.array([1, 1], dtype="i4")
    atomic_numbers = np.array([14.0])

    forces = np.zeros((2, 3))  # equilibrium
    stress = np.diag([-1.2e-5, -1.2e-5, -1.2e-5])  # near-zero diagonal

    write_gsr(
        out / "run.abo_GSR.nc",
        cell_bohr=cell,
        positions_frac=positions,
        atom_species=atom_species,
        atomic_numbers=atomic_numbers,
        etotal_ha=-7.8341234567890,
        e_fermie_ha=0.20123456789,
        forces_ha_per_bohr=forces,
        stress_ha_per_bohr3=stress,
    )

    (out / "run.abo").write_text(ABO_BASIC)


def make_magnetic() -> None:
    """bcc Fe primitive cell, ferromagnetic (collinear)."""
    out = HERE / "magnetic"
    out.mkdir(exist_ok=True)

    a = 5.42  # Bohr (~2.87 Å)
    cell = np.array(
        [[-a / 2, a / 2, a / 2], [a / 2, -a / 2, a / 2], [a / 2, a / 2, -a / 2]]
    )
    positions = np.array([[0.0, 0.0, 0.0]])
    atom_species = np.array([1], dtype="i4")
    atomic_numbers = np.array([26.0])

    forces = np.zeros((1, 3))
    stress = np.diag([-3.5e-5, -3.5e-5, -3.5e-5])

    # intgden shape: (n_spden, n_atoms). For nspden=2 collinear:
    # row 0 = up density, row 1 = down density (per atom, integrated).
    # spin moment per atom = up - down.
    intgden = np.array([[5.16], [2.94]])  # Fe ~2.22 μ_B per atom

    write_gsr(
        out / "run.abo_GSR.nc",
        cell_bohr=cell,
        positions_frac=positions,
        atom_species=atom_species,
        atomic_numbers=atomic_numbers,
        etotal_ha=-2.5345678901234e1,
        e_fermie_ha=0.456789,
        forces_ha_per_bohr=forces,
        stress_ha_per_bohr3=stress,
        intgden=intgden,
    )

    (out / "run.abo").write_text(ABO_MAGNETIC)


if __name__ == "__main__":
    make_basic()
    make_magnetic()
    print("Wrote basic and magnetic fixtures to", HERE)
