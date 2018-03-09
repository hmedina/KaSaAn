#! /usr/bin/python3

import glob
import re
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import PatchCollection
from snapshot_visualizer import process_snapshot, snapshot_composition_simple, colorize_agents, snapshot_legend_simple
from kappa4_snapshot_analysis import KappaSnapshot


# ToDo make this a function!

# Helper function to sort file names
def numerical_sort(value):
    parts = re.compile(r'(\d+)').split(value)
    parts[1::2] = map(int, parts[1::2])

    return parts


# Get & sort the file names
def find_snapshot_files(base_dir='./'):
    snap_names = sorted(glob.glob(base_dir + 'snapshot.*.ka'), key=numerical_sort)
    snapshot_list = []
    for file_name in snap_names:
        snapshot_list.append(KappaSnapshot(file_name))

    return snapshot_list


# Define consistent coloring scheme & maximum mass
def define_agent_list_and_max_mass(snap_list):
    max_mass = 0
    agent_set = set()
    for snap in snap_list:
        agent_set.update(snap.get_agent_types_present())
        if max_mass < snap.get_total_mass():
            max_mass = snap.get_total_mass()

    return list(agent_set), max_mass




# Figure size & target resolution of mass
my_snapshot_directory = './models/trace_vis/'
my_snapshots = find_snapshot_files(my_snapshot_directory)
print('Found ' + str(len(my_snapshots)) + ' snapshots in ' + my_snapshot_directory)

my_agent_list, my_max_mass = define_agent_list_and_max_mass(my_snapshots)
print('Found ' + str(len(my_agent_list)) + ' agents.')

my_color_scheme = colorize_agents(my_agent_list)

my_vis_mode = 'mass'
data_XY_ratio = 1
my_x_res = 1000
my_y_res = my_x_res * data_XY_ratio

fig_width = 16 #width of figure, in inches
my_fig = plt.figure(figsize=[fig_width, fig_width/2])
data_ax = my_fig.add_subplot(121, aspect=1)
lgnd_ax = my_fig.add_subplot(122, aspect=1)

# Define the animation, i.e. the left axis
artist_list = []
for my_snap in my_snapshots:
    ars = []
    snap_scale = my_snap.get_total_mass() / my_max_mass
    my_data = process_snapshot(my_snap)
    rectangles, maxi = snapshot_composition_simple(data=my_data, color_scheme=my_color_scheme, vis_mode=my_vis_mode,
                                                   x_res=my_x_res * snap_scale, y_res=my_y_res * snap_scale)
    for r in rectangles:
        ar = data_ax.add_patch(r)
        ars.append(ar)
    ars.append(data_ax.text(0, my_y_res,
                            'Time ' + str(my_snap.get_snapshot_time()) + ' ; final time ' + str(my_snapshots[-1].get_snapshot_time()),
                            horizontalalignment='left', verticalalignment='bottom'))
    ars.append(data_ax.text(my_x_res, my_y_res, 'Mass present ' + str(my_snap.get_total_mass()),
                            horizontalalignment='right', verticalalignment='bottom'))
    artist_list.append(ars)


data_ax.set_xlim(left=0, right=my_x_res)
data_ax.set_ylim(bottom=0, top=my_y_res)
data_ax.axis('off')

# Define the legend, i.e. the right axis
columns = 2
legend_squares, legend_texts = snapshot_legend_simple(color_scheme=my_color_scheme, col_num=columns)
lgnd_ax.add_collection(PatchCollection(legend_squares, match_original=True))
for text in legend_texts:
    lgnd_ax.add_artist(text)

lgnd_ax.set_xlim(left=0, right=columns)
lgnd_ax.set_ylim(top=1, bottom=-divmod(len(my_color_scheme), columns)[0] - 1)
lgnd_ax.axis('off')

# Make movie out of list
ani = animation.ArtistAnimation(fig=my_fig, artists=artist_list, interval=500, repeat_delay=1000)

#ani.save('prozone.mp4')
plt.show()