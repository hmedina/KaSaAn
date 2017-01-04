#! python.exe
import re
import os


def complex_sizes(kappa_file):
    # First read the file and get, for each line (i.e. one complex per line), the length & abundance
    with open(kappa_file, 'r') as kf:
        raw_complex_size = []
        raw_complex_num = []
        for line in kf:
            if (line[0] != '#') & (line != '\n'):
                raw_complex_size.append(line.count('('))
                raw_complex_num.append(int(re.search('%init:\s(\d+)\s', line).group(1)))
    # Make sure we have both length & abundance of each complex
    assert len(raw_complex_size) == len(raw_complex_num)

    # Expand the list by repeating the size of the complex, the number of times it appears in the mix
    # (i.e. if a dimer appears three times, the list will contain at least the number 2 in triplicate)
    c_sizes = []
    for i, x in enumerate(raw_complex_num):
        c_sizes += [raw_complex_size[i] for _ in range(x)]

    c_sizes.sort()
    return c_sizes


def get_sorted_snapshots(folder, prefix):
    # Problem: snap1, snap10, snap2, snap3 ... are in order lexically, but not by event. Ergo, I must parse the
    #  directory. I need the list of event numbers at at which the snapshot were taken. I can then reconstruct the
    # filename from that number and return a sorted list.
    snapshot_indexes = []
    for f in os.listdir(folder):
        m = re.search('(?<=' + prefix + ')(\d+).ka', f)
        if m:
            snapshot_indexes.append(int(m.group(1)))

    # Sort the indexes, rendered numerically above, to get the snapshots in the right order
    snapshot_indexes.sort()

    # Now reconstruct the name of the snapshot, including the folder
    sorted_snapshots = []
    for i in snapshot_indexes:
        sorted_snapshots.append(folder + '/' + prefix + str(i) + '.ka')

    return sorted_snapshots, snapshot_indexes


def time_series_distribution(sorted_snapshots):
    # Parse the snapshots, to get their data.
    snap_distributions = []
    for snap in sorted_snapshots:
        snap_distributions.append(complex_sizes(snap))

    # Make sure we have an entry for every snapshot
    assert len(sorted_snapshots) == len(snap_distributions)

    return snap_distributions
