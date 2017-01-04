#! python.exe
from kappa_snapshot_analysis import time_series_distribution as tsd
from kappa_snapshot_analysis import get_sorted_snapshots as gss
import matplotlib.pyplot as plt
import statistics

#TODO Make a kappa simulation where the degree of connectedness / degeneracy of cycle increases with time (rate?)

#TODO run 1000 KaSim repetitions, output the snapshot to directories, grouped by TIME

#TODO Go to each directory (i.e. time point), get the dir contents & parse those sapshots & get their stats

#TODO Iterate over the different time points (i.e. folders) to get a trend


# Acquire data of times series distribution
my_snaps, snap_indexes = gss('snapshots', 'val2-tri_')
my_dist = tsd(my_snaps)

# Get mean & standard deviation of samples
my_means = []
my_stdev = []
my_gc_fraction = []
for x in my_dist:
    my_means.append(statistics.mean(x))
    my_stdev.append(statistics.stdev(x))
    my_gc_fraction.append(max(x) / sum(x))

# Plot!
fig, axes = plt.subplots(nrows=1, ncols=2)
axes[0].errorbar(snap_indexes, my_means, yerr=my_stdev)
axes[0].set_xlabel('Event number')
axes[0].set_ylabel('Mean complex size with standard deviation')
axes[0].set_title('Evolution of complex size distribution')

axes[1].plot(snap_indexes, my_gc_fraction)
axes[1].set_xlabel('Event number')
axes[1].set_ylabel('Reaction mixture fraction taken up by the giant component')
axes[1].set_title('Growth of the giant component')

plt.show()
