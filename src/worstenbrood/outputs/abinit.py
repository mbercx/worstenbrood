"""ABINIT output class and output mapping."""

from pathlib import Path
from typing import Annotated, Any, Optional, Union

from dough import Unit
from dough.outputs.base import BaseOutput, output_mapping
from glom import Spec

from worstenbrood import CONSTANTS
from worstenbrood.outputs.parsers.abinit_stdout import AbinitStdoutParser
from worstenbrood.outputs.parsers.gsr import GsrParser

# Element symbols indexed by atomic number; index 0 is a placeholder so that
# `_SYMBOLS[Z]` works directly. Covers Z = 1..118.
_SYMBOLS = (
    "X",  # placeholder for Z=0
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",
    "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds",
    "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
)  # fmt: skip


def _build_structure(gsr: dict[str, Any]) -> dict[str, Any]:
    """Assemble a code-native structure dict from raw GSR variables.

    Keys:
        symbols (list[str]): chemical symbol per atom.
        cell (list[list[float]]): real-space lattice vectors in Å, shape (3, 3).
        positions (list[list[float]]): fractional positions, shape (n_atoms, 3).
    """
    species = gsr["atom_species"]  # 1-based per-atom index
    z_per_species = gsr["atomic_numbers"]  # one Z per species
    symbols = [_SYMBOLS[int(z_per_species[s - 1])] for s in species]

    cell = [
        [v * CONSTANTS.bohr_to_ang for v in row] for row in gsr["primitive_vectors"]
    ]
    positions = [list(row) for row in gsr["reduced_atom_positions"]]

    return {"symbols": symbols, "cell": cell, "positions": positions}


def _collinear_total_magnetization(intgden: list[list[float]]) -> float:
    """Total cell magnetization (μ_B) from `intgden` for collinear runs.

    `intgden` shape is (n_spden, n_atoms). For nspden=2, row 0 is the
    spin-up density and row 1 is the spin-down density. The cell moment is
    the sum over atoms of (up - down).
    """
    up, down = intgden[0], intgden[1]
    return sum(u - d for u, d in zip(up, down))


def _collinear_magnetization_per_site(intgden: list[list[float]]) -> list[float]:
    """Per-atom magnetic moment (μ_B) from `intgden` for collinear runs."""
    up, down = intgden[0], intgden[1]
    return [u - d for u, d in zip(up, down)]


@output_mapping
class _AbinitMapping:
    """Typed outputs of an ABINIT ground-state calculation."""

    total_energy: Annotated[
        float,
        Spec(("gsr.etotal", lambda e: e * CONSTANTS.hartree_to_ev)),
        Unit("eV"),
    ]
    """Total energy in eV."""

    fermi_energy: Annotated[
        float,
        Spec(("gsr.e_fermie", lambda e: e * CONSTANTS.hartree_to_ev)),
        Unit("eV"),
    ]
    """Fermi energy in eV."""

    structure: Annotated[
        dict[str, Any],
        Spec(("gsr", _build_structure)),
    ]
    """Final structure with keys ``"symbols"`` (list[str]), ``"cell"`` (list[list[float]], Å), ``"positions"`` (list[list[float]], fractional)."""

    forces: Annotated[
        list[list[float]],
        Spec(
            (
                "gsr.cartesian_forces",
                lambda f: [
                    [c * CONSTANTS.hartree_to_ev / CONSTANTS.bohr_to_ang for c in row]
                    for row in f
                ],
            )
        ),
        Unit("eV/angstrom"),
    ]
    """Forces on atoms in eV/Å, shape ``[n_atoms][3]``."""

    stress: Annotated[
        list[list[float]],
        Spec(
            (
                "gsr.cartesian_stress_tensor",
                lambda s: [[c * CONSTANTS.au_gpa for c in row] for row in s],
            )
        ),
        Unit("GPa"),
    ]
    """Stress tensor in GPa, shape ``[3][3]``."""

    total_magnetization: Annotated[
        float,
        Spec(("gsr.intgden", _collinear_total_magnetization)),
        Unit("bohr_magneton"),
    ]
    """Total cell magnetization in μ_B (collinear runs only)."""

    magnetization_per_site: Annotated[
        list[float],
        Spec(("gsr.intgden", _collinear_magnetization_per_site)),
        Unit("bohr_magneton"),
    ]
    """Per-atom magnetic moment in μ_B (collinear runs only), shape ``[n_atoms]``."""

    job_done: Annotated[bool, Spec("stdout.job_done")] = False
    """Whether the calculation reached the ``Calculation completed.`` marker. Defaults to ``False`` if not parsed."""

    n_scf_steps: Annotated[int, Spec("stdout.n_scf_steps")]
    """Total number of SCF iterations parsed from the ``.abo`` file."""

    code_version: Annotated[str, Spec("stdout.code_version")]
    """ABINIT version string (e.g. ``"10.4.0"``) parsed from the ``.abo`` header."""


class AbinitOutput(BaseOutput[_AbinitMapping]):
    """Output container for ABINIT ground-state calculations."""

    @classmethod
    def from_dir(cls, directory: Union[str, Path]) -> "AbinitOutput":
        """Construct from an ABINIT calculation directory.

        Looks for a single ``*.abo`` file and a matching ``*_GSR.nc`` file.
        Multi-dataset runs (`_DS{n}_` in filenames) are not handled here.
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise ValueError(f"Path `{directory}` is not a valid directory.")

        abo_candidates = [
            p
            for p in directory.iterdir()
            if p.is_file() and p.suffix == ".abo" and not p.name.endswith(".nc")
        ]
        stdout_file = abo_candidates[0] if len(abo_candidates) == 1 else None

        gsr_file: Optional[Path] = None
        for candidate in directory.iterdir():
            if candidate.is_file() and candidate.name.endswith("_GSR.nc"):
                gsr_file = candidate
                break

        return cls.from_files(stdout=stdout_file, gsr=gsr_file)

    @classmethod
    def from_files(
        cls,
        *,
        stdout: Optional[Union[str, Path]] = None,
        gsr: Optional[Union[str, Path]] = None,
    ) -> "AbinitOutput":
        """Construct from explicit file paths."""
        raw_outputs: dict[str, Any] = {}

        if stdout is not None:
            raw_outputs["stdout"] = AbinitStdoutParser.parse_from_file(stdout)
        if gsr is not None:
            raw_outputs["gsr"] = GsrParser.parse_from_file(gsr)

        return cls(raw_outputs=raw_outputs)
