#! /usr/bin/env python3

import glob
import warnings
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


def observable_multi_data_axis_annotator(co_plot_axis, file_data_list: List[Tuple[List[str], np.array, str]],
                                         coplot_index: int, coplot_name: str, diff_toggle: bool):
    """Co-plot the same variable from a list of files."""
    legend_entries = []
    for file_data in file_data_list:
        legend_data, numeric_data, file_name = file_data
        # find indexes to plot:
        if coplot_index:
            var_index = coplot_index - 1
        elif coplot_name:
            try:
                var_index = legend_data.index(coplot_name)
            except ValueError as ve:
                raise ValueError('Requested variable name not found in variable list; available options are:\n' +
                                 ' | '.join(legend_data)) from ve
        else:
             raise ValueError('Function requires a variable index, or a name.')
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
        co_plot_axis.plot(data_x, data_y, label=legend_entry, drawstyle=plot_drawstyle)
    co_plot_axis.set_xlabel('Time')
    if diff_toggle:
        co_plot_axis.set_ylabel(r'$\frac{\Delta \mathrm{x}}{\Delta t}$', rotation='horizontal')
    else:
        co_plot_axis.set_ylabel('Value')
    if len(set(legend_entries)) == 1:
        co_plot_axis.set_title(legend_entries[0])
    else:
        co_plot_axis.legend()
    return co_plot_axis


def observable_coplot_axis_annotator(target_axis, file_pattern: str, variable_index: int, variable_name: str,
                                     differential_toggle: bool):
    file_names = find_data_files(file_pattern)
    file_data_list = []
    for file_name in file_names:
        legend_data, numeric_data = observable_file_reader(file_name)
        if numeric_data.shape[0] <= 1:
            warnings.warn('Only one time point in file ' + file_name)
        file_data_list.append((legend_data, numeric_data, file_name))
    if not variable_index and not variable_name:
        raise ValueError('Function requires the index of a variable, or a name for it.')
    observable_multi_data_axis_annotator(co_plot_axis=target_axis, file_data_list=file_data_list,
                                         coplot_index=variable_index, coplot_name=variable_name,
                                         diff_toggle=differential_toggle)
    return target_axis
