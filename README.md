# KaSaAn: Kappa Snapshot Analysis

## Overview
This provides several tools to analyze [Kappa](https://kappalanguage.org/) snapshots. Concretely, it
implements Kappa-centric classes, and a whole-mix visualizer.

Snapshots are represented as instances of the class KappaSnapshot. Within snapshots, molecular species are represented
as instances of the class KappaComplex. Within complexes, proteins/agents are represented as instances of the class
KappaAgent. Within agents, sites are represented as instances of either KappaPort (i.e. sites with internal state and/or
bond state), or KappaCounter (i.e. sites with a numeric value that can be tested and used for dynamic rule rates).
Tokens are represented as instances of the class KappaToken.

In other words, in addition to KappaTokens, a KappaSnapshot is composed of one or more entities of KappaComplex,
themselves composed of one or more entities of KappaAgent, themselves composed of one or more entities of KappaPort
and/or KappaCounter.

Several of these methods return objects of the appropriate class. For example, a KappaSnapshot's
`get_largest_complexes()` returns a list of KappaComplexes. 

This tool is compatible with [KaSim](https://github.com/Kappa-Dev/KaSim/) syntax 4.


## Classes
See readme file in [KaSaAn/KaSaAn/core](./KaSaAn/core/README.md)

## Visualization
See readme file in [KaSaAn/KaSaAn/scripts](./KaSaAn/scripts/README.md)

![Snapshot as network](./models/kite_snap_network.png)


## Requirements
General:
* Python 3.7 or above

For visualization scripts:
* Python packages:
  * numpy
  * matplotlib
  * squarify
* ffmpeg for writing mp4 movies of traces
* imagemagick for writing gifs of traces
* an X server, like Xming under Windows / Windows Subsystem for Linux

On the Kappa Side:
* Kappa Simulator [KaSim](https://github.com/Kappa-Dev/KaSim) v4 or above.
For executing models, producing snapshots, producing traces, etc.

* Trace Query Language engine [TQL](https://github.com/jonathan-laurent/Kappa-TQL).
For querying a trace to, for example, obtain periodic snapshots.


