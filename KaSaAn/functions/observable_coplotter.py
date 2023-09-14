#! /usr/bin/env python3

import ast
import glob
import warnings
import matplotlib.axes as mpa
import numpy as np
from typing import List, Tuple
from .observable_plotter import observable_file_reader
from .numerical_sort import numerical_sort


def _find_data_files(pattern: str) -> List[str]:
    """Find files that match the pattern."""
    file_list = glob.glob(pattern)
    if not file_list:
        raise ValueError('No files found matching: ' + str(pattern))
    sorted_file_list = sorted(file_list, key=numerical_sort)
    return sorted_file_list


def _multi_data_axis_annotator(co_plot_axis: mpa.Axes, file_data_list: List[Tuple[List[str], np.array, str]],
                               coplot_index: int, coplot_name: str, coplot_expression: str,
                               diff_toggle: bool = False, log_x: bool = False, log_y: bool = False,
                               omit_legend: bool = False) -> mpa.Axes:
    """Annotate the provided axis."""
    artist_list = []
    # Define things to plot
    for file_data in file_data_list:
        legend_data, numeric_data, file_name = file_data
        if coplot_index:
            var_index = coplot_index - 1
            data_y = numeric_data[:, var_index]
            legend_label = legend_data[var_index]
        elif coplot_name:
            try:
                var_index = legend_data.index(coplot_name)
            except ValueError as ve:
                raise ValueError('Requested variable name not found in variable list; available options are:\n' +
                                 ' | '.join(legend_data)) from ve
            data_y = numeric_data[:, var_index]
            legend_label = file_name
        elif coplot_expression:
            # to render an algebraic expression, we create an abstract syntax tree,
            #  then replace the tokens that are strings found in the legend with
            #  the name of the data array, with proper indexing; finally
            #  the new tree can be executed (with fixed linenos & indents).
            # TokenTransformer is declared here so it can include in its scope
            #  the legend_data values; this avoids more extensive subclassing
            class TokenTransformer(ast.NodeTransformer):
                """Swap column names for the indexed-array."""
                def visit_Constant(self, node, obs_list=legend_data):
                    """Transform node if it's a string found in the legend data."""
                    if isinstance(node.value, str):
                        if node.value in obs_list:
                            return ast.copy_location(
                                ast.Subscript(
                                    value=ast.Name(id='numeric_data', ctx=ast.Load()),
                                    slice=ast.Tuple(elts=[ast.Slice(), ast.Constant(value=obs_list.index(node.value))],
                                                    ctx=ast.Load()),
                                    ctx=ast.Load()), node)
                        else:
                            raise ValueError('Error: <{}> not found in observables: {}'.format(node.value, obs_list))
                    else:
                        return node
            my_ast = ast.parse(coplot_expression, mode='eval')
            TokenTransformer().visit(my_ast)
            data_y = eval(compile(ast.fix_missing_locations(my_ast), '<string>', 'eval'))
            legend_label = file_name
        else:
            raise ValueError('Function requires a variable index, a variable name, or an expression of variables.')
        # an entry was defined; now to process it if differential was requested
        data_x = numeric_data[:, 0]
        if diff_toggle:
            d_t = np.diff(data_x)
            d_v = np.diff(data_y)
            if np.any(d_t == 0.0):
                raise ValueError('Time difference of zero found in file ' + file_name)
            data_y = d_v / d_t
            data_x = data_x[1:]
        # finally, plot the entry
        plot_draw_style = 'steps-post' if len(data_x) < 1000 else 'default'
        artist_list.extend(co_plot_axis.plot(data_x, data_y, label=legend_label, drawstyle=plot_draw_style))
    co_plot_axis.set_xlabel('Time')
    # if plotting a time differential, adjust Y-axis label
    if diff_toggle:
        co_plot_axis.set_ylabel(r'$\frac{\Delta \mathrm{x}}{\Delta t}$', rotation='horizontal')
    else:
        co_plot_axis.set_ylabel('Value')
    # if requested index yielded one observable name (all tracks of same observable),
    # use the file-names for annotating the legend, and the observable name as a plot title;
    # else use the variable names that resulted from the requested index plus their file-name
    if coplot_index:
        legend_strings: List[str] = [artist.get_label() for artist in artist_list]
        if len(set(legend_strings)) == 1:
            co_plot_axis.set_title(legend_strings[0])
            for ix, artist in enumerate(artist_list):
                artist.set_label(file_data_list[ix][2])
        else:
            for ix, artist in enumerate(artist_list):
                artist.set_label('{} in {}'.format(artist.get_label(), file_data_list[ix][2]))
    elif coplot_name:
        co_plot_axis.set_title(coplot_name)
    elif coplot_expression:
        co_plot_axis.set_title(coplot_expression)
    if not omit_legend:
        co_plot_axis.legend()
    # adjust plot scales
    if log_x:
        co_plot_axis.set_xscale('log')
    if log_y:
        co_plot_axis.set_yscale('log')
    return co_plot_axis


def observable_coplot_axis_annotator(target_axis: mpa.Axes, file_pattern: str,
                                     variable_index: int, variable_name: str, variable_expr: str,
                                     differential_toggle: bool = False,
                                     log_axis_x: bool = False, log_axis_y: bool = False,
                                     no_legend: bool = False) -> mpa.Axes:
    """See file under `KaSaAn.scripts` for usage."""
    file_names = _find_data_files(file_pattern)
    file_data_list = []
    for file_name in file_names:
        legend_data, numeric_data = observable_file_reader(file_name)
        if numeric_data.shape[0] <= 1:
            warnings.warn('Only one time point in file ' + file_name)
        file_data_list.append((legend_data, numeric_data, file_name))
    if not variable_index and not variable_name and not variable_expr:
        raise ValueError('Function requires the index of a variable,'
                         ' a name for one, or an expression of variables found in the observable file.')
    _multi_data_axis_annotator(co_plot_axis=target_axis, file_data_list=file_data_list,
                               coplot_index=variable_index, coplot_name=variable_name, coplot_expression=variable_expr,
                               diff_toggle=differential_toggle, log_x=log_axis_x, log_y=log_axis_y,
                               omit_legend=no_legend)
    return target_axis
