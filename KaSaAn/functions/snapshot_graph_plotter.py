#! /usr/bin/env python3

import ast
import networkx as nx
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from typing import List, Tuple
from KaSaAn.core import KappaSnapshot, KappaAgent
from KaSaAn.functions.snapshot_patchwork_visualizer import colorize_agents


def render_snapshot_as_plain_graph(snapshot: KappaSnapshot, highlight_patterns: List[KappaAgent],
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
            color_list.append(color_scheme[KappaAgent(agent_name)])
        except KeyError as k_e:
            raise ValueError('Complex contains agent <' + str(agent_name) + '> not found in supplied palette.') from k_e
    # construct plot for all agents
    fig, ax = plt.subplots(figsize=fig_size)
    nx.draw(snapshot_graph, pos=node_positions, ax=ax, node_color=color_list, with_labels=False,
            node_size=node_size, width=edge_width)
    plt.axis('off')
    # create legend list
    legend_entries = [mpatches.Patch(label=agent.get_agent_name() + ': ' + str(snapshot_agents[agent_name]),
                                     color=color_scheme[agent])
                      for agent in snapshot_agents]
    ax.legend(handles=legend_entries, ncol=4, loc='upper right',
              title=str(vip_complex.get_size_of_complex()) + ' agents')
    fig_list.append((fig, 'all'))
    # generate n+1 plots, one per agent plus one for all agents

    for agent_of_interest in coloring_scheme.keys():
        # create local coloring list and labeling dictionary for nodes, based on agent name
        color_list = []
        for node in lc_graph.nodes.data():
            node_agent = node[1]['kappa']
            agent_name = node_agent.get_agent_name()
            if node_agent.get_agent_name() == agent_of_interest.get_agent_name():
                color_list.append(coloring_scheme[KappaAgent(agent_name)])
            else:
                color_list.append('#00000000')
        # construct plot(s)
        fig, ax = plt.subplots(figsize=[10, 10])
        nx.draw_networkx_nodes(lc_graph, pos=node_positions, ax=ax, labels=label_dict, node_color=color_list,
                               with_labels=label_toggle, node_size=node_size)
        nx.draw_networkx_edges(lc_graph, pos=node_positions, ax=ax, node_size=node_size,
                               width=edge_width, edge_color='k', alpha=0.1)
        plt.axis('off')
        # create legend list
        legend_entries = [mpatches.Patch(label=agent_name + ': ' + str(compo[KappaAgent(agent_name)]),
                                         color=coloring_scheme[KappaAgent(agent_name)])
                          for agent_name in set(label_dict.values())]
        ax.legend(handles=legend_entries, ncol=4, loc='upper right',
                  title=str(vip_complex.get_size_of_complex()) + ' agents')
        fig_list.append((fig, agent_of_interest.get_agent_name()))
    return fig
