#! /usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
from KaSaAn.functions import kappa_trace_coplotter


def main():
    """Co-plot the same variable from multiple files, save as file or display the figure."""
    parser = argparse.ArgumentParser(description='Co-plot the same variable form multiple files, save as file or display'
                                                 'the figure.')
    parser.add_argument('-p', '--pattern', type=str, required=True,
                        help='Pattern, passed to glob.glob that would match the desired files to co-plot, should'
                             ' probably be quoted.')
    parser.add_argument('-v', '--variable', type=int, required=True,
                        help='Variable to be co-plotted. Index is the order of declaration (i.e. var #1 plot is'
                             ' observable #1), or column as printed in the out_file.csv from KaSim (i.e. var #1 plots'
                             ' column #1).')
    parser.add_argument('-o', '--out_file', type=str, default='',
                        help='Name of the file where the figure should be saved. If left blank or omitted, the figure'
                             ' will be shown instead.')
    args = parser.parse_args()
    fig = kappa_trace_coplotter(args.pattern, args.variable)
    if args.out_file:
        fig.savefig(args.out_file)
    else:
        plt.show()

        
if __name__ == '__main__':
    main()
