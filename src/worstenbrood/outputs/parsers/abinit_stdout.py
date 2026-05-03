"""Parse the ABINIT main text output (`.abo` file)."""

from __future__ import annotations

import re
from typing import Any

from dough.outputs.parsers.base import BaseOutputFileParser

VERSION_RE = re.compile(r"^\.Version\s+(\S+)\s+of\s+ABINIT", re.MULTILINE)
COMPLETED_RE = re.compile(r"^\s*Calculation completed\.", re.MULTILINE)
SCF_ITER_RE = re.compile(r"^\s*ETOT\s+\d+\s", re.MULTILINE)
TRIM_REMOVED_RE = re.compile(
    r"^---\s*Removed:\s*(\d+)\s+SCF iterations\s*---", re.MULTILINE
)


class AbinitStdoutParser(BaseOutputFileParser):
    """Parse the ABINIT `.abo` main text output.

    Used by `worstenbrood` for triage signals (`job_done`, SCF iteration count,
    code version). Quantitative outputs (energy, forces, stress, structure)
    come from `GSR.nc` instead.
    """

    @staticmethod
    def parse(content: str) -> dict[str, Any]:
        result: dict[str, Any] = {
            "job_done": bool(COMPLETED_RE.search(content)),
        }

        version_match = VERSION_RE.search(content)
        if version_match is not None:
            result["code_version"] = version_match.group(1)

        n_visible = len(SCF_ITER_RE.findall(content))
        n_trimmed = sum(int(m) for m in TRIM_REMOVED_RE.findall(content))
        if n_visible or n_trimmed:
            result["n_scf_steps"] = n_visible + n_trimmed

        return result
