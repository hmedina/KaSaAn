#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
from KaSaAn.functions import kappa_trace_reader, kappa_trace_figure_maker


def main():
    parser = argparse.ArgumentParser(description='Plot a trace file produced by KaSim.')
    parser.add_argument('-i', '--input_file_name', type=str, default='data.csv',
                        help='Name of the file with the time series traces to be plotted. By default it will look for <data.csv>')
    parser.add_argument('-o', '--output_file_name', type=str, default=None,
                        help='Name of the file to where the figure should be saved; displayed if not specified.')
    parser.add_argument('-p', '--print_observables_to_file', type=str, default='',
                        help="If specified, dump the list of observables to a file, one per line, so that the line number corresponds to the observable's index.")
    parser.add_argument('-v', '--variables_to_plot', type=int, default=None, nargs='*',
                        help='The list of variable / observable indexes that should be plotted. If not specified, all will be plotted against time. Observables are plotted in order, with the top-most legend entry corresponding to number 1.')
    args = parser.parse_args()

    # parse data
    this_data = kappa_trace_reader(args.input_file_name)
    indexes_to_plot = args.variables_to_plot
    this_figure = kappa_trace_figure_maker(data=this_data, vars_to_plot=indexes_to_plot)

    # print out observables
    if args.print_observables_to_file:
        with open(args.print_observables_to_file, 'w') as file:
            for obs in this_data[0]:
                file.write(obs + '\n')

    # save or display the figure
    if args.output_file_name:
        this_figure.savefig(fname=args.output_file_name)
    else:
        plt.show()


if __name__ == '__main__':
    main()
