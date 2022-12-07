#! /usr/bin/env python3

import ast
import squarify
import warnings
import networkx as nx
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from typing import List, Tuple
from ..core import KappaSnapshot, KappaComplex, KappaAgent
from .agent_color_assignment import colorize_observables


def render_complexes_as_plain_graph(snapshot_file_name: str, sizes_requested: List[int], highlight_patterns: List[str],
                                    color_scheme_file_name: str, node_size: int, edge_width: float,
                                    fig_size: Tuple[float, float], print_distro: bool) -> List[plt.figure]:
    """Take a KappaSnapshot, get complexes of a given size, render them as plain graphs, optionally highlighting
     certain patterns. See file under `KaSaAn.scripts` for usage."""
    snapshot = KappaSnapshot(snapshot_file_name)
    if print_distro:
        print("Snapshot's distribution, size:abundance\n" + str(snapshot.get_size_distribution()))
    snapshot_agents = snapshot.get_agent_types_present()
    # get list of complexes to visualize, with abundances and sizes for weighting
    compl_list: List[KappaComplex] = []
    abund_list: List[int] = []
    sizes_list: List[int] = []
    if sizes_requested:
        # of requested sizes, get present ones; warn user if some requested not present
        sizes_to_view = list(set(snapshot.get_all_sizes()).intersection(sizes_requested))
        sizes_absent = list(set(sizes_requested).difference(set(snapshot.get_all_sizes())))
        if sizes_absent:
            warnings.warn('Requested size(s) <' + str(sizes_absent) + '> not found in size distribution, skipped.')
        if sizes_to_view:
            sizes_to_view.sort(reverse=True)
            for query_size in sizes_to_view:
                comps, abuns = zip(*snapshot.get_complexes_of_size(query_size))
                compl_list.extend(comps)
                abund_list.extend(abuns)
                sizes_list.extend([query_size] * len(abuns))
        else:
            raise ValueError('Snapshot did not contain any of the requested sizes.')
    else:
        compl_list, abund_list = zip(*snapshot.get_largest_complexes())
        sizes_list = [compl_list[0].get_size_of_complex()] * len(compl_list)
    # read or define color scheme
    # for user-defined coloring schemes, read the dictionary from a file, convert keys to KappaAgent
    if color_scheme_file_name:
        color_scheme = {}
        with open(color_scheme_file_name, 'r') as cs_file:
            coloring_scheme_raw = ast.literal_eval(cs_file.read())
            for key, value in coloring_scheme_raw.items():
                color_scheme[KappaAgent(key)] = value
    else:
        color_scheme = colorize_observables(sorted(snapshot_agents))
    # using squarify to define axis locations based on complex sizes
    fig_width = 1
    fig_height = 1
    fig_origin_x = 0
    fig_origin_y = 0
    norm_sizes = squarify.normalize_sizes(sizes_list, fig_width, fig_height)
    axis_rects: List[dict] = squarify.padded_squarify(norm_sizes, fig_origin_x, fig_origin_y, fig_width, fig_height)
    # for each complex, get the networkx graph and define node positions
    compl_graphs = [compl.to_networkx() for compl in compl_list]
    node_positions = [graphviz_layout(compl_graph, prog='sfdp') for compl_graph in compl_graphs]
    plotting_data = list(zip(compl_graphs, compl_list, abund_list, axis_rects, node_positions))
    # figure list construction
    fig_list: List[plt.figure] = []
    # construct the all-agent figure
    fig_all = plt.figure(figsize=fig_size)
    for c_graph, c_kappa, abund, rect, npos in plotting_data:
        ax = fig_all.add_axes([rect['x'], rect['y'], rect['dx'], rect['dy']])
        # try to assign color to nodes based on color scheme
        axis_color_list = []
        for node in c_graph.nodes.data():
            agent_name = node[1]['kappa'].get_agent_name()
            try:
                axis_color_list.append(color_scheme[KappaAgent(agent_name)])
            except KeyError as k_e:
                raise ValueError('Complex contains agent <' + agent_name + '> not found in coloring palette.') from k_e
        nx.draw(c_graph, pos=npos, ax=ax, node_color=axis_color_list, with_labels=False,
                node_size=node_size, width=edge_width)
        # define the axis legend
        legend_entries = []
        for ka_agent, ag_abun in c_kappa.get_complex_composition().items():
            patch_label = '{}: {}'.format(ka_agent, ag_abun)
            patch_color = color_scheme[ka_agent] if ka_agent in color_scheme else '#00000000'
            legend_entries.append(mpatches.Patch(label=patch_label, color=patch_color))
        ax.legend(handles=legend_entries, title=(r'{} {}, size$={}$'.format(abund, 'copies' if abund > 1 else 'copy', c_kappa.get_size_of_complex())))
    fig_list.append(fig_all)
    # construct the patter-specific figures
    if highlight_patterns:
        for string_pattern in highlight_patterns:
            kappa_query = KappaAgent(string_pattern)
            fig_patt = plt.figure(figsize=fig_size)
            for c_graph, c_kappa, abund, rect, npos in plotting_data:
                ax = fig_patt.add_axes([rect['x'], rect['y'], rect['dx'], rect['dy']])
                # try to assign color to nodes based on color scheme and user-supplied pattern
                axis_color_list = []
                for node in c_graph.nodes.data():
                    node_agent = node[1]['kappa']
                    try:
                        if kappa_query in node_agent:
                            axis_color_list.append(color_scheme[KappaAgent(kappa_query.get_agent_name())])
                        else:
                            axis_color_list.append('#00000000')
                    except KeyError as k_e:
                        raise ValueError('Complex contains agent <' + node_agent.get_agent_name() +
                                         '> not found in supplied palette.') from k_e
                nx.draw(c_graph, pos=npos, ax=ax, node_color=axis_color_list, with_labels=False,
                        node_size=node_size, width=edge_width)
                # define the axis legend
                patch_label = '{}: {}'.format(str(kappa_query), c_kappa.get_number_of_embeddings_of_agent(kappa_query))
                patch_color = color_scheme[KappaAgent(kappa_query.get_agent_name())]
                legend_entry = mpatches.Patch(label=patch_label, color=patch_color)
                ax.legend(handles=[legend_entry], title=(r'{} {}, size$={}$'.format(abund, 'copies' if abund > 1 else 'copy', c_kappa.get_size_of_complex())))
            fig_list.append(fig_patt)
    return fig_list
