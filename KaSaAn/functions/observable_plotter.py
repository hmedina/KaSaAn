#!/usr/bin/env python3

from typing import List, Tuple
import ast
import csv
import matplotlib.axes as mpa
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


def observable_list_axis_annotator(obs_axis: mpa.Axes, data: Tuple[list, np.ndarray],
                                   vars_indexes: List[int], vars_names: List[str], vars_exprs: List[str],
                                   axis_x_log: bool = False, axis_y_log: bool = False,
                                   diff_toggle: bool = False) -> mpa.Axes:
    """Function plots a parsed kappa output file, e.g. <data.csv>, and returns a matplotlib figure object. See file
     under `KaSaAn.scripts` for further usage."""
    leg_data, num_data = data
    data_to_plot = []
    legend_to_plot = []
    # determine what observables to plot
    # by default, plot all observables except the first, which plots [T]
    if not vars_exprs and not vars_indexes and not vars_names:
        vars_to_plot = range(2, len(leg_data) + 1)
    else:
        vars_to_plot = []
        # plot by index
        if vars_indexes:
            for var in vars_indexes:
                if var not in range(1, len(leg_data) + 1):
                    raise ValueError('Variable {} not in observables; valid range is [1;{}]'.format(var, len(leg_data)))
                vars_to_plot.append(var)
        # plot by variable name
        if vars_names:
            for var_name in vars_names:
                if var_name not in leg_data:
                    raise ValueError('{} not found in observables; entries are:\n{}'.format(var_name,
                                                                                            ', '.join(leg_data)))
                vars_to_plot.append(leg_data.index(var_name) + 1)
        # plot by algebraic expression
        if vars_exprs:
            for alg_expression in vars_exprs:
                # to render an algebraic expression, we create an abstract syntax tree,
                #  then replace the tokens that are strings found in the legend with
                #  the name of the data array, with proper indexing; finally
                #  the new tree can be executed (with fixed linenos & indents).
                # TokenTransformer is declared here so it can include in its scope
                #  the legend_data values; this avoids more extensive subclassing
                class TokenTransformer(ast.NodeTransformer):
                    """Swap column names for the indexed-array."""
                    def visit_Constant(self, node, obs_list=leg_data):
                        """Transform node if it's a string found in the legend data."""
                        if isinstance(node.value, str):
                            if node.value in obs_list:
                                return ast.copy_location(
                                    ast.Subscript(
                                        value=ast.Name(id='num_data', ctx=ast.Load()),
                                        slice=ast.Tuple(elts=[
                                                              ast.Slice(),
                                                              ast.Constant(value=obs_list.index(node.value))],
                                                        ctx=ast.Load()),
                                        ctx=ast.Load()), node)
                            else:
                                raise ValueError('<{}> not found in observables: {}'.format(node.value, obs_list))
                        else:
                            return node
                my_ast = ast.parse(alg_expression, mode='eval')
                TokenTransformer().visit(my_ast)
                data_to_plot.append(eval(compile(ast.fix_missing_locations(my_ast), '<string>', 'eval')))
                legend_to_plot.append(alg_expression)
    for variable in vars_to_plot:
        data_to_plot.append(num_data[:, variable - 1])
        legend_to_plot.append(leg_data[variable - 1])
    # determine the type of plot
    x_data = num_data[:, 0]
    if diff_toggle:
        d_t = np.diff(x_data)
        x_data = x_data[1:]
        if np.any(d_t == 0.0):
            raise ValueError('Time difference of zero found in input data.')
    # plot
    for ix, this_var in enumerate(legend_to_plot):
        y_data = data_to_plot[ix]
        if diff_toggle:
            d_v = np.diff(y_data)
            y_data = d_v / d_t
        if len(x_data) < 1000:
            plot_drawstyle = 'steps-post'
        else:
            plot_drawstyle = 'default'
        obs_axis.plot(x_data, y_data, label=this_var, drawstyle=plot_drawstyle)
    obs_axis.legend()
    obs_axis.set_xlabel('Time')
    # adjust label if plotting a differential
    if diff_toggle:
        obs_axis.set_ylabel(r'$\frac{\Delta \mathrm{x}}{\Delta t}$', rotation='horizontal')
    else:
        obs_axis.set_ylabel('Value')
    # adjust axes scales
    if axis_x_log:
        obs_axis.set_xscale('log')
    if axis_y_log:
        obs_axis.set_yscale('log')
    return obs_axis
