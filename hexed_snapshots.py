#! /usr/bin/env python3

from KaSaAn.core import KappaSnapshot
from typing import List, Optional, Tuple
import copy
import matplotlib.axes as mpax
import matplotlib.colors as mpco
import matplotlib.patches as mppa
import matplotlib.pyplot as plt
import numpy as np

# inspiration: 10.1109/ACCESS.2019.2944766 figure 4.C

# hexed_snapshot
# main figure is a grid of hexes
# hexes can be groupped by 7s into larger canvases, or remain alonge for a 1-hex canvas
# complexes of smallest sizes get a 1-hex canvas, while largest get a 7^n sized canvas

test_snap = KappaSnapshot('models/alphabet_soup_snap.ka')

# determine canvas size histogram: how many 7^0, how many 7^1, etc?

# satisfy:
#  figure is n*(x*n) in size, yielding that many hexes
# first guess!
#  assign 7^y hexes to each complex; minimize "wasted" area, using histogram difference?
#  for each, subtract 7^y hexes from figure's number of hexes?
#  n >= y_max
# layout?
#  place biggest in center, then... next biggest next to it?
#  direction? flip direction if above canvas top?

def this_ys_error(size_weights, size_list: List[int]) -> float:
    """Roon-mean-square deviation-like error calculation.
    Remember ^ is a shifting operation, not a power operation."""
    err = 0
    for this_w, this_size in zip(size_weights, size_list, strict=True):
        class_err = (this_size - (7 ** this_w)) ** 2
        err += class_err
    np.sqrt(err / len(size_weights))
    return err

def idealized_weights(size_list: List[int]) -> List[int]:
    """Find an idealized set of weights for the sizes.
    Increase sizes until the error stops decreasing; gradient is implicit:
    Largest complex contributes the most to the error, so in practice we
    start from the largest error contributors and work our way down to the
    smallest complexes."""
    size_list = np.array(size_list)
    sort_indexes = np.argsort(size_list)
    weights = np.repeat(0, len(size_list))     # initialize with all at 7^0=1 hex
    error_so_far = this_ys_error(weights, size_list)
    max_y = int(np.ceil(size_list[sort_indexes[-1]] ** (1/7)))
    for indx in reversed(range(len(size_list))):        # start at biggestmers
        for some_y in range(1, max_y + 1 ):             # add one to include np.ceil result
            new_weights = copy.deepcopy(weights)        # gods damnit Python
            new_weights[sort_indexes[indx]] = some_y    # to keep weights aligned with size_list, index the sorted array
            new_error = this_ys_error(new_weights, size_list)
            # print('{}, {} vs. {}'.format(new_weights, new_error, error_so_far))
            if new_error < error_so_far:
                error_so_far = new_error
                weights = new_weights
            else:
                break
    return weights

my_sizes = test_snap.get_all_sizes()
# print('\n'.join(['w:{}\ts:{}'.format(item[0], item[1]) for item in zip(idealized_weights(my_sizes), my_sizes)]))
i_weights = idealized_weights(my_sizes)

sum([7**pow for pow in i_weights])

# define lowest-level grid, y=0
# all subsequent grids derived from inmediate lower-level grid

# fit maxi-size class in their top-most grid
# accept or reject?
#  reject -> increase canvas size somehow
#  accept -> go to next size class
#   for each n-th class in their n-th grid:
#       find empty space, try to fit ??
# let's leave automated layout for a different time


class hex():
    """Hexagonal member of lattice.
    * Flat-top configuration for top size class
    * Smaller class hexes remain centered with their containing super-hex
    * Each layer subdivision rotates the lattice; this way of hexagonal subdivision minimizes 'wasted' visual space between hexagons of different sizes
    * Top layer has circumscribed circle of radius 1; hexagon's corners lie on the unit circle"""
    x: float
    """Ordinate of the hex's center."""
    y: float
    """Coordinate of the hex's center."""
    size_class: int
    """The size class this hex belongs to; biggest layer is 0, smaller layers are -1, -2, etc."""
    half_height: float
    """Half-height of the hexagon. I.e. radius of inscribed circle."""
    half_width: float
    """Half-width of the hexagon. I.e. radius of the circumscribed circle."""

    sublayer_rotation: float = np.arcsin(2 / np.sqrt(28) * np.sin(5/6 * np.pi))
    """Rotation each sublayer gets to fit in parent.

    Derived from the triangle that connects:
    * A: parent-hex center
    * B: child-hex center
    * C: closes corner of parent-hex

    Its measurements are:
    * AB length: 2 half-heights of child-hex
    * AC length: half-width of parent-hex
    * BC length: half-height of child-hex
    * ABC angle: is 2/3 Pi + 1/6 Pi
    
    Using the sine law, distances cancel out, yielding scale-independent angle."""

    def __init__(self, x: float, y:float, size_class: int):
        if size_class > 0:
            raise ValueError("Layer can not be greater than 0, got {}".format(size_class))
        # basic hexagon dimensions
        if size_class == 0:
            half_height = np.sqrt(3) / 2
            half_width = 1
        else:
            parent_hex = hex(0, 0, size_class + 1)                      # obtained from the right-triangle that connects parent's C0 | H1's C0, C3, and child-hex H6's C0
            half_height = np.sqrt(3/28 * (parent_hex.half_width)**2)    # C0-C3 = 2 parent half-widths, C3-H6C0 = 5 child half-widths, H1C0-H6c0 = 2 child half-heights,
            half_width = half_height * 2 / np.sqrt(3)                   # and a half-width = 2/sqrt(3) * half-height
        self.x = x
        self.y = y
        self.size_class = size_class
        self.half_height = half_height
        self.half_width = half_width
        
    def corners(self) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        """Returns the (x0..x5) (y0..y5) coordinates for the 6 corners of this hexagon. These points lie on the circumscribed circle."""
        agg = []
        for ix in range(6):
            x_raw, y_raw = [self.half_width, 0]
            theta = (ix * np.pi / 3) + ((np.pi / 6 + self.sublayer_rotation) * abs(self.size_class))
            x_rot = x_raw * np.cos(theta) - y_raw * np.sin(theta)
            y_rot = x_raw * np.sin(theta) + y_raw * np.cos(theta)
            x = x_rot + self.x
            y = y_rot + self.y
            agg.append((x, y))
        return tuple(agg)
    
    def midpoints(self) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        """Returns the (x0..x5) (y0..y5) coordinates of 6 points, each centered on an edge. These points lie on the incsribed circle."""
        agg = []
        p0, p1, p2, p3, p4, p5 = self.corners()
        sides = [p0, p1, p2, p3, p4, p5, p0]
        for ix in range(len(sides) - 1):
            x = (sides[ix][0] + sides[ix + 1][0]) / 2
            y = (sides[ix][1] + sides[ix + 1][1]) / 2
            agg.append((x, y))
        return tuple(agg)

    def draw(self, ax: mpax.Axes, facecolor = None, edgecolor = None):
        """Draw onto a target axis"""
        ax.add_patch(mppa.Polygon(self.corners(), closed=True, fc=facecolor, ec=edgecolor))

    def subdivide(self) -> Tuple[hex, hex, hex, hex, hex, hex, hex]:
        """Subdivide this hex into its 7 constituing subhexes."""
        sub_size = self.size_class - 1
        sh_center = hex(x=self.x, y=self.y, size_class=sub_size)
        neighbor_hexes = []
        for x_mid, y_mid in sh_center.midpoints():
            x = (x_mid - self.x) + x_mid
            y = (y_mid - self.y) + y_mid
            neighbor_hexes.append(hex(x=x, y=y, size_class=sub_size))
        return sh_center, *neighbor_hexes


fig, ax = plt.subplots(1, 1, layout='constrained', figsize=[10, 10])

hexus_maximus = hex(0, 0, 0)
hexus_maximus.draw(ax, facecolor='white', edgecolor='black')

hex_a0, hex_a1, hex_a2, hex_a3, hex_a4, hex_a5, hex_a6 = hexus_maximus.subdivide()

hex_a0.draw(ax, facecolor='white', edgecolor='black')

for some_1 in hex_a1.subdivide():
    some_1.draw(ax, facecolor='white', edgecolor='black')

for some_1 in hex_a2.subdivide():
    for some_2 in some_1.subdivide():
        some_2.draw(ax, facecolor='white', edgecolor='black')

for some_1 in hex_a3.subdivide():
    for some_2 in some_1.subdivide():
        for some_3 in some_2.subdivide():
            some_3.draw(ax, facecolor='white', edgecolor='black')

for some_1 in hex_a4.subdivide():
    for some_2 in some_1.subdivide():
        for some_3 in some_2.subdivide():
            for some_4 in some_3.subdivide():
                some_4.draw(ax, facecolor='white', edgecolor='black')

for some_1 in hex_a5.subdivide():
    for some_2 in some_1.subdivide():
        for some_3 in some_2.subdivide():
            for some_4 in some_3.subdivide():
                for some_5 in some_4.subdivide():
                    some_5.draw(ax, facecolor='white', edgecolor='black')


ax.set_aspect('equal', 'box')
ax.autoscale_view()
fig.savefig('/mnt/c/Users/megap/Desktop/hex_subdivision.pdf')
# plt.show()

