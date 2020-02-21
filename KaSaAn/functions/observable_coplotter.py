#! /usr/bin/env python3

import glob
import warnings
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple
from .observable_plotter import observable_file_reader
from .numerical_sort import numerical_sort


def find_data_files(pattern: str) -> List[str]:
    """Find files that match the pattern."""
    file_list = glob.glob(pattern)
    if not file_list:
        raise ValueError('No files found matching: ' + str(pattern))
    sorted_file_list = sorted(file_list, key=numerical_sort)
    return sorted_file_list


def observable_multi_data_figure_maker(file_data_list: List[Tuple[List[str], np.array, str]], var_to_coplot: int, diff_toggle: bool):
    """Co-plot the same variable from a list of files."""
    var_index = var_to_coplot - 1
    co_plot_fig, ax = plt.subplots()
    legend_entries = []
    for file_data in file_data_list:
        legend_data, numeric_data, file_name = file_data
        data_x = numeric_data[:, 0]
        data_y = numeric_data[:, var_index]
        legend_entry = legend_data[var_index]
        if diff_toggle:
            d_t = np.diff(data_x)
            d_v = np.diff(data_y)
            if np.any(d_t == 0.0):
                raise ValueError('Time difference of zero found in file ' + file_name)
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
        ax.set_ylabel(r'$\frac{\Delta \mathrm{x}}{\Delta t}$', rotation='horizontal')
    else:
        ax.set_ylabel('Value')
    if len(set(legend_entries)) == 1:
        ax.set_title(legend_entries[0])
    else:
        ax.legend()
    return co_plot_fig


def observable_coplot_figure_maker(file_pattern: str, plot_variable: int, differential_toggle: bool):
    file_names = find_data_files(file_pattern)
    file_data_list = []
    for file_name in file_names:
        legend_data, numeric_data = observable_file_reader(file_name)
        if numeric_data.shape[0] <= 1:
            warnings.warn('Only one time point in file ' + file_name)
        file_data_list.append((legend_data, numeric_data, file_name))
    fig = observable_multi_data_figure_maker(file_data_list, plot_variable, differential_toggle)
    return fig
