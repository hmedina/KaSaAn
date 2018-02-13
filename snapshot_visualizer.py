#! /usr/bin/python3

import squarify
import matplotlib.pyplot as plt
import matplotlib.patches
from matplotlib.collections import PatchCollection
from kappa4_snapshot_analysis import KappaSnapshot

# Read and process data
my_snap = KappaSnapshot('models/cyclic_polyvalent_polymers_snap.ka')
# ToDo Generate & associate colors
num_colors = len(my_snap.get_agent_types_present())

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

# Normalize data
my_sizes = [item[0] for item in size_sort]
#my_abundances = [item[1] for item in size_sort]
#my_masses = [item[0] * item[1] for item in size_sort]

my_sizes = squarify.normalize_sizes(sizes=my_sizes, dy=my_width, dx=my_height)
#my_abundances = squarify.normalize_sizes(sizes=my_abundances, dy=my_width, dx=my_height)
#my_masses = squarify.normalize_sizes(sizes=my_masses, dy=my_width, dx=my_height)

# Create rectangle containers for species
sizes_rects = squarify.padded_squarify(sizes=my_sizes, x=my_x, y=my_y, dy=my_width, dx=my_height)
#abundances_rects = squarify.padded_squarify(sizes=my_abundances, x=my_x, y=my_y, dy=my_width, dx=my_height)
#masses_rects = squarify.padded_squarify(sizes=my_masses, x=my_x, y=my_y, dy=my_width, dx=my_height)

# Create rectangle containers for species composition
agent_patches = []
for species in range(num_species):
    composition = my_data[species][2]
    agent_count = [composition[k] for k in sorted(composition, key=composition.get, reverse=True)]
    agent_type = [k for k in sorted(composition, key=composition.get, reverse=True)]

    c = sizes_rects[species]
    rectangles = squarify.squarify(sizes=agent_count, x=c['x'], y=c['y'], dy=c['dy'], dx=c['dx'])
    for agent in rectangles:
        r = matplotlib.patches.Rectangle(xy=[agent['x'],agent['y']], width=agent['dx'], height=agent['dy'], facecolor='#888888')
        agent_patches.append(r)

agent_collection = PatchCollection(agent_patches, match_original=True)

    # ToDo assign colors to each rectangle based on what agent it colors:

species_patches = []
for c in sizes_rects:
    r = matplotlib.patches.Rectangle(xy=[c['x'],c['y']], width=c['dx'], height=c['dy'], facecolor='#ffffff', edgecolor='#000000')
    species_patches.append(r)

species_collection = PatchCollection(species_patches, match_original=True)

fig, ax = plt.subplots(1)
ax.add_collection(species_collection)
ax.add_collection(agent_collection)

ax.axis('off')
ax.axis('equal')
ax.axis('tight')

plt.show()
