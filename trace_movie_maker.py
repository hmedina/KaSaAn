#! /usr/bin/python3

import glob
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches
from snapshot_visualizer import process_snapshot, snapshot_composition_simple
from kappa4_snapshot_analysis import KappaSnapshot



# Get the list of file names
snapshot_directory = './models/trace_vis/'
snap_names = glob.glob(snapshot_directory + 'snapshot.*.ka')
print('Found ' + str(len(snap_names)) + ' snapshots in ' + snapshot_directory)

# Define consistent coloring scheme
my_color_scheme = {'X': 'C0', 'Y': 'C1'}
my_vis_mode = 'mass'
my_x_res = 1200
my_y_res = 800

def my_init_func():
    r = matplotlib.patches.Rectangle(xy=[0, 0], width=my_x_res, height=my_y_res)
    return [r]

def my_frme_func(file_name):
    my_snapshot = KappaSnapshot(file_name)
    my_data = process_snapshot(my_snapshot)
    artist_iterable, maxi = snapshot_composition_simple(data=my_data, color_scheme=my_color_scheme,
                                                        vis_mode=my_vis_mode, x_res=my_x_res, y_res=my_y_res)
    return artist_iterable

# Make movie out of list
fig = plt.figure()
ani = animation.FuncAnimation(fig, func=my_frme_func, frames=snap_names, init_func=my_init_func, interval=50, blit=True, repeat_delay=1000)

# ani.save('dynamic_images.mp4')
plt.show()