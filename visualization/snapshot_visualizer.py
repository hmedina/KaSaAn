#! /usr/bin/python3

import squarify
import matplotlib.pyplot as plt
import matplotlib.patches
import matplotlib.text
import matplotlib as mpl
import colorsys
import numpy
from matplotlib.collections import PatchCollection
from KaSaAn import KappaSnapshot
from operator import itemgetter
import argparse
from typing import List, Set, Tuple



def process_snapshot(snapshot: KappaSnapshot) -> List[dict]:
    # Extract the relevant information from a snapshot: size, abundance, & compositions
    data = []
    for kappa_complex, abundance in snapshot.get_all_complexes_and_abundances():
        size = kappa_complex.get_size_of_complex()
        composition = kappa_complex.get_complex_composition()
        data.append({'size': size, 'count': abundance, 'mass': size * abundance, 'composition': composition})
    return data


def colorize_agents(agents: Set[str]) -> dict:
    # Generate & associate colors as a dictionary {Agent: Color}
    agent_list = list(agents)
    num_agents = len(agent_list)
    agent_colors = {}
    # Use built-in palettes: for 10 or less use the default colors
    if num_agents <= len(mpl.rcParams['axes.prop_cycle']):
        for agent in range(num_agents):
            agent_colors[agent_list[agent]] = 'C' + str(agent)
    # For 20 or more agents, use the tab20 colormap
    elif num_agents <= 20:
        colormap = plt.get_cmap('tab20')
        for agent in range(num_agents):
            agent_colors[agent_list[agent]] = colormap(agent)
    # For more than 20, pick linearly spaced values on HSV space
    else:
        h = numpy.linspace(start=0, stop=1, num=num_agents, endpoint=False)
        for agent in range(num_agents):
            agent_colors[agent_list[agent]] = colorsys.hsv_to_rgb(h[agent], 0.7, 0.75)
    return agent_colors
    # ToDo use colormath spaces to get better distinguishable colors; e.g. in LuvColor space


def snapshot_composition_simple(data: List[dict], color_scheme: dict, vis_mode: str, x_res: float, y_res: float) -> Tuple[List[matplotlib.patches.Rectangle], int]:
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
        s = matplotlib.patches.Rectangle(xy=(species_canvas['x'], species_canvas['y']),
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
            r = matplotlib.patches.Rectangle(xy=(agent_rectangle['x'],agent_rectangle['y']),
                                             width=agent_rectangle['dx'],
                                             height=agent_rectangle['dy'],
                                             facecolor=color_scheme[agent_type[a]])
            agent_patches.append(r)

    # Add the rectangles to the figure
    patch_list = agent_patches + species_patches

    return patch_list, max_value


def snapshot_legend_simple(color_scheme: dict, col_num: int) -> Tuple[list, list]:
    # Add agent entries with their colors (as composition key)
    position = 0 #var to track indexing
    x_dim = 0.5 #size of rectangle serving as color key
    y_dim = 0.5
    rect_list = []
    text_list = []
    for agent, color in sorted(color_scheme.items(), key=itemgetter(0), reverse=False):
        y_pos, x_pos = divmod(position, col_num)
        legend_entry_rect = matplotlib.patches.Rectangle(xy=(x_pos, -y_pos), width=x_dim, height=y_dim, edgecolor='#000000', fc=color)
        legend_entry_text = matplotlib.text.Text(x=x_pos + x_dim, y=-y_pos, text=agent, verticalalignment='baseline')
        rect_list.append(legend_entry_rect)
        text_list.append(legend_entry_text)
        position += 1

    return rect_list, text_list


def snapshot_legend_maxima(vis_mode: str, max_mass: int, max_size: int, max_count: int) -> List[matplotlib.text.Text]:
    if vis_mode == 'all':
        # Add entries for maxima at the top
        max_mass_text = matplotlib.text.Text(x=0, y=4, text='Max mass: ' + str(max_mass), verticalalignment='top')
        max_size_text = matplotlib.text.Text(x=0, y=3, text='Max size: ' + str(max_size), verticalalignment='top')
        max_count_text = matplotlib.text.Text(x=0, y=2, text='Max count: ' + str(max_count), verticalalignment='top')
        text_list = [max_mass_text, max_size_text, max_count_text]
    else:
        text_list = matplotlib.text.Text(x=0, y=2, text='Max ' + vis_mode + ': ' + str(max_mass), verticalalignment='top')
    return text_list


def snapshot_legend_maximum(max_data: int, vis_mode: str) -> matplotlib.text.Text:
    #Same as snapshot_legend_maxima, but for a single maximum
    max_text = matplotlib.text.Text(x=0, y=2, text='Max ' + vis_mode + ': ' + str(max_data), verticalalignment='top')
    return max_text


def render_snapshot(snapshot_file: str, color_scheme: dict = None, vis_mode: str ='all') -> plt.figure:
    # Process the snapshot
    my_snapshot = KappaSnapshot(snapshot_file)
    my_data = process_snapshot(my_snapshot)
    assert len(my_data) > 0, 'Problem: empty snapshot <<' + snapshot_file + '>>'

    # Determine coloring scheme, unless provided
    if color_scheme:
        my_color_scheme = color_scheme
    else:
        agent_list = my_snapshot.get_agent_types_present()
        if len(agent_list) > 20:
            print('Over 20 agents found: color palette might be ugly. Try googling <<iwanthue>> for a tool to generate optimally distinct colors.')
        my_color_scheme = colorize_agents(agent_list)

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
        rectangles_mass, my_max_mass = snapshot_composition_simple(data=my_data, color_scheme=my_color_scheme, vis_mode='mass', x_res=res_w, y_res=res_h)
        rectangles_size, my_max_size = snapshot_composition_simple(data=my_data, color_scheme=my_color_scheme, vis_mode='size', x_res=res_w, y_res=res_h)
        rectangles_count, my_max_count = snapshot_composition_simple(data=my_data, color_scheme=my_color_scheme, vis_mode='count', x_res=res_w, y_res=res_h)
        ax_mass.add_collection(PatchCollection(rectangles_mass, match_original=True))
        ax_size.add_collection(PatchCollection(rectangles_size, match_original=True))
        ax_count.add_collection(PatchCollection(rectangles_count, match_original=True))

        # Add title onto axes, hide the ticks, re-center the bounding box
        ax_mass.set_title('Area proportional to mass of species')
        ax_size.set_title('Area proportional to size of species')
        ax_count.set_title('Area proportional to count of species')
        ax_mass.axis('off')
        ax_size.axis('off')
        ax_count.axis('off')
        ax_mass.axis('tight')
        ax_size.axis('tight')
        ax_count.axis('tight')

        #Define maxima; proxy for scale bar
        maxima_texts = snapshot_legend_maxima(vis_mode=vis_mode, max_mass=my_max_mass, max_count=my_max_count, max_size=my_max_size)
        legend_top_edge = 4
        for text in maxima_texts:
            ax_legend.add_artist(text)

    else:
        ax_data = figure.add_subplot(121, aspect=1)
        ax_legend = figure.add_subplot(122, aspect=1)
        plt.title(s='Area proportional to ' + vis_mode + ' of species')
        rectangles_data, my_max_data = snapshot_composition_simple(data=my_data, color_scheme=my_color_scheme, vis_mode=vis_mode, x_res=res_w, y_res=res_h)
        ax_data.add_collection(PatchCollection(rectangles_data, match_original=True))
        ax_data.axis('off')
        ax_data.axis('tight')

        #Define maximum; proxy for scale bar
        maxima_text = snapshot_legend_maximum(vis_mode=vis_mode, max_data=my_max_data)
        legend_top_edge = 2
        ax_legend.add_artist(maxima_text)

    # Add the legend
    columns = 5  #number of columns in legend
    legend_squares, legend_texts = snapshot_legend_simple(color_scheme=my_color_scheme, col_num=columns)
    ax_legend.add_collection(PatchCollection(legend_squares, match_original=True))
    for text in legend_texts:
        ax_legend.add_artist(text)

    ax_legend.set_xlim(left=0, right=columns)
    ax_legend.set_ylim(top=legend_top_edge, bottom=-divmod(len(my_color_scheme), columns)[0] - 1)
    ax_legend.axis('off')
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