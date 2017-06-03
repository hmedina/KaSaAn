#! /usr/bin/python3
from kappa_snapshot_analysis import KappaSnapshot
import glob
import csv
import argparse


def snapshot_analyzer(base_directory, snap_prefix, verbosity):
    snap_names = glob.glob(base_directory + snap_prefix + 'snap*.ka')
    snap_num = len(snap_names)
    if verbosity:
        print("Found " + str(snap_num) + " snapshots in directory " + base_directory + ' with prefix <' + snap_prefix + '> .')

    assert snap_num >= 2, "Error: less than 2 snapshots were found."

    cum_dist = {}
    for snap_name in snap_names:
        dist = KappaSnapshot(snap_name).get_size_distribution()
        for key in dist.keys():
            if key in cum_dist:
                cum_dist[key] += dist[key]
            else:
                cum_dist[key] = dist[key]

    with open(base_directory + snap_prefix + 'distribution_cumulative.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Size', 'Cumulative Abundance'])
        for key, value in cum_dist.items():
            writer.writerow([key, value])

    if verbosity:
        print("Cumulative distribution written to file.")


    with open(base_directory + snap_prefix + 'distribution_mean.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Size', 'Mean Abundance'])
        for key, value in cum_dist.items():
            writer.writerow([key, value/snap_num])

    if verbosity:
        print("Mean distribution written to file.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Get cumulative and mean abundance of complexes based on snapshots sharing a common prefix,'
                    ' like "t_one_snap_7.ka" having the prefix "t_one_". Snapshots must contain the word "snap" and end'
                    ' in ".ka". Two files will be produced in the same directory as the snapshots are. They will be'
                    ' prefixed accordingly: [prefix]distribution_cumulative.csv and [prefix]distribution_mean.csv')
    parser.add_argument('-p', '--prefix', type=str, default='',
                        help='Prefix identifying snapshots to analyze, precedes the string "snap"; e.g. "foo_" is the'
                             ' prefix for "foo_snap_76.ka".')
    parser.add_argument('-d', '--working_directory', type=str, default='/.',
                        help='The directory where snapshots are held, and where distribution files will be saved to.')
    parser.add_argument('-v', '--verbosity', action='store_true',
                        help='Print extra information, like number of snapshots found, directory understood, and'
                             ' file names used for output.')
    args = parser.parse_args()

    snapshot_analyzer(base_directory=args.working_directory, snap_prefix=args.prefix, verbosity=args.verbosity)
