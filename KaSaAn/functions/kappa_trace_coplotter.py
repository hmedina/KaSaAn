#! /usr/bin/env python3

import glob
import warnings
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple
from .kappa_trace_plotter import kappa_trace_reader
from .numerical_sort import numerical_sort


def find_data_files(pattern: str) -> List[str]:
    """Find files that match the pattern."""
    file_list = glob.glob(pattern)
    if not file_list:
        raise ValueError('No files found matching: ' + str(pattern))
    sorted_file_list = sorted(file_list, key=numerical_sort)
    return sorted_file_list


def get_xy_legend_data_from_file(variable: int, file_name: str) -> Tuple[np.array, np.array, str]:
    """Extract time and value data for a specific observable from a standard Kappa time-trace file."""
    legend_data, numeric_data = kappa_trace_reader(file_name)
    if numeric_data.shape[0] <= 1:
        warnings.warn('Only one time point in file ' + str(file_name))
    time_series = numeric_data[:, 0]
    var_val_series = numeric_data[:, variable]
    legend_name = legend_data[variable]
    return time_series, var_val_series, legend_name


def co_plot_variable_from_file_list(data_files: List[str], var_to_coplot: int, diff_toggle: bool):
    """Co-plot the same variable from a list of files."""
    var_index = var_to_coplot - 1
    co_plot_fig, ax = plt.subplots()
    legend_entries = []
    for rep_file in data_files:
        data_x, data_y, legend_entry = get_xy_legend_data_from_file(var_index, rep_file)
        if diff_toggle:
            d_t = np.diff(data_x)
            d_v = np.diff(data_y)
            if np.any(d_t == 0.0):
                raise ValueError('Time difference of zero found in file ' + rep_file)
            data_y = d_v / d_t
            data_x = data_x[1:]
        legend_entries.append(legend_entry)
        if len(data_x) < 1000:
            plot_drawstyle = 'steps-post'
        else:
            plot_drawstyle = 'default'
        ax.plot(data_x, data_y, label=legend_entry, drawstyle=plot_drawstyle)
    ax.set_xlabel('Time')
    if diff_toggle:
        ax.set_ylabel(r'$\frac{\Delta \mathrm{x}}{\Delta t}$')
    else:
        ax.set_ylabel('Value')
    if len(set(legend_entries)) == 1:
        ax.set_title(legend_entries[0])
    else:
        ax.legend()
    return co_plot_fig


def kappa_trace_coplotter(file_pattern: str, plot_variable: int, differential_toggle: bool):
    file_names = find_data_files(file_pattern)
    fig = co_plot_variable_from_file_list(file_names, plot_variable, differential_toggle)
    return fig
