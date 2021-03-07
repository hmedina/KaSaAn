#!/usr/bin/env python3
"""
Tools and utilities for analyzing Kappa objects. The `scripts` submodule contains command line utilities (installed via SetupTools EntryPoints under the namespace `kappa_[object type]`), for which the functions are located under `functions`. A low-level API is provided under `core`.

To view the set of installed scripts, view the `setup.py` file. Examples include:

* `kappa_observable_coplotter`, to plot the a specific observable name jointly from multiple observable files (e.g. `data.csv`)
* `kappa_snapshot_visualizer_network`, to plot a snapshot as a ball & stick network
* `kappa_trace_movie_maker`, to make a gif of a series of snapshots derived from a trace to visualize the size and composition of the mixture through time

"""