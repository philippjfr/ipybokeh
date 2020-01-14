
# ipybokeh

[![Build Status](https://travis-ci.org/pyviz/ipybokeh.svg?branch=master)](https://travis-ci.org/pyviz/ipybokeh)
[![codecov](https://codecov.io/gh/pyviz/ipybokeh/branch/master/graph/badge.svg)](https://codecov.io/gh/pyviz/ipybokeh)


A Jupyter widget for rendering bokeh. This prototype has since been moved into the [official Bokeh Jupyter extension](https://github.com/bokeh/jupyter_bokeh).

## Installation

You can install using `pip`:

```bash
pip install ipybokeh
```

Or if you use jupyterlab:

```bash
pip install ipybokeh
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

If you are using Jupyter Notebook 5.2 or earlier, you may also need to enable
the nbextension:
```bash
jupyter nbextension enable --py [--sys-prefix|--user|--system] ipybokeh
```
