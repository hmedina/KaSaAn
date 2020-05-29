#!/usr/bin/env python3

from typing import List, Tuple
import csv
import numpy as np


def observable_file_reader(file_name: str = 'data.csv') -> Tuple[list, np.ndarray]:
    """Function parses a kappa output file, e.g. <data.csv>, and returns the legend and numeric data."""
    # read the header, skipping UUID and command recipe, extract legend entries
    with open(file_name, 'r', newline='') as csv_file:
        legend_reader = csv.reader(csv_file, dialect='excel')
        _ = next(legend_reader)         # recipe line
        _ = next(legend_reader)         # UUID line
        leg_data = next(legend_reader)  # legend line
    num_data = np.loadtxt(file_name, delimiter=',', skiprows=3)
    leg_data = [entry.replace("'", "").replace('"', '') for entry in leg_data]
    return leg_data, num_data


def observable_list_axis_annotator(obs_axis, data: Tuple[list, np.ndarray], vars_to_plot: List[int],
                                   diff_toggle: bool):
    """Function plots a parsed kappa output file, e.g. <data.csv>, and returns a matplotlib figure object."""
    leg_data, num_data = data
    # determine what observables to plot
    # by default, plot all observables except the first, which plots [T]
    if not vars_to_plot:
        vars_to_plot = range(2, len(leg_data) + 1)
    for var in vars_to_plot:
        if var not in range(1, len(leg_data) + 1):
            raise ValueError('Variable <' + str(var) + '> not in observables present: 1-' + str(len(leg_data)))
    # determine the type of plot
    x_data = num_data[:, 0]
    if diff_toggle:
        d_t = np.diff(x_data)
        x_data = x_data[1:]
        if np.any(d_t == 0.0):
            raise ValueError('Time difference of zero found in input data.')
    # plot
    for variable in vars_to_plot:
        y_data = num_data[:, variable - 1]
        if diff_toggle:
            d_v = np.diff(y_data)
            y_data = d_v / d_t
        if len(x_data) < 1000:
            plot_drawstyle = 'steps-post'
        else:
            plot_drawstyle = 'default'
        obs_axis.plot(x_data, y_data, label=leg_data[variable - 1], drawstyle=plot_drawstyle)
    obs_axis.legend()
    obs_axis.set_xlabel('Time')
    if diff_toggle:
        obs_axis.set_ylabel(r'$\frac{\Delta \mathrm{x}}{\Delta t}$', rotation='horizontal')
    else:
        obs_axis.set_ylabel('Value')
    return obs_axis
