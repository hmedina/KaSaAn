# Command line scripts

Some of these command line scripts are added as entry-points (see `setup.py`, mostly the same name but with `kappa_` prefixed to group by namespace). This is a brief overview of these files. All of them are documented internally, use `--help` for full details. The scripts operate as wrappers that parse arguments, with the functions located under `KaSaAn/functions`.

### `catalytic_potential.py`
Out of a series of snapshots from a simulation, obtain the catalytic potential of each snapshot, and save the list as a CSV file. The catalytic potential of a state, a snapshot, is the sum of the catalytic potentials over all the constituent species. The potential of a species is the product of the number of bound enzyme agents, times the number of bound substrate agents, times the abundance of that species.

### `observable_plotter.py`
Plot a set of observables against time from the observable's file produced by KaSim. The `-d` option toggles "differential" mode, useful for transforming a cumulative token into an instantaneous rate. The `-p` option prints the list of observables to a CSV, where the line number is the index value this script understands. This is useful for models with large number of observables, where plotting a subset is desired.

### `observable_coplotter.py`
Similar to the `observable_plotter.py` script, but this allows one to plot a single observable from a set of different observable files. When running replicates, it is sometimes useful to coplot the trajectories of key observables in the different simulation outputs. Each observable value will be plotted against its own time definition, so this is resilient against varying time samplings. This script also allows `-d` for "differential" mode.

### `snapshot_visualizer_network.py`
Visualize a kappa snapshot as a plain graph. The script allows one to define a custom coloring scheme for agents; as MatPlotLib understands RGBA tuples, one can set transparency values to show/hide some agents, or focus the view on others. Moreover, the script allows via `-p` a list of kappa patterns; the script will generate a figure with all the nodes colored, and then a figure for each of those patterns, coloring only the agents that match that pattern. This allows multiple views while using a single layout call, which is quite costly for large networks. Moreover, it also allows consistent coloring. The combination of consistent locations and consistent coloring schemes allow one to compare the all-agents snapshot with the pattern-matched one easily.

Coloring all nodes:
![Snapshot as a plain graph](../../models/kite_snap_network.png)

Coloring only nodes that match a specific pattern:
![Snapshot contents that match a pattern](../../models/kite_snap_network_0.png)

### `snapshot_visualizer_patchwork.py`
Visualize a kappa snapshot using a patchwork layout, where the area colored is proportional to the metric assayed. Metrics supported are mass (default), size, or count of each molecular species. Composition of each species is also displayed.

![Snapshot as a patchwork](../../models/kite_snap_patchwork.png)
Same snapshot as above, but viewed as a patchwork. The biggest species is the heptamer, but the greates mass is in the hexamers, as there's two of them.
