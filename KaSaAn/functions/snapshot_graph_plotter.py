#! /usr/bin/env python3

import ast
import networkx as nx
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from typing import List, Tuple
from KaSaAn.core import KappaSnapshot, KappaAgent
from KaSaAn.functions.snapshot_patchwork_visualizer import colorize_agents


def render_snapshot_as_plain_graph(snapshot: KappaSnapshot, highlight_patterns: List[str],
                                   color_scheme_file_name: str, node_size: int, edge_width: float,
                                   fig_size: Tuple[float, float]) -> plt.figure:
    """"Take a KappaSnapshot and render it as a plain graph, optionally highlighting certain patterns."""
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
    else:
        color_scheme = colorize_agents(snapshot_agents)
    # construct color list object
    color_list = []
    for node in snapshot_graph.nodes.data():  # create coloring list for nodes, based on agent name
        agent_name = node[1]['kappa'].get_agent_name()
        try:
            if highlight_patterns:
                any_pattern_in_agent = sum([KappaAgent(item) in node[1]['kappa'] for item in highlight_patterns])
                if any_pattern_in_agent:
                    color_list.append(color_scheme[KappaAgent(agent_name)])
                else:
                    color_list.append('#00000000')
            else:
                color_list.append(color_scheme[KappaAgent(agent_name)])
        except KeyError as k_e:
            raise ValueError('Complex contains agent <' + str(agent_name) + '> not found in supplied palette.') from k_e
    # construct plot for all agents
    fig, ax = plt.subplots(figsize=fig_size)
    nx.draw(snapshot_graph, pos=node_positions, ax=ax, node_color=color_list, with_labels=False,
            node_size=node_size, width=edge_width)
    plt.axis('off')
    # create legend list
    legend_entries = []
    for agent in snapshot_agents:
        patch_label = agent.get_agent_name() + ': ' + str(snapshot_composition[agent])
        any_pattern_match = sum([agent in KappaAgent(item) for item in highlight_patterns])
        if any_pattern_match:
            patch_color = color_scheme[agent]
        else:
            patch_color = '#00000000'
        legend_entries.append(mpatches.Patch(label=patch_label, color=patch_color))
    ax.legend(handles=legend_entries, ncol=4, loc='upper right',
              title=str(snapshot.get_total_mass()) + ' agents')
    return fig
