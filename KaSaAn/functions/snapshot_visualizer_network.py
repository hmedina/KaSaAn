#! /usr/bin/env python3

import ast
import networkx as nx
import matplotlib.figure as mpf
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from typing import List, Tuple
from ..core import KappaSnapshot, KappaAgent
from .agent_color_assignment import colorize_observables, sanity_check_agent_colors


def render_snapshot_as_plain_graph(snapshot_file_name: str, highlight_patterns: List[str],
                                   color_scheme_file_name: str, node_size: int, edge_width: float,
                                   fig_size: Tuple[float, float]) -> List[mpf.Figure]:
    """Take a KappaSnapshot and render it as a plain graph, optionally highlighting certain patterns.
    See file under `KaSaAn.scripts` for usage."""
    snapshot = KappaSnapshot(snapshot_file_name)
    snapshot_agents = snapshot.get_agent_types_present()
    snapshot_composition = snapshot.get_composition()
    snapshot_graph = snapshot.to_networkx()
    node_positions = graphviz_layout(snapshot_graph, prog="sfdp")
    # for user-defined coloring schemes, read the dictionary from a file, convert keys to KappaAgent
    if color_scheme_file_name:
        color_scheme = {}
        with open(color_scheme_file_name, 'r') as cs_file:
            coloring_scheme_raw = ast.literal_eval(cs_file.read())
            for key, value in coloring_scheme_raw.items():
                color_scheme[KappaAgent(key)] = value
        sanity_check_agent_colors(snapshot_agents, color_scheme)
    else:
        color_scheme = colorize_observables(snapshot_agents)
    # start assembling the list of figures
    fig_list = []
    # 1: construct the all-agent figure
    color_list_all = []
    for node in snapshot_graph.nodes.data():
        agent_name = node[1]['kappa'].get_agent_name()
        try:
            color_list_all.append(color_scheme[KappaAgent(agent_name)])
        except KeyError as k_e:
            raise ValueError('Complex contains agent <' + agent_name + '> not found in coloring palette.') from k_e
    fig_all, ax_all = plt.subplots(figsize=fig_size)
    nx.draw(snapshot_graph, pos=node_positions, ax=ax_all, node_color=color_list_all, with_labels=False,
            node_size=node_size, width=edge_width)
    plt.axis('off')
    legend_entries = []
    for agent in snapshot_agents:
        patch_label = agent.get_agent_name() + ': ' + str(snapshot_composition[agent])
        patch_color = color_scheme[agent]
        legend_entries.append(mpatches.Patch(label=patch_label, color=patch_color))
    ax_all.legend(handles=legend_entries, ncol=4, loc='upper right',
                  title=str(snapshot.get_total_mass()) + ' agents')
    fig_list.append(fig_all)
    # 2: iterate over patterns, producing a figure for each
    if highlight_patterns:
        for string_pattern in highlight_patterns:
            kappa_query = KappaAgent(string_pattern)
            query_agent_name = kappa_query.get_agent_name()
            color_list_patt = []    # a list of colors for the nodes
            match_number = 0        # snapshot.get_abundance_of_agent() would also work, but this avoids extra recursion
            for node in snapshot_graph.nodes.data():  # create coloring list for nodes, based on agent's name
                node_agent = node[1]['kappa']
                try:
                    if kappa_query in node_agent:
                        color_list_patt.append(color_scheme[KappaAgent(query_agent_name)])
                        match_number += 1
                    else:
                        color_list_patt.append('#00000000')
                except KeyError as k_e:
                    raise ValueError('Complex contains agent <' + node_agent.get_agent_name() +
                                     '> not found in supplied palette.') from k_e
            fig_patt, ax_patt = plt.subplots(figsize=fig_size)
            nx.draw(snapshot_graph, pos=node_positions, ax=ax_patt, node_color=color_list_patt, with_labels=False,
                    node_size=node_size, width=edge_width)
            plt.axis('off')
            patch_label = str(kappa_query) + ' : ' + str(match_number) + ' matches'
            patch_color = color_scheme[KappaAgent(query_agent_name)]
            legend_entry = mpatches.Patch(label=patch_label, color=patch_color)
            ax_patt.legend(handles=[legend_entry], loc='upper right')
            fig_list.append(fig_patt)
    return fig_list
