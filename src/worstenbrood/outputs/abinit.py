"""ABINIT output class and output mapping."""

from pathlib import Path
from typing import Annotated, Any, Optional, Union

from dough import Unit
from dough.outputs.base import BaseOutput, output_mapping
from glom import Spec

from worstenbrood import CONSTANTS
from worstenbrood.outputs.parsers.abinit_abo import AbinitAboParser


@output_mapping
class _AbinitMapping:
    """Typed outputs of an ABINIT ground-state calculation."""

    completed: Annotated[bool, Spec("abo.completed")] = False
    """Whether the calculation reached the `Calculation completed.` marker. Defaults to `False` if not parsed."""

    n_scf_steps: Annotated[int, Spec("abo.n_scf_steps")]
    """Total number of SCF iterations parsed from the `.abo` file."""

    code_version: Annotated[str, Spec("abo.code_version")]
    """ABINIT version string (e.g. `"10.4.0"`) parsed from the `.abo` header."""

    total_energy: Annotated[
        float,
        Spec(("abo.total_energy", lambda e: e * CONSTANTS.hartree_to_ev)),
        Unit("eV"),
    ]
    """Final converged total energy in eV (from the `>>>>> Etotal=` block)."""


class AbinitOutput(BaseOutput[_AbinitMapping]):
    """Output container for ABINIT ground-state calculations."""

    @classmethod
    def from_dir(cls, directory: Union[str, Path]) -> "AbinitOutput":
        """Construct from an ABINIT calculation directory.

        Looks for the first `*.abo` file.
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise ValueError(f"Path `{directory}` is not a valid directory.")

        abo_file = next(
            (p for p in directory.iterdir() if p.is_file() and p.suffix == ".abo"),
            None,
        )
        return cls.from_files(abo=abo_file)

    @classmethod
    def from_files(
        cls,
        *,
        abo: Optional[Union[str, Path]] = None,
    ) -> "AbinitOutput":
        """Construct from explicit file paths."""
        raw_outputs: dict[str, Any] = {}

        if abo is not None:
            raw_outputs["abo"] = AbinitAboParser.parse_from_file(abo)

        return cls(raw_outputs=raw_outputs)
