#!/usr/bin/env python3

import matplotlib as mpl
import matplotlib.figure as mpf
import matplotlib.pyplot as plt
import matplotlib.patches as mpp
import matplotlib.text
import squarify
import warnings
from matplotlib.collections import PatchCollection
from operator import itemgetter
from typing import List, Dict, Tuple, Any

from KaSaAn.core import KappaSnapshot, KappaAgent
from KaSaAn.functions import sanity_check_agent_colors, colorize_observables


def process_snapshot(snapshot: KappaSnapshot) -> List[dict]:
    """Extract relevant information from a snapshot: size, abundance, & compositions"""
    data = []
    for kappa_complex, abundance in snapshot.get_all_complexes_and_abundances():
        size = kappa_complex.get_size_of_complex()
        composition = kappa_complex.get_complex_composition()
        data.append({'size': size, 'count': abundance, 'mass': size * abundance, 'composition': composition})
    if len(data) < 1:
        warnings.warn('Empty snapshot <<' + str(snapshot) + '>>')
    return data


def snapshot_composition_simple(data: List[dict], color_scheme: Dict[KappaAgent, Any], vis_mode: str,
                                x_res: float, y_res: float) -> Tuple[List[mpp.Rectangle], int]:
    """Assemble a list of rectangles for MatPlotLib to plot, plus the size of the largest of these (for mass
     normalization in trace movie making)."""
    if vis_mode != 'size' and vis_mode != 'count' and vis_mode != 'mass':
        warnings.warn('Unknown mode <<' + vis_mode + '>>')
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
        s = mpp.Rectangle(xy=(species_canvas['x'], species_canvas['y']),
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
            r = mpp.Rectangle(xy=(agent_rectangle['x'], agent_rectangle['y']),
                              width=agent_rectangle['dx'],
                              height=agent_rectangle['dy'],
                              facecolor=color_scheme[agent_type[a]])
            agent_patches.append(r)

    # Add the rectangles to the figure
    patch_list = agent_patches + species_patches

    return patch_list, max_value


def snapshot_legend_simple(color_scheme: Dict[KappaAgent, Any], col_num: int) ->\
        Tuple[List[mpp.Rectangle], List[matplotlib.text.Text]]:
    """Create legend components; their entries with appropriate colors (as composition key);
     companion to snapshot_composition_simple."""
    position = 0    # var to track indexing
    x_dim = 0.5     # size of rectangle serving as color key
    y_dim = 0.5
    rect_list = []
    text_list = []
    for agent, color in sorted(color_scheme.items(), key=itemgetter(0), reverse=False):
        y_pos, x_pos = divmod(position, col_num)
        legend_entry_rect = mpp.Rectangle(
            xy=(x_pos, -y_pos), width=x_dim, height=y_dim, edgecolor='#000000', fc=color)
        legend_entry_text = matplotlib.text.Text(
            x=x_pos + x_dim, y=-y_pos, text=agent.get_agent_name(), verticalalignment='baseline')
        rect_list.append(legend_entry_rect)
        text_list.append(legend_entry_text)
        position += 1
    return rect_list, text_list


def _snapshot_legend_maxima(vis_mode: str, max_mass: int, max_size: int, max_count: int) -> List[matplotlib.text.Text]:
    """Define the maxima to put on the legend based on visualization mode."""
    if vis_mode == 'all':
        # Add entries for maxima at the top
        max_mass_text = matplotlib.text.Text(x=0, y=4, text='Max mass: ' + str(max_mass), verticalalignment='top')
        max_size_text = matplotlib.text.Text(x=0, y=3, text='Max size: ' + str(max_size), verticalalignment='top')
        max_count_text = matplotlib.text.Text(x=0, y=2, text='Max count: ' + str(max_count), verticalalignment='top')
        text_list = [max_mass_text, max_size_text, max_count_text]
    else:
        text_list = matplotlib.text.Text(x=0, y=2, text='Max ' + vis_mode + ': ' + str(max_mass),
                                         verticalalignment='top')
    return text_list


def _snapshot_legend_maximum(max_data: int, vis_mode: str) -> matplotlib.text.Text:
    """Same as snapshot_legend_maxima, but for a single maximum."""
    max_text = matplotlib.text.Text(x=0, y=2, text='Max ' + vis_mode + ': ' + str(max_data), verticalalignment='top')
    return max_text


def render_snapshot_as_patchwork(snapshot_file: str, color_scheme: Dict[KappaAgent, Any] = None, vis_mode: str = 'all',
                                 fig_size: Tuple[float, float] = mpl.rcParams['figure.figsize'],
                                 fig_res: float = mpl.rcParams['figure.dpi']) -> mpf.Figure:
    """Render a snapshot as a patchwork / tree-map diagram, using any of four supported modes:

    * `count`: a complex' area is proportional to how many times it appears
    * `size`: a complex' area is proportional to how big it is
    * `mass`: a complex' area is proportional to how much mass it has, the product of its count times its mass
    * `all`: plot all three side by side

    See file under `KaSaAn.scripts` for further usage."""
    # Process the snapshot
    my_snapshot = KappaSnapshot(snapshot_file)
    my_data = process_snapshot(my_snapshot)
    if len(my_data) < 1:
        warnings.warn('Empty snapshot <<' + snapshot_file + '>>')
    # sanity check color scheme, or create one
    if color_scheme:
        sanity_check_agent_colors(agents_found=my_snapshot.get_agent_types_present(), color_scheme=color_scheme)
        my_color_scheme = color_scheme
    else:
        agent_set = my_snapshot.get_agent_types_present()
        if len(agent_set) > 20:
            print('Over 20 agents found: palette might be ugly.\n'
                  'Try googling <<iwanthue>> for a tool to generate distinct colors,\n'
                  'then provide a custom palette to this tool.')
        my_color_scheme = colorize_observables(agent_set)

    # Define figure definition & resolution
    res_w = fig_res * fig_size[0]
    res_h = fig_res * fig_size[1]
    figure = plt.figure(figsize=fig_size, layout='constrained')

    # If visualizing all, then we need three subplots (for mass, size, count), plus the area for the legend
    if vis_mode == 'all':
        # Define all three axes
        ax_mass = figure.add_subplot(221, aspect=1)
        ax_size = figure.add_subplot(222, aspect=1)
        ax_count = figure.add_subplot(223, aspect=1)
        ax_legend = figure.add_subplot(224)
        # Draw data onto axes
        rectangles_mass, my_max_mass = snapshot_composition_simple(
            data=my_data, color_scheme=my_color_scheme, vis_mode='mass', x_res=res_w, y_res=res_h)
        rectangles_size, my_max_size = snapshot_composition_simple(
            data=my_data, color_scheme=my_color_scheme, vis_mode='size', x_res=res_w, y_res=res_h)
        rectangles_count, my_max_count = snapshot_composition_simple(
            data=my_data, color_scheme=my_color_scheme, vis_mode='count', x_res=res_w, y_res=res_h)
        ax_mass.add_collection(PatchCollection(rectangles_mass, match_original=True))
        ax_size.add_collection(PatchCollection(rectangles_size, match_original=True))
        ax_count.add_collection(PatchCollection(rectangles_count, match_original=True))

        # Add title onto axes, hide the ticks, re-center the bounding box
        ax_mass.set_title('Mass')
        ax_size.set_title('Size')
        ax_count.set_title('Count')
        ax_mass.axis('off')
        ax_size.axis('off')
        ax_count.axis('off')
        ax_mass.axis('tight')
        ax_size.axis('tight')
        ax_count.axis('tight')

        # Define maxima; proxy for scale bar
        maxima_texts = _snapshot_legend_maxima(
            vis_mode=vis_mode, max_mass=my_max_mass, max_count=my_max_count, max_size=my_max_size)
        legend_top_edge = 4
        for text in maxima_texts:
            ax_legend.add_artist(text)

    else:
        ax_data = figure.add_subplot(121, aspect=1)
        ax_legend = figure.add_subplot(122, aspect=1)
        plt.title(label='Area proportional to ' + vis_mode + ' of species')
        rectangles_data, my_max_data = snapshot_composition_simple(
            data=my_data, color_scheme=my_color_scheme, vis_mode=vis_mode, x_res=res_w, y_res=res_h)
        ax_data.add_collection(PatchCollection(rectangles_data, match_original=True))
        ax_data.axis('off')
        ax_data.axis('tight')

        # Define maximum; proxy for scale bar
        maxima_text = _snapshot_legend_maximum(vis_mode=vis_mode, max_data=my_max_data)
        legend_top_edge = 2
        ax_legend.add_artist(maxima_text)

    # Add the legend
    columns = 5     # number of columns in legend
    legend_squares, legend_texts = snapshot_legend_simple(color_scheme=my_color_scheme, col_num=columns)
    ax_legend.add_collection(PatchCollection(legend_squares, match_original=True))
    for text in legend_texts:
        ax_legend.add_artist(text)

    ax_legend.set_xlim(left=0, right=columns)
    ax_legend.set_ylim(top=legend_top_edge, bottom=-divmod(len(my_color_scheme), columns)[0] - 1)
    ax_legend.axis('off')
    return figure
