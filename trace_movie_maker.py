#! /usr/bin/python3

import glob
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from snapshot_visualizer import process_snapshot, snapshot_composition_simple
from kappa4_snapshot_analysis import KappaSnapshot



# Get the list of file names
snapshot_directory = './models/trace_vis/'
snap_names = glob.glob(snapshot_directory + 'snapshot.*.ka')
# ToDo sort properly the snapshot names
print('Found ' + str(len(snap_names)) + ' snapshots in ' + snapshot_directory)

# Define consistent coloring scheme
my_color_scheme = {'X': 'C0', 'Y': 'C1'}
# ToDo auto-define a color scheme
my_vis_mode = 'mass'
my_x_res = 1200
my_y_res = 800

fig, ax = plt.subplots()

artist_list = []
for file_name in snap_names:
    ars = []
    my_snapshot = KappaSnapshot(file_name)
    my_data = process_snapshot(my_snapshot)
    rectangles, maxi = snapshot_composition_simple(data=my_data, color_scheme=my_color_scheme,
                                                   vis_mode=my_vis_mode, x_res=my_x_res, y_res=my_y_res)
    for r in rectangles:
        ar = ax.add_patch(r)
        ars.append(ar)

    artist_list.append(ars)
    print('Finished processing ' + file_name)

ax.set_xlim(left=0, right=my_x_res)
ax.set_ylim(bottom=0, top=my_y_res)
# ToDo hide the axes & ticks

# Make movie out of list
ani = animation.ArtistAnimation(fig=fig, artists=artist_list)

# ani.save('dynamic_images.mp4')
plt.show()