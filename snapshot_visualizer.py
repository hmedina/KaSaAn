#! /usr/bin/python3

import squarify
import matplotlib.pyplot as plt
import matplotlib.patches
import matplotlib as mpl
import colorsys
import numpy
from matplotlib.collections import PatchCollection
from kappa4_snapshot_analysis import KappaSnapshot
from operator import itemgetter
import argparse


def process_snapshot(snapshot):
    # Extract the relevant information from a snapshot: size, abundance, & compositions
    data = []
    for kappa_complex, abundance in snapshot.get_all_complexes_and_abundances():
        size = kappa_complex.get_size_of_complex()
        composition = kappa_complex.get_complex_composition()
        data.append([size, abundance, composition])

    return data


def colorize_agents(agent_list):
    # Generate & associate colors as a dictionary {Agent: Color}
    num_agents = len(agent_list)
    agent_colors = {}
    # Use a built-in palette unless there are too many agents
    if num_agents <= len(mpl.rcParams['axes.prop_cycle']):
        for agent in range(num_agents):
            agent_colors[agent_list[agent]] = 'C' + str(agent)
    else:
        h = numpy.linspace(start=0, stop=1, num=num_agents, endpoint=False)
        for agent in range(num_agents):
            agent_colors[agent_list[agent]] = colorsys.hsv_to_rgb(h[agent], 0.5, 0.75)
    return agent_colors


def snapshot_composition(data, color_scheme, vis_mode, x_res, y_res):
    assert vis_mode == 'size' or vis_mode == 'count' or vis_mode == 'mass', 'Problem: unknown mode <<' + vis_mode + '>>'

    species_num = len(data)

    # Define & organize the data that we'll be plotting
    area_and_composition = []
    for species in range(species_num):
        species_entry = my_data[species]
        species_size = species_entry[0]
        species_abundance = species_entry[1]
        species_mass = species_entry[0] * species_entry[1]
        species_composition = species_entry[2]
        if vis_mode == 'size':
            area_and_composition.append([species_size, species_composition])
        elif vis_mode == 'count':
            area_and_composition.append([species_abundance, species_composition])
        else:
            area_and_composition.append([species_mass, species_composition])

    # Sort the data decreasing by magnitude
    sorted_area_and_composition = sorted(area_and_composition, key=lambda foo: foo[0], reverse=True)

    # Normalize the data by specified x/y resolution
    areas = [a[0] for a in sorted_area_and_composition]
    comps = [a[1] for a in sorted_area_and_composition]
    areas = squarify.normalize_sizes(sizes=areas, dy=y_res, dx=x_res)
    species_canvases = squarify.padded_squarify(sizes=areas, x=0, y=0, dy=y_res, dx=x_res)

    # Determine the rectangles that make up each species, i.e. composition
    agent_patches = []
    species_patches = []
    for species in range(species_num):
        # Define the box that represents this species as a whole
        species_canvas = species_canvases[species]
        s = matplotlib.patches.Rectangle(xy=[species_canvas['x'],species_canvas['y']],
                                         width=species_canvas['dx'],
                                         height=species_canvas['dy'],
                                         facecolor='#00000000',
                                         edgecolor='#000000ff')
        species_patches.append(s)
        # Determine the agent composition of this species
        composition = comps[species]
        agent_count = [composition[k] for k in sorted(composition, key=composition.get, reverse=True)]
        agent_type = [k for k in sorted(composition, key=composition.get, reverse=True)]
        # Calculate the sub-rectangles to draw on this rectangle / canvas
        normalized_agent_count = squarify.normalize_sizes(sizes=agent_count,
                                                          dx=species_canvas['dx'],
                                                          dy=species_canvas['dy'])
        agent_rectangles = squarify.squarify(sizes=normalized_agent_count,
                                             x=species_canvas['x'],
                                             y=species_canvas['y'],
                                             dy=species_canvas['dy'],
                                             dx=species_canvas['dx'])
        # Draw the rectangles using the appropriate color (determined by the agent type)
        for a in range(len(agent_type)):
            agent_rectangle = agent_rectangles[a]
            r = matplotlib.patches.Rectangle(xy=[agent_rectangle['x'],agent_rectangle['y']],
                                             width=agent_rectangle['dx'],
                                             height=agent_rectangle['dy'],
                                             facecolor=color_scheme[agent_type[a]])
            agent_patches.append(r)

    agent_collection = PatchCollection(agent_patches + species_patches, match_original=True)
    return agent_collection


def composition_legend(color_scheme, x_res, y_res, axis):
    # Make a list of colored rectangles + agent names
    num_agents = len(color_scheme)
    y_positions = numpy.linspace(start=0, stop=y_res, endpoint=False, num=num_agents+1)
    # Dumb var to get nicely laid-out text entries
    position = 0
    for agent, color in sorted(color_scheme.items(), key=itemgetter(0), reverse=True):
        x_dim = x_res * 0.1
        y_dim = y_res * 0.5 / num_agents
        x_pos = x_res * 1.1
        y_pos = y_positions[position + 1] - y_dim / 2
        r = matplotlib.patches.Rectangle(xy=[x_pos, y_pos],
                                         width=x_dim,
                                         height=y_dim,
                                         edgecolor='#000000',
                                         facecolor=color)
        axis.add_patch(r)
        axis.text(x=x_res * 1.2,
                  y=y_positions[position + 1],
                  s=agent,
                  verticalalignment='center')
        position += 1

    return axis


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visualize a kappa snapshot using a patchwork layout, where the area '
                                                 'colored is proportional to the metric assayed. Metrics supported are '
                                                 'mass (default), size, or count of each molecular species. Composition '
                                                 'of each species is also displayed.')
    parser.add_argument('-sf', '--snapshot_file', type=str, required=True,
                        help='Name of the snapshot file to be viewed.')
    parser.add_argument('-cs', '--coloring_scheme', type=dict,
                        help='Optional dictionary with color scheme to use for species composition. If not provided, '
                             'one will be generated. It /may/ not match one generated by a different snapshot.')
    parser.add_argument('-vm', '--visualization_mode', choices=['mass', 'count', 'size'], type=str, default='mass',
                        help='Type of visualization: size displays biggest species largest; '
                            'count displays most abundant species largest; mass is the '
                            'product of size times abundance, indicative of "where is the '
                            'bulk of my system".')
    parser.add_argument('-of', '--output_file', type=str,
                        help='Optional name of file to save the view to instead of displaying it on screen. Extension'
                             ' dictates the format. Valid choices include PNG, PDF, SVG (anything supported by'
                             ' MatPlotLib).')
    args = parser.parse_args()

    # Process the snapshot
    my_snapshot = KappaSnapshot(args.snapshot_file)
    my_data = process_snapshot(my_snapshot)

    # Determine coloring scheme, unless provided
    if args.coloring_scheme:
        my_color_scheme = args.coloring_scheme
    else:
        my_color_scheme = colorize_agents(list(my_snapshot.get_agent_types_present()))

    # Define figure definition & resolution
    w_h_ratio = 2/3
    res_w = 1200
    res_h = res_w * w_h_ratio

    fig_width = 8 # Width of default figure box, in inches [?!]
    fig = plt.figure(figsize=[fig_width, fig_width * w_h_ratio])
    ax = fig.add_subplot(1, 1, 1, aspect=1)

    # Define composition & view mode
    my_vis_mode = args.visualization_mode
    ax.add_collection(snapshot_composition(data=my_data,
                                           color_scheme=my_color_scheme,
                                           vis_mode=my_vis_mode,
                                           x_res=res_w,
                                           y_res=res_h))
    plt.title(s='Area proportional to ' + my_vis_mode + ' of species')
    ax = composition_legend(my_color_scheme, res_w, res_h, ax)

    ax.axis('off')
    ax.axis('equal')
    ax.axis('tight')

    # Either save figure to file, or plot it
    if args.output_file:
        plt.savefig(args.output_file, bbox_inches='tight')
    else:
        plt.show()