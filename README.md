# KaSaAn: Kappa Snapshot Analysis

## Overview
This provides several tools to analyze Kappa snapshots. Concretely, it
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

This tool is compatible with KaSim syntax 4.


## Classes


### KappaSnapshot
This class represents KappaSnapshots. It contains a dictionary, where
the keys are KappaComplexes, and the values are the abundances of those
complexes. The basic methods are re-writings of the core dictionary
methods with more explicit names suitable for Kappa. These serve as
foundation for more advanced methods. Currently, the initializer can
only read from a plain text-file.

Currently implemented methods:
  * `get_snapshot_file_name()`
     * Returns a string with the name of the file this snapshot came from.
  * `get_snapshot_time()`
     * Returns a float with the time at which this snapshot was taken.
  * `get_snapshot_uuid()`
     * Returns a string with the snapshot's UUID.
  * `get_snapshot_event()`
     * Returns an integer with the event number the snapshot was taken at.
  * `get_all_complexes()`
    * Returns a list of KappaComplexes with all the complexes in the snapshot (i.e. one complex per snapshot line).
  * `get_all_abundances()`
    * Returns a list integers with all the abundances in the snapshot.
  * `get_all_sizes()`
    * Returns a list of integers with all the complex sizes visible in the snapshot, one item per complex (i.e. can contain repeat numbers if they correspond to different complexes).
  * `get_all_complexes_and_abundances()`
    * Returns a list of tuples (technically an ItemsView object) of the KappaComplexes and their abundances.
  * `get_total_mass()`
    * Returns an int with the total mass in the snapshot (i.e. the number of agents).
  * `def get_agent_types_present():`
    * Returns a set of KappaAgents of the names of the agents present in the snapshot (i.e. ignores agent signatures).
  * `get_complexes_with_abundance(query_abundance)`
    * Returns a list of KappaComplexes present at abundance `query_abundance` (integer: number of molecules).
  * `get_complexes_of_size(query_size)`
    * Returns a list of KappaComplexes of size `query_size` (integer: number of agents).
  * `get_largest_complexes()`
    * Returns a list of the largest KappaComplexes.
  * `get_smallest_complexes()`
    * Returns a list of the smallest KappaComplexes.
  * `get_most_abundant_complexes()`
    * Returns a list of the most abundant KappaComplexes.
  * `get_least_abundant_complexes()`
    * Returns a list of the least abundant KappaComplexes.
  * `get_size_distribution()`
    * Returns a list of integers with the size distribution of complexes in the snapshot.
  * `get_all_tokens()`
    * Returns a dictionary where the key is a KappaToken, and the value the numeric value of the token in this snapshot.
  * `get_value_of_token(query_token)`
    * Returns a float with the numeric value of `query_token`.
  * `get_tokens_present()`
    * Returns a list of KappaTokens with the tokens present in the snapshot.

```
>>> from KaSaAn import KappaSnapshot
>>> foo = KappaSnapshot('E_10000.ka')
>>> print(foo)
%init: 5 B(s[1]{#}), S(a[.]{#} b[1]{#} m[.]{#} n[.]{#})
%init: 45 B(s[.]{#})
%init: 24 A(s[1]{#}), S(a[1]{#} b[.]{#} m[.]{#} n[.]{#})
%init: 476 A(s[.]{#})
%init: 2 S(a[.]{#} b[.]{#} m[.]{#} n[1]{#}), S(a[.]{#} b[.]{#} m[1]{#} n[.]{#})
%init: 108 S(a[.]{#} b[.]{#} m[.]{#} n[.]{#})
>>> foo.get_size_distribution()
{2: 31, 1: 629}
```


### KappaComplex
This class represents Kappa complexes. Most of the methods return an
instance of KappaAgent.

Currently implemented methods:
  * `get_number_of_bonds()`
    * Returns an integer with the number of bonds present in the complex.
  * `get_size_of_complex()`
    * Returns an integer with the number of agents present in the complex.
  * `get_agent_types()`
    * Returns a set of KappaAgents, with the agent names that make up the complex.
  * `get_all_agents()`
    * Returns a list of KappaAgents, with all the agents that make up the complex (includes agent signature).
  * `get_number_of_embeddings_of_agent(query)`
    * Returns an integer with the number of embeddings a given query `agent(signature)` has on the complex. The query
    must be a KappaAgent, KappaSite, or KappaCounter, or a string that can be parsed into any of those.
  * `get_complex_composition(self)`
    * Returns a dictionary where the key is an agent name, and the value the number of times that agent appears in this
     complex.

```
>>> bar = foo.get_largest_complexes()[0]
>>> print(bar)
B(s[1]{#}), S(a[.]{#} b[1]{#} m[.]{#} n[.]{#})
>>> bar.get_number_of_embeddings_of_agent('S(b[_])')
1
```
 
  
### KappaAgent
This class represents individual Kappa agents. It supports checking for containment through the `in` keyword. The query
must be a KappaAgent, KappaSite, or KappaCounter, or a string that can be parsed into any of those.

Currently implemented methods:
  * `get_agent_name()`
    * Returns a string with the agent's name.
  * `get_agent_signature()`
    * Returns true if the agent contains `query_site`, included is the check against internal and bond states, e.g.
     `my_agent.contains_site_with_states(foo{bar}[.])`
  * `get_bond_identifiers()`
    * Returns a list of strings with the bond identifiers that start/end at this agent. For example, for the KappaAgent
    `A(a[.] b[1] c[2] d{a}[.])` these would be the list `['1','2']`.
 
```
>>> baz = bar.get_all_agents()[1]
>>> print(baz)
S(a[.]{#} b[1]{#} m[.]{#} n[.]{#})
>>> 'm[#]' in baz
True
>>> 'n[_]' in baz
False
```


### KappaPort
This class represents "vanilla" Kappa sites, i.e. sites capable of having internal states and bond states, unlike
counter sites. It supports checking for containment through the `in` keyword. The query
must be a KappaSite, or a string that can be parsed into one.

Currently implemented methods:
  * `get_port_name()`
    * Returns a string with the name of the port.
  * `get_port_int_state()`
    * Returns a string with the internal state of the port, or hash sign (i.e. wildcard) if undeclared.
  * `get_port_bond_state()`
    * Returns a string with the bond identifier of the port, a period if unbound, or a hash sign (i.e. wildcard)
    if undeclared.
    
```
>>> fitz = baz.get_agent_signature()[0]
>>> print(fitz)
a[.]{#}
>>> fitz.get_port_int_state()
'#'
>>> 'a[_]' in fitz
False
>>> 'a[#]' in fitz
True
```


### KappaCounter
This class represents counter Kappa "sites", i.e. sites that hold a numeric value in an instance-specific manner, which
can be used as a variable in rule rates (e.g. level of phosphorylation of a protein).

Currently implemented methods:
  * `get_counter_name()`
    * Returns a string with the name of the counter.
  * `get_counter_value()`
    * Returns an integer with the value of the counter.
    
```
>>> from KaSaAn import KappaCounter
>>> botz = KappaCounter('g{=5}')
>>> print(botz)
g{=5}
>>> botz.get_counter_value() > 4
True
>>> botz.get_counter_value() > 6
False
```


## Visualization
Scripts are provided for visualization of different Kappa entities: snapshots, traces, and rules.


### Snapshot visualization
These scripts use the patchwork / treemap layout. Each molecular species is displayed as a box with a black boundary.
Within each species, its composition is displayed as boxes corresponding to the abundance of agents in that species: an
agent's abundance within that complex is proportional to the area it occupies within the species. All areas are set to
the same scale, so the size of the box of one agent type in one species can be compared to the size of the box of a
different agent type in a different species.
 
Three ways of determining an species's weight are offered: by count (i.e. how many of it there are), by size
(i.e. how many agents it has), and by mass (i.e. the product of the count times the size).

Giant species tend to be rare; tiny species tend to be frequent; when
thinking about the state of the mixture (i.e. "where are my agents?"),
it may be useful to resolve the size vs. rarity trade-off through
their product, hence the `mass` mode is presented.


#### Count
```
$ ./visualization/snapshot_visualizer.py -sf ./models/alphabet_soup_snap.ka -vm count -of ./models/alphabet_soup_snap_count.png
```
![Visualization by species count](./models/alphabet_soup_snap_count.png)

Each black-bounded box represents a species, with its area proportional to
the number of times that species is present in the mixture. Here we can
see the mixture is composed of a large set of species at very similar
abundance levels (e.g. a gazillion types of dimers).


#### Size
```
$ ./visualization/snapshot_visualizer.py -sf ./models/alphabet_soup_snap.ka -vm size -of ./models/alphabet_soup_snap_size.png
```
![Visualization by species size](./models/alphabet_soup_snap_size.png)

When sorting by size of the species, keep in mind that a single species
is surrounded by a black box. In this image, an enormous species
dominates the view. The next largest species is a very distant second.
There is one type of species that is very large.


#### Mass
```
$ ./visualization/snapshot_visualizer.py -sf ./models/alphabet_soup_snap.ka -vm mass -of ./models/alphabet_soup_snap_mass.png
```
![Visualization by species mass](./models/alphabet_soup_snap_mass.png)

When sorting by the mass of species, we are asking "what is the bulk of
my mixture doing?". I.e. is my mixture dominated by a very large number
of small species, or a very small number of large species? Here we see
there is a giant component that dominates the bulk of the mixture,
having recruited ~4/5ths of the entire mixture (i.e. its area is ~4/5ths
of the entire patchwork / mixture).


#### All
```
$ ./visualization/snapshot_visualizer.py -sf ./models/alphabet_soup_snap.ka -vm all -of ./models/alphabet_soup_snap_all.png
```
![Visualization by species count, size, and mass](./models/alphabet_soup_snap_all.png)

It is difficult to view this entity when viewing by `count` alone, as there
is a very low number of copies of it (probably only one). When viewing
by `size`, it however is the only species that is appreciable. When
viewed by `mass`, it is clear it is an important species.




## Requirements
Python 3.7 or above.

For snapshot analysis: none.

For visualization scripts (of rules, snapshots, or traces): 
* matplotlib 3.0.2
* squarify 0.3.0
