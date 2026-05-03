# worstenbrood

A `dough`-based wrapper of [ABINIT](https://www.abinit.org) with strong typing.

`worstenbrood` parses ABINIT ground-state output (`.abo` text + `GSR.nc` netCDF) into a typed namespace.
Quantities are exposed in user-facing units (eV, Å, eV/Å, GPa, μ_B); the parsers stay in ABINIT's native atomic units and the Specs convert.

## Install

```bash
pip install worstenbrood
```

`netCDF4` is a hard dependency: nearly every ABINIT user reaches for trajectory and phonon files (NetCDF) within the first calculation.

## Quickstart

```python
from worstenbrood.outputs import AbinitOutput

out = AbinitOutput.from_dir("/path/to/abinit/run")

out.outputs.total_energy           # eV
out.outputs.fermi_energy           # eV
out.outputs.structure              # {"symbols": [...], "cell": [[...]], "positions": [[...]]}
out.outputs.forces                 # eV/Å, shape (n_atoms, 3)
out.outputs.stress                 # GPa, 3×3
out.outputs.total_magnetization    # μ_B (collinear spin runs only)
out.outputs.job_done               # bool — did ABINIT print "Calculation completed."?
```

`out.list_outputs()` returns the names of fields that successfully resolved.
Accessing a field that wasn't parsed raises `AttributeError` with a clear message.
