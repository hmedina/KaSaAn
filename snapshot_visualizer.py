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
        data.append({'size': size, 'count': abundance, 'mass': size * abundance, 'composition': composition})
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


def snapshot_composition_simple(data, color_scheme, vis_mode, target_axis, x_res, y_res):
    assert vis_mode == 'size' or vis_mode == 'count' or vis_mode == 'mass', 'Problem: unknown mode <<' + vis_mode + '>>'
    species_num = len(data)

    # First plot the species & their agent composition
    # Sort the data according to visualization mode
    if vis_mode == 'mass':
        sorted_data = sorted(data, key=lambda k: k['mass'], reverse=True)
        areas = [species['mass'] for species in sorted_data]
    elif vis_mode == 'count':
        sorted_data = sorted(data, key=lambda k: k['count'], reverse=True)
        areas = [species['count'] for species in sorted_data]
    else:
        sorted_data = sorted(data, key=lambda k: k['size'], reverse=True)
        areas = [species['size'] for species in sorted_data]
    compositions = [species['composition'] for species in sorted_data]
    # Save value of largest entity, useful for legend annotation
    max_value = max(areas)

    # Normalize the data by specified x/y resolution
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
        composition = compositions[species]
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

    # Add the rectangles to the figure
    target_axis.add_collection(PatchCollection(agent_patches + species_patches, match_original=True))

    return target_axis, max_value


def snapshot_legend_simple(color_scheme, max_mass, max_size, max_count, target_axis):
    # Add entries for maxima at the top
    target_axis.text(x=0, y=4, s='Max mass: ' + str(max_mass), verticalalignment='center')
    target_axis.text(x=0, y=3, s='Max size: ' + str(max_size), verticalalignment='center')
    target_axis.text(x=0, y=2, s='Max count: ' + str(max_count), verticalalignment='center')

    # Add agent entries with their colors (as composition key)
    position = 0 #var to track indexing
    col_num = 5  #number of columns in legend
    # Size of the rectangle serving as color key
    x_dim = 0.5
    y_dim = 0.5
    for agent, color in sorted(color_scheme.items(), key=itemgetter(0), reverse=False):
        y_pos, x_pos = divmod(position, col_num)
        r = matplotlib.patches.Rectangle(xy=[x_pos, -y_pos], width=x_dim, height=y_dim, edgecolor='#000000', fc=color)
        target_axis.add_patch(r)
        target_axis.text(x=x_pos + x_dim, y=-y_pos, s=agent, verticalalignment='baseline')
        position += 1

    target_axis.set_xlim(left=0, right=col_num)
    target_axis.set_ylim(top=4, bottom=-divmod(position, col_num)[0] - 1)
    return target_axis


def snapshot_composition_with_legend(data, color_scheme, target_axis, vis_mode, x_res, y_res):
    assert vis_mode == 'size' or vis_mode == 'count' or vis_mode == 'mass', 'Problem: unknown mode <<' + vis_mode + '>>'
    species_num = len(data)

    # First plot the species & their agent composition
    # Sort the data according to visualization mode
    if vis_mode == 'mass':
        sorted_data = sorted(data, key=lambda k: k['mass'], reverse=True)
        areas = [species['mass'] for species in sorted_data]
    elif vis_mode == 'count':
        sorted_data = sorted(data, key=lambda k: k['count'], reverse=True)
        areas = [species['count'] for species in sorted_data]
    else:
        sorted_data = sorted(data, key=lambda k: k['size'], reverse=True)
        areas = [species['size'] for species in sorted_data]
    compositions = [species['composition'] for species in sorted_data]

    # Normalize the data by specified x/y resolution
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
        composition = compositions[species]
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

    # Add the rectangles to the figure
    target_axis.add_collection(PatchCollection(agent_patches + species_patches, match_original=True))

    # Now to plot the legend
    # Make a list of colored rectangles + agent names
    num_agents = len(color_scheme)
    y_positions = numpy.linspace(start=0, stop=y_res, endpoint=False, num=num_agents+1)

    # Add entry for largest box at the bottom
    largest_area = str(max(areas))
    if vis_mode == 'size':
        l_entry = 'Biggest size: ' + largest_area
    elif vis_mode == 'count':
        l_entry = 'Largest count: ' + largest_area
    else:
        l_entry = 'Greatest mass: ' + largest_area
    target_axis.text(x=x_res * 1.1, y=y_positions[0], s=l_entry, verticalalignment='center')

    # Add agent entries with their colors (as composition key)
    position = 0 #var to get nicely laid-out text entries
    for agent, color in sorted(color_scheme.items(), key=itemgetter(0), reverse=True):
        x_dim = x_res * 0.1
        y_dim = y_res * 0.5 / num_agents
        x_pos = x_res * 1.1
        y_pos = y_positions[position + 1] - y_dim / 2
        r = matplotlib.patches.Rectangle(xy=[x_pos, y_pos], width=x_dim, height=y_dim, edgecolor='#000000', fc=color)
        target_axis.add_patch(r)
        target_axis.text(x=x_res * 1.2, y=y_positions[position + 1], s=agent, verticalalignment='center')
        position += 1

    return target_axis


def render_snapshot(snapshot_file, color_scheme=None, vis_mode='all'):
    # Process the snapshot
    my_snapshot = KappaSnapshot(snapshot_file)
    my_data = process_snapshot(my_snapshot)

    # Determine coloring scheme, unless provided
    if color_scheme:
        my_color_scheme = color_scheme
    else:
        my_color_scheme = colorize_agents(list(my_snapshot.get_agent_types_present()))

    # Define figure definition & resolution
    h_w_ratio = 2/3
    res_w = 1200
    res_h = res_w * h_w_ratio

    fig_width = 8 # Width of default figure box, in inches [?!]
    figure = plt.figure(figsize=[fig_width, fig_width * h_w_ratio])

    # If visualizing all, then we need three subplots (for mass, size, count), plus the area for the legend
    if vis_mode == 'all':
        # Define all three axes
        ax_mass = figure.add_subplot(221, aspect=1)
        ax_size = figure.add_subplot(222, aspect=1)
        ax_count = figure.add_subplot(223, aspect=1)
        ax_legend = figure.add_subplot(224)
        # Draw data onto axes
        ax_mass, my_max_mass = snapshot_composition_simple(data=my_data, color_scheme=my_color_scheme, vis_mode='mass', target_axis=ax_mass, x_res=res_w, y_res=res_h)
        ax_size, my_max_size = snapshot_composition_simple(data=my_data, color_scheme=my_color_scheme, vis_mode='size', target_axis=ax_size, x_res=res_w, y_res=res_h)
        ax_count, my_max_count = snapshot_composition_simple(data=my_data, color_scheme=my_color_scheme, vis_mode='count', target_axis=ax_count, x_res=res_w, y_res=res_h)
        # Add a the legend
        ax_legend = snapshot_legend_simple(color_scheme=my_color_scheme, max_mass=my_max_mass, max_size=my_max_size, max_count=my_max_count, target_axis=ax_legend)

        # Add title onto axes, hide the ticks, re-center the bounding box
        ax_mass.set_title('Area proportional to mass of species')
        ax_size.set_title('Area proportional to size of species')
        ax_count.set_title('Area proportional to count of species')
        ax_mass.axis('off')
        ax_size.axis('off')
        ax_count.axis('off')
        ax_legend.axis('off')
        ax_mass.axis('tight')
        ax_size.axis('tight')
        ax_count.axis('tight')
    else:
        ax = figure.add_subplot(111, aspect=1)
        plt.title(s='Area proportional to ' + vis_mode + ' of species')
        ax = snapshot_composition_with_legend(data=my_data, color_scheme=my_color_scheme, target_axis=ax,
                                              vis_mode=vis_mode, x_res=res_w, y_res=res_h)
        ax.axis('off')
        ax.axis('tight')

    return figure



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
    parser.add_argument('-vm', '--visualization_mode', choices=['all', 'mass', 'count', 'size'], type=str, default='all',
                        help='Type of visualization: size displays biggest species largest; '
                            'count displays most abundant species largest; mass is the '
                            'product of size times abundance, indicative of "where is the '
                            'bulk of my system".')
    parser.add_argument('-of', '--output_file', type=str,
                        help='Optional name of file to save the view to instead of displaying it on screen. Extension'
                             ' dictates the format. Valid choices include PNG, PDF, SVG (anything supported by'
                             ' MatPlotLib).')
    args = parser.parse_args()

    fig = render_snapshot(snapshot_file=args.snapshot_file,
                    color_scheme=args.coloring_scheme,
                    vis_mode=args.visualization_mode)

    # Either save figure to file, or plot it
    if args.output_file:
        plt.savefig(args.output_file, bbox_inches='tight')
    else:
        plt.show()