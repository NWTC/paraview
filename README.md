# paraview
Scripts for Paraview batch processing (using pvbatch)

Sample Peregrine environment:
```bash
Currently Loaded Modulefiles:
  1) gcc/4.8.2                 2) openmpi-gcc/1.7.3-4.8.2   3) python/2.7.6              4) paraview/4.2.0-compute
```

Sample usage:
```bash
pvbatch slice2D_to_png.py U_slice_horizontal_z080.yaml
```

The system version of Peregrine depends on an antiquated system python module (and it won't work with conda). Additional dependencies, e.g. yaml, may be installed as follows:
```bash
pip install --install-option="--prefix=$HOME" pyyaml
```
Of course, be sure to set up your environment accordingly:
```bash
export PYTHONPATH="$HOME:$PYTHONPATH"
```
