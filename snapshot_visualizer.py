#! /usr/bin/python3

import squarify
import matplotlib.pyplot as plt
import matplotlib.patches
import matplotlib as mpl
import colorsys
import numpy
from matplotlib.collections import PatchCollection
from kappa4_snapshot_analysis import KappaSnapshot

# Read and process data
my_snap = KappaSnapshot('models/cyclic_polyvalent_polymers_snap.ka')

# Generate & associate colors as a dictionary {Agent: Color}
agent_types = list(my_snap.get_agent_types_present())
num_agents = len(agent_types)
agent_colors = {}
if num_agents <= len(mpl.rcParams['axes.prop_cycle']):
    for agent in range(num_agents):
        agent_colors[agent_types[agent]] = 'C' + str(agent)
else:
    # ToDO test this color scheme for snapshots with over 10 agents
    h = numpy.linspace(start=0, stop=1, num=num_agents, endpoint=False)
    for agent in range(num_agents):
        agent_colors[agent_types[agent]] = colorsys.hsv_to_rgb(h[agent], 0.5, 0.5)

my_data = []
for my_complex, my_abundance in my_snap.get_all_complexes_and_abundances():
    my_size = my_complex.get_size_of_complex()
    my_composition = my_complex.get_complex_composition()
    my_data.append([my_size, my_abundance, my_composition])

num_species = len(my_data)

# Sort data
size_sort = sorted(my_data, key=lambda foo: foo[0], reverse=True)
abundance_sort = sorted(my_data, key=lambda foo: foo[1], reverse=True)
mass_sort = sorted(my_data, key=lambda foo: foo[0] * foo[1], reverse=True)

# Define mass resolution: my_width * my_height = total "pixels" of mass
my_width = 1000
my_height = 1000
my_x = 0
my_y = 0

# Normalize the species by the different metrics: size|abundance|mass
my_sizes = [item[0] for item in size_sort]
#my_abundances = [item[1] for item in size_sort]
#my_masses = [item[0] * item[1] for item in size_sort]
my_sizes = squarify.normalize_sizes(sizes=my_sizes, dy=my_width, dx=my_height)
#my_abundances = squarify.normalize_sizes(sizes=my_abundances, dy=my_width, dx=my_height)
#my_masses = squarify.normalize_sizes(sizes=my_masses, dy=my_width, dx=my_height)

# Determine the "species canvases" i.e. the rectangle that represents a single species and holds the sub-rectangles that
# represent its composition
species_canvases = squarify.padded_squarify(sizes=my_sizes, x=my_x, y=my_y, dy=my_width, dx=my_height)
#abundances_rects = squarify.padded_squarify(sizes=my_abundances, x=my_x, y=my_y, dy=my_width, dx=my_height)
#masses_rects = squarify.padded_squarify(sizes=my_masses, x=my_x, y=my_y, dy=my_width, dx=my_height)


agent_patches = []
for species in range(num_species):
    # Determine the agent composition of this species
    composition = size_sort[species][2]
    agent_count = [composition[k] for k in sorted(composition, key=composition.get, reverse=True)]
    agent_type = [k for k in sorted(composition, key=composition.get, reverse=True)]
    # Calculate the sub-rectangles to draw on this rectangle / canvas
    species_canvas = species_canvases[species]
    normalized_agent_count = squarify.normalize_sizes(sizes=agent_count,
                                                      dx=species_canvas['dx'],
                                                      dy=species_canvas['dy'])
    agent_rectangles = squarify.squarify(sizes=normalized_agent_count,
                                         x=species_canvas['x'],
                                         y=species_canvas['y'],
                                         dy=species_canvas['dy'],
                                         dx=species_canvas['dx'])
    # Draw the rectangles using the appropriate color (determined by the agent type)
    for agent in range(len(agent_rectangles)):
        agent_rectangle = agent_rectangles[agent]
        r = matplotlib.patches.Rectangle(xy=[agent_rectangle['x'],agent_rectangle['y']],
                                         width=agent_rectangle['dx'],
                                         height=agent_rectangle['dy'],
                                         facecolor=agent_colors[agent_types[agent]])
        agent_patches.append(r)

agent_collection = PatchCollection(agent_patches, match_original=True)

# Create rectangle containers for the species themselves
species_patches = []
for c in species_canvases:
    r = matplotlib.patches.Rectangle(xy=[c['x'],c['y']], width=c['dx'], height=c['dy'], color='#88888888')
    species_patches.append(r)

species_collection = PatchCollection(species_patches, match_original=True)

fig, ax = plt.subplots(1)
ax.add_collection(species_collection)
ax.add_collection(agent_collection)

ax.axis('off')
ax.axis('equal')
ax.axis('tight')

plt.show()
