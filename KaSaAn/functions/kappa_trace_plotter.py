#!/usr/bin/env python3

from typing import List, Tuple
import numpy as np
import matplotlib.pyplot as plt


def kappa_trace_reader(file_name: str = 'data.csv') -> Tuple[list, np.ndarray]:
    """Function parses a kappa output file, e.g. <data.csv>, and returns the legend and numeric data."""
    leg_data = np.loadtxt(file_name, delimiter=',', skiprows=2, max_rows=1, dtype=str)
    num_data = np.loadtxt(file_name, delimiter=',', skiprows=3)
    leg_data = [entry.replace("'", "").replace('"', '') for entry in leg_data]
    return leg_data, num_data


def kappa_trace_figure_maker(data: Tuple[list, np.ndarray], vars_to_plot: List[int]) -> plt.figure:
    """Function plots a parsed kappa output file, e.g. <data.csv>, and returns a matplotlib figure object."""
    leg_data, num_data = data
    # determine what observables to plot
    if not vars_to_plot:
        vars_to_plot = range(1, len(leg_data) + 1)
    for var in vars_to_plot:
        if not var in range(1, len(leg_data) + 1):
            raise ValueError('Variable <' + str(var) + '> not in observables present: 1-' + str(len(leg_data)))
    # determine the type of plot
    fig, ax = plt.subplots()
    x_data = num_data[:, 0]
    if len(x_data) < 1000:
        plot_drawstyle = 'steps-post'
    else:
        plot_drawstyle = 'default'
    # plot
    for variable in vars_to_plot:
        ax.plot(x_data, num_data[:, variable - 1], label=leg_data[variable - 1], drawstyle=plot_drawstyle)
    ax.legend()
    ax.set_xlabel('Time')
    return fig
