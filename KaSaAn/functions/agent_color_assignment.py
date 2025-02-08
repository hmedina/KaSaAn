#!/usr/bin/env python3

import colorsys
import numpy
import warnings
import matplotlib as mpl
import matplotlib.colors
import matplotlib.pyplot
from typing import Any, Dict, Set, Union

from KaSaAn.core import KappaAgent, KappaComplex


def colorize_observables(object_set: Set[Union[KappaAgent, KappaComplex]]) -> Dict[Union[KappaAgent, KappaComplex], Any]:
    """Generate & associate colors; supports KappaAgent or KappaComplex as keys in the dictionary."""
    num_agents = len(object_set)
    object_colors = {}
    # Use built-in palettes: for 10 or less use the default colors
    if num_agents <= len(mpl.rcParams['axes.prop_cycle']):
        for i, this_object in enumerate(object_set):
            object_colors[this_object] = matplotlib.colors.to_rgba('C' + str(i))
    # For 20 or more agents, use the tab20 colormap
    elif num_agents <= 20:
        colormap = matplotlib.pyplot.get_cmap('tab20')
        for i, this_object in enumerate(object_set):
            object_colors[this_object] = colormap(i)
    # For more than 20, pick linearly spaced values on HSV space
    else:
        h = numpy.linspace(start=0, stop=1, num=num_agents, endpoint=False)
        for i, this_object in enumerate(object_set):
            object_colors[this_object] = colorsys.hsv_to_rgb(h[i], 0.7, 0.75)
    return object_colors


def sanity_check_agent_colors(agents_found: Set[KappaAgent], color_scheme: Dict[KappaAgent, Any]):
    """
    Sanity check a user-provided color-scheme when operating with KappaAgents.
    This function operates under a sum-formula assumption, so overspecification by including an agent signature must be
    guarded against. Additionally, agents requested in the scheme but not found in the kappa object, or vice versa, 
    throw a warning."""
    if color_scheme.keys() != agents_found:
        for agent in color_scheme:
            if len(agent.get_agent_signature()) > 0:
                raise ValueError('Agent <' + str(agent) +
                                 '> in provided coloring scheme is overspecified: remove the ports or counters.')
            if agent not in agents_found:
                warnings.warn(
                    'Agent <' + agent.get_agent_name() +
                    '> requested in the coloring scheme was not found in kappa object>.')
        for agent in agents_found:
            if agent not in color_scheme:
                warnings.warn(
                    'Agent <' + agent.get_agent_name() +
                    '> present in the kappa object has no color assigned in the coloring scheme provided.')
