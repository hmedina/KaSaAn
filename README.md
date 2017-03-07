# KaSaAn: Kappa Snapshot Analysis

## Overview

This provides several tools to analyze Kappa snapshots. Concretely, it implements three classes, a KappaSnapshot is
composed of one or more entities of KappaComplex, themselves composed of one or more entities of KappaAgent.

Several of these methods return objects of the appropriate class. For example, a KappaSnapshot's 
`get_largest_complexes()` returns a list of KappaComplexes.

## Classes

### KappaSnapshot
This class is a glorified dictionary, where the keys are KappaComplexes, and the values are the abundances of those
complexes. The basic methods are re-writings of the core dictionary methods with more explicit names suitable for Kappa.
These serve as foundation for more advanced methods. Currently, the constructor reads from a plain text-file.

Currently implemented methods:
  * `get_all_complexes()`
    * Returns a list of KappaComplexes with all the complexes in the snapshot (i.e. one complex per snapshot line)
  * `get_all_abundances()`
    * Returns a list integers with all the abundances in the snapshot.
  * `get_all_complexes_and_abundances()`
    * Returns a dictionary of all the KappaComplexes as keys and their abundances as values.
  * `get_complexes_with_abundance(query_abundance)`
    * Returns a list of KappaComplexes present at abundance `query_abundance`
  * `get_complexes_of_size(query_size)`
    * Returns a list of KappaComplexes of size (in agents) `query_size`
  * `get_largest_complexes()`
    * Returns the largest (or a list of multiple) KappaComplex(es)
  * `get_smallest_complexes()`
    * Returns the smallest (or a list of multiple) KappaComplex(es)
  * `get_most_abundant_complexes()`
    * Returns the KappaComplex (or list of) present at the highest concentration
  * `get_least_abundant_complexes()`
    * Returns the KappaComplex (or list of) present at the lowest concentration (typically 1)
  * `get_size_distribution()`
    * Returns a list of integers with the size distribution of complexes in the snapshot
  * `plot_size_distribution()`
    * Plots the size distribution (i.e. x: length of polymer, y: abundance of that length)
  * `plot_mass_distribution()`
    * Plots the mass distribution (i.e. x: length of polymer, y: abundance * length of that length)
  
### KappaComplex
This class represents Kappa complexes. Most of the methods return an instance of KappaAgent. To get the raw Kappa
expression, access the instance variable KappaExpression.

Currently implemented methods:
  * `get_number_of_bonds()`
    * Returns an integer with the number of bonds present in the complex
  * `get_size_of_complex()`
    * Returns an integer with the number of agents present in the complex
  * `get_agent_types()`
    * Returns a list of the unique agent names that make up the complex
  * `get_agents()`
    * Returns a list of KappaAgents, with the agents that make up the complex (includes agent signature)
  * `get_number_of_embeddings_of_agent(query)`
    * Returns the number of embeddings a given query `agent(signature)` has on the complex. Single agents only.
  
### KappaAgent
This class represents individual Kappa agents. To get the raw Kappa expression, access the instance variable
KappaExpression.

Currently implemented methods:
  * `contains_site(query_site)`
    * Returns true if the agent contains `query_site`. It supports state identifiers (e.g. `s~a`) and wild-cards
    (e.g. `s!_`).
  
## Requirements
  * [matplotlib](http://matplotlib.org/)