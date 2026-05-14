# worstenbrood

A [`dough`](https://mbercx.github.io/dough/)-based wrapper of [ABINIT](https://www.abinit.org) with strong typing.

`worstenbrood` parses ABINIT output into a typed namespace.
This initial slice covers the `.abo` text output only; quantitative outputs from `GSR.nc` (energies, forces, stress, structure, magnetization) will follow.

## Install

```bash
pip install worstenbrood
```

## Quickstart

```python
from worstenbrood.outputs import AbinitOutput

out = AbinitOutput.from_dir("/path/to/abinit/run")

out.outputs.completed       # bool — did ABINIT print "Calculation completed."?
out.outputs.n_scf_steps     # int — total SCF iterations
out.outputs.code_version    # str — e.g. "10.4.0"
out.outputs.total_energy    # eV — converged total energy
```

`out.list_outputs()` returns the names of fields that successfully resolved.
Accessing a field that wasn't parsed raises `AttributeError` with a clear message.
