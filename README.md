# fre-python-tools
Python-based tools and interfaces to be used by FRE workflows

## Install fre-python-tools and dependencies with conda

`fre-python-tools` is available on NOAA-GFDL's anaconda channel.
To create a new conda environment containing `fre-python-tools`:

```
conda create --name fre-python-tools fre-python-tools --channel=noaa-gfdl
```

Then, activate the environment to bring fre-python-tools libraries and scripts into your PATH.

```
conda activate fre-python-tools
```

## Install dependencies only with conda

For developing `fre-python-tools`, we recommend installing the dependencies
with conda. Then, one can import and use `fre-python-tool` libraries
and run `pytest` tests.

1. Create conda environment with fre-python-tool dependencies
```
conda env create --file environment.yml
```

2. Activate conda environment

```
conda activate fre-python-tools-dev
```

3. Run tests

While fre-python-tools is not installed in your environment,
you can run tests on the checked-out code with `python -m pytest`
(compared to `pytest` which does NOT add the current directory to `sys.path`.)

```
python -m pytest
```

There should be no errors. You may get a harmless
warning regarding the deprecation of `sre_constants` within the `metomi.isodatetime`
package.

## Build conda package

To test the conda packaging, you can build the fre-python-tools package using conda-build.

1. Install conda-build (into either an isolated conda environment or the base environment)

```
conda install conda-build
```

2. Build fre-python-tools

```
conda build .
```
