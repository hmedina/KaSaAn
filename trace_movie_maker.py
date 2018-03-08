#! /usr/bin/python3

import glob
import re
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from snapshot_visualizer import process_snapshot, snapshot_composition_simple, colorize_agents
from kappa4_snapshot_analysis import KappaSnapshot


# ToDo make this a function!
# Helper function to sort file names
numbers = re.compile(r'(\d+)')
def numerical_sort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


# Get & sort the file names
snapshot_directory = './models/trace_vis/'
snap_names = sorted(glob.glob(snapshot_directory + 'snapshot.*.ka'), key=numerical_sort)
print('Found ' + str(len(snap_names)) + ' snapshots in ' + snapshot_directory)
snapshot_list = []
for file_name in snap_names:
    snapshot_list.append(KappaSnapshot(file_name))


# Define consistent coloring scheme & maximum mass
max_mass = 0
agent_set = set()
for snap in snapshot_list:
    agent_set.update(snap.get_agent_types_present())
    if max_mass < snap.get_total_mass():
        max_mass = snap.get_total_mass()

my_color_scheme = colorize_agents(list(agent_set))


# Figure size & target resolution of mass
my_vis_mode = 'mass'
my_x_res = 1200
my_y_res = 800

fig, ax = plt.subplots()

artist_list = []
for snap in snapshot_list:
    ars = []
    snap_scale = snap.get_total_mass() / max_mass
    my_data = process_snapshot(snap)
    rectangles, maxi = snapshot_composition_simple(data=my_data, color_scheme=my_color_scheme, vis_mode=my_vis_mode,
                                                   x_res=my_x_res * snap_scale, y_res=my_y_res * snap_scale)
    for r in rectangles:
        ar = ax.add_patch(r)
        ars.append(ar)
    ars.append(ax.text(0, my_y_res, 'Time ' + str(snap.get_snapshot_time()) + ' ; final time ' + str(snapshot_list[-1].get_snapshot_time()),
                       horizontalalignment='left', verticalalignment='bottom'))
    ars.append(ax.text(my_x_res, my_y_res, 'Mass present ' + str(snap.get_total_mass()),
                       horizontalalignment='right', verticalalignment='bottom'))
    artist_list.append(ars)


ax.set_xlim(left=0, right=my_x_res)
ax.set_ylim(bottom=0, top=my_y_res)
ax.axis('off')


# Make movie out of list
ani = animation.ArtistAnimation(fig=fig, artists=artist_list, interval=500, repeat_delay=1000)

#ani.save('prozone.mp4')
plt.show()