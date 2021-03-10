#!/usr/bin/env python3
"""Contains `KappaContactMap`, class for representing and fine-tuning the layout of a contact map."""

import colorsys
import random
import re
import matplotlib.path
import matplotlib.patches
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import numpy as np
from typing import List, Dict, Tuple


def _default_site_colors(number_of_sites) -> list:
    """Define a list of colors appropriate to the number of sites being drawn."""
    # Use built-in palettes: for 10 or less use the default colors
    if number_of_sites <= len(mpl.rcParams['axes.prop_cycle']):
        color_set = ['C' + str(i) for i in range(len(mpl.rcParams['axes.prop_cycle']))]
    # For 20 or more agents, use the tab20 colormap
    elif number_of_sites <= 20:
        colormap = plt.get_cmap('tab20')
        color_set = [colormap(i) for i in range(20)]
    # For more than 20, pick linearly spaced values on HSV space
    else:
        hue_samples = np.linspace(start=0, stop=1, num=number_of_sites, endpoint=False)
        color_set = [colorsys.hsv_to_rgb(h, 0.7, 0.75) for h in hue_samples]
    color_list = random.sample(color_set, number_of_sites)
    return color_list


def _file_name_to_string_list(contact_map_file_name: str) -> List[str]:
    """Read an "inputs.ka" style file containing contact map data, process into a clean list of 1-agent strings."""
    with open(contact_map_file_name, 'r') as cmf:
        raw_expression = cmf.read()
    spaced_string = re.sub(r'\s+', ' ', raw_expression)                 # condense spaces
    flat_string = spaced_string.replace(' [', '[')                      # remove whitespace before bracket
    flat_string = flat_string.replace(' {', '{')                        # remove whitespace before curly bracket
    split_string = flat_string.split('%agent: ')[1:]                    # break into list, discard empty first element
    split_string[-1] = split_string[-1].split(')')[0] + ')'
    cleaned_list = [agent_exp.strip() for agent_exp in split_string]    # clean trailing space
    return cleaned_list


def _raw_string_to_agent_sites_bond_types(raw_string: str) -> Tuple[str, dict]:
    """Process the raw string to extract the agent's name, the list of sites, the bond types for each site."""
    raw_expression = raw_string
    kappa_ident = r'([_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
    agent_sign_pat = r'\(([^()]*)\)'
    agent_pat = r'^' + kappa_ident + agent_sign_pat + r'$'
    agent_digest = re.match(agent_pat, raw_expression)
    agent_name = agent_digest.group(1)
    agent_sites = agent_digest.group(2)
    sites_data = {}

    if agent_sites:
        site_expression_list = re.findall(kappa_ident + r'(?:{([^}]+)})?(?:\[([^]]+)\])?', agent_sites)
        for site_expression in site_expression_list:
            site_name, site_internals_expr, site_bonds_expr = site_expression
            site_int_states = site_internals_expr.split()
            site_bnd_states = site_bonds_expr.split()
            sites_data[site_name] = {'int_states': site_int_states, 'bnd_states': site_bnd_states}
    return agent_name, sites_data


def _parsed_kappa_to_default_graphics(parsed_kappa_struct: dict,
                                      wedge_surf_dist=1, wedge_thick_ratio=0.5, grid_spacing=10) -> dict:
    """Initialize agents as a square grid, sites superposed (i.e. default values)."""
    agent_graphics = {}
    grid_base = np.ceil(np.sqrt(len(parsed_kappa_struct.keys())))
    for agent_index, agent_name in enumerate(parsed_kappa_struct.keys()):
        agent_x: int = np.mod(agent_index, grid_base) * grid_spacing           # default values, square grid
        agent_y: int = np.floor_divide(agent_index, grid_base) * grid_spacing
        binding_sites = {}
        flagpole_site_data = {}
        for site_name in parsed_kappa_struct[agent_name].keys():
            if parsed_kappa_struct[agent_name][site_name]['bnd_states']:
                binding_sites[site_name] = {'center': (agent_x, agent_y),
                                            'r': wedge_surf_dist,
                                            'theta1': 0.0, 'theta2': 0.0,       # these will be set later
                                            'width': wedge_thick_ratio * wedge_surf_dist,
                                            'facecolor': '#000000'}
            if parsed_kappa_struct[agent_name][site_name]['int_states']:
                flagpole_site_data[site_name] = parsed_kappa_struct[agent_name][site_name]['int_states']
        flagpole_location = {'center': (agent_x, agent_y),
                             'r': wedge_surf_dist,
                             'theta1': 0.0, 'theta2': 0.0,                      # these will be set later
                             'width': wedge_thick_ratio * wedge_surf_dist,
                             'facecolor': '#444444'}
        agent_graphics[agent_name] = {'loc_x': agent_x, 'loc_y': agent_y,
                                      'bnd_sites': binding_sites, 'flagpole_sites': flagpole_site_data,
                                      'flagpole_loc': flagpole_location}
    return agent_graphics


def _initialize_sites_graphic_structure(graphic_struct: dict, scale_wedges: bool = False) -> dict:
    """Once the data structure has been created, it can now be initialized with plausible values."""
    init_site_graphics = graphic_struct
    for agent_name in init_site_graphics.keys():
        # identify number of wedges to draw
        bind_site_number = len(init_site_graphics[agent_name]['bnd_sites'])
        if init_site_graphics[agent_name]['flagpole_sites']:
            wedge_number = bind_site_number + 2
        else:
            wedge_number = bind_site_number + 1
        wedge_scaling_factor = np.sqrt(wedge_number) if scale_wedges else 1
        wedge_ends = np.rad2deg(np.linspace(0, 2*np.pi, wedge_number))
        # define default color palette based on number of wedges
        site_palette = _default_site_colors(bind_site_number)
        # (re)initialize data, wedges scale in size with the number of wedges to draw
        wedge_center = (graphic_struct[agent_name]['loc_x'], graphic_struct[agent_name]['loc_y'])
        for bind_site_index, bind_site_name in enumerate(init_site_graphics[agent_name]['bnd_sites'].keys()):
            init_site_graphics[agent_name]['bnd_sites'][bind_site_name]['theta1'] = wedge_ends[bind_site_index]
            init_site_graphics[agent_name]['bnd_sites'][bind_site_name]['theta2'] = wedge_ends[bind_site_index+1]
            init_site_graphics[agent_name]['bnd_sites'][bind_site_name]['facecolor'] = site_palette[bind_site_index]
            init_site_graphics[agent_name]['bnd_sites'][bind_site_name]['center'] = wedge_center
            init_site_graphics[agent_name]['bnd_sites'][bind_site_name]['r'] *= wedge_scaling_factor
            init_site_graphics[agent_name]['bnd_sites'][bind_site_name]['width'] *= wedge_scaling_factor
        if init_site_graphics[agent_name]['flagpole_sites']:
            init_site_graphics[agent_name]['flagpole_loc']['theta1'] = wedge_ends[-2]
            init_site_graphics[agent_name]['flagpole_loc']['theta2'] = wedge_ends[-1]
            init_site_graphics[agent_name]['flagpole_loc']['center'] = wedge_center
            init_site_graphics[agent_name]['flagpole_loc']['r'] *= wedge_scaling_factor
            init_site_graphics[agent_name]['flagpole_loc']['width'] *= wedge_scaling_factor
    return init_site_graphics


def _get_bond_types(parsed_kappa_struct: dict) -> dict:
    """Define the agent and site points for later spline drawing."""
    bond_dict = {}
    for agent_a in parsed_kappa_struct.keys():
        for site_a in parsed_kappa_struct[agent_a].keys():
            for type_data in parsed_kappa_struct[agent_a][site_a]['bnd_states']:
                raw_exp = type_data
                site_b, agent_b = raw_exp.split('.')
                # canonicalize bond name by alphabetical agent number, site name if equal: avoids duplication
                if agent_a < agent_b:
                    bond_name = agent_a + '.' + site_a + '..' + site_b + '.' + agent_b
                elif agent_a > agent_b:
                    bond_name = agent_b + '.' + site_b + '..' + site_a + '.' + agent_a
                else:
                    if site_a < site_b:
                        bond_name = agent_a + '.' + site_a + '..' + site_b + '.' + agent_b
                    else:
                        bond_name = agent_b + '.' + site_b + '..' + site_a + '.' + agent_a
                bond_dict[bond_name] = {'ag_1': agent_a, 'st_1': site_a, 'st_2': site_b, 'ag_2': agent_b}
    return bond_dict


def _define_bond_spline_points(bond_type_dict, init_graphic_struct) -> dict:
    """Define point coordinates for drawing splines based on initialized agent & site data."""
    graphic_bond_points = {}
    for bond_name in bond_type_dict.keys():
        point_dict = {}
        # get agent & site names
        ag_1_name = bond_type_dict[bond_name]['ag_1']
        ag_2_name = bond_type_dict[bond_name]['ag_2']
        st_1_name = bond_type_dict[bond_name]['st_1']
        st_2_name = bond_type_dict[bond_name]['st_2']
        # find agent center positions
        ag_1_center_x = init_graphic_struct[ag_1_name]['loc_x']
        ag_1_center_y = init_graphic_struct[ag_1_name]['loc_y']
        ag_2_center_x = init_graphic_struct[ag_2_name]['loc_x']
        ag_2_center_y = init_graphic_struct[ag_2_name]['loc_y']
        # find site midline angles, special case for symmetric dimerization
        if (ag_1_name == ag_2_name) and (st_1_name == st_2_name):
            st_1_midline = (1.2 * init_graphic_struct[ag_1_name]['bnd_sites'][st_1_name]['theta1'] +
                            0.8 * init_graphic_struct[ag_1_name]['bnd_sites'][st_1_name]['theta2']) / 2
            st_2_midline = (0.8 * init_graphic_struct[ag_2_name]['bnd_sites'][st_2_name]['theta1'] +
                            1.2 * init_graphic_struct[ag_2_name]['bnd_sites'][st_2_name]['theta2']) / 2
        else:
            st_1_midline = (init_graphic_struct[ag_1_name]['bnd_sites'][st_1_name]['theta1'] +
                            init_graphic_struct[ag_1_name]['bnd_sites'][st_1_name]['theta2']) / 2
            st_2_midline = (init_graphic_struct[ag_2_name]['bnd_sites'][st_2_name]['theta1'] +
                            init_graphic_struct[ag_2_name]['bnd_sites'][st_2_name]['theta2']) / 2
        # find agent mantle and surface radii
        ag_1_surface = init_graphic_struct[ag_1_name]['bnd_sites'][st_1_name]['r']
        ag_2_surface = init_graphic_struct[ag_2_name]['bnd_sites'][st_2_name]['r']
        # get point coordinates in cartesian space
        point_dict['a_x'] = ag_1_center_x + np.cos(np.deg2rad(st_1_midline)) * ag_1_surface
        point_dict['a_y'] = ag_1_center_y + np.sin(np.deg2rad(st_1_midline)) * ag_1_surface
        point_dict['d_x'] = ag_2_center_x + np.cos(np.deg2rad(st_2_midline)) * ag_2_surface
        point_dict['d_y'] = ag_2_center_y + np.sin(np.deg2rad(st_2_midline)) * ag_2_surface
        point_dict['b_x'] = ag_1_center_x + np.cos(np.deg2rad(st_1_midline)) * 3 * ag_1_surface
        point_dict['b_y'] = ag_1_center_y + np.sin(np.deg2rad(st_1_midline)) * 3 * ag_1_surface
        point_dict['c_x'] = ag_2_center_x + np.cos(np.deg2rad(st_2_midline)) * 3 * ag_2_surface
        point_dict['c_y'] = ag_2_center_y + np.sin(np.deg2rad(st_2_midline)) * 3 * ag_2_surface
        graphic_bond_points[bond_name] = point_dict
    return graphic_bond_points


def _create_spline(point_dict: dict, bond_width=3):
    """Create a spline object."""
    path_data = [
        (matplotlib.path.Path.MOVETO, (point_dict['a_x'], point_dict['a_y'])),
        (matplotlib.path.Path.CURVE4, (point_dict['b_x'], point_dict['b_y'])),
        (matplotlib.path.Path.CURVE4, (point_dict['c_x'], point_dict['c_y'])),
        (matplotlib.path.Path.CURVE4, (point_dict['d_x'], point_dict['d_y']))
    ]
    # ax.plot([Ax,Bx,Cx,Dx],[Ay,By,Cy,Dy],'ro') #draw the spline's control points
    spline_codes, spline_vertices = zip(*path_data)
    path = matplotlib.path.Path(vertices=spline_vertices, codes=spline_codes)
    spline = matplotlib.patches.PathPatch(path, edgecolor='k', facecolor='none', linewidth=bond_width)
    return spline


def _list_binding_wedges(agent_graphic_struct: dict) -> List[matplotlib.patches.Wedge]:
    """Create a list of wedges from the binding data in the structure."""
    wedge_list = []
    for agent_name in agent_graphic_struct.keys():
        for site_name in agent_graphic_struct[agent_name]['bnd_sites'].keys():
            wedge_parms = agent_graphic_struct[agent_name]['bnd_sites'][site_name]
            this_wedge = matplotlib.patches.Wedge(**wedge_parms, label=site_name)
            wedge_list.append(this_wedge)
    return wedge_list


def _list_flagpole_wedges(agent_graphic_struct: dict) -> List[matplotlib.patches.Wedge]:
    """Create a list of wedges for the flagpoles in the structure."""
    wedge_list = []
    for agent_name in agent_graphic_struct.keys():
        if agent_graphic_struct[agent_name]['flagpole_sites']:
            wedge_parms = agent_graphic_struct[agent_name]['flagpole_loc']
            this_wedge = matplotlib.patches.Wedge(**wedge_parms)
            wedge_list.append(this_wedge)
    return wedge_list


def _annotate_wedges_and_agents(agent_graphic_struct: dict, figure_axis):
    """Annotate an axis with data from the binding sites"""
    agent_txt_kwrds = {'fontfamily': 'monospace', 'fontsize': 'medium',
                       'horizontalalignment': 'center', 'verticalalignment': 'center',
                       'bbox': {'boxstyle': 'round', 'fc': '#ffffffaa'}}
    wedge_txt_kwrds = {'backgroundcolor': '#ddddddaa', 'fontfamily': 'monospace', 'fontsize': 'x-small',
                       'verticalalignment': 'center', 'rotation_mode': 'anchor'}
    for agent_name in agent_graphic_struct.keys():
        ag_x = agent_graphic_struct[agent_name]['loc_x']
        ag_y = agent_graphic_struct[agent_name]['loc_y']
        for site_name in agent_graphic_struct[agent_name]['bnd_sites'].keys():
            site_data = agent_graphic_struct[agent_name]['bnd_sites'][site_name]
            st_midline = (site_data['theta1'] + site_data['theta2']) / 2
            txt_x = ag_x + np.cos(np.deg2rad(st_midline)) * (site_data['r'] - site_data['width'])
            txt_y = ag_y + np.sin(np.deg2rad(st_midline)) * (site_data['r'] - site_data['width'])
            if np.cos(np.deg2rad(st_midline)) > 0:
                text_rotation = 0
                horz_align = 'left'
            else:
                text_rotation = 180
                horz_align = 'right'
            txt_rot = st_midline + text_rotation
            figure_axis.text(s=site_name, x=txt_x, y=txt_y, rotation=txt_rot, **wedge_txt_kwrds,
                             ha=horz_align)
        # agent name should overlay wedge names
        figure_axis.text(s=agent_name, x=ag_x, y=ag_y, **agent_txt_kwrds)


def _draw_flagpole(agent_graphic_struct: dict, figure_axis, detailed_toggle: bool):
    """Draw the flagpole, line, site names, and state list"""
    for agent_name in agent_graphic_struct.keys():
        if agent_graphic_struct[agent_name]['flagpole_sites']:
            # find coordinates for text and lines
            ag_x = agent_graphic_struct[agent_name]['loc_x']
            ag_y = agent_graphic_struct[agent_name]['loc_y']
            fp_loc = agent_graphic_struct[agent_name]['flagpole_loc']
            fp_midline = (fp_loc['theta1'] + fp_loc['theta2']) / 2
            fp_x_base = ag_x + np.cos(np.deg2rad(fp_midline)) * fp_loc['r']
            fp_y_base = ag_y + np.sin(np.deg2rad(fp_midline)) * fp_loc['r']
            fp_x_offs = ag_x + np.cos(np.deg2rad(fp_midline)) * (fp_loc['width'] + fp_loc['r'])
            fp_y_offs = ag_y + np.sin(np.deg2rad(fp_midline)) * (fp_loc['width'] + fp_loc['r'])
            # define string
            fp_strings = []
            for site_name in agent_graphic_struct[agent_name]['flagpole_sites'].keys():
                state_list = agent_graphic_struct[agent_name]['flagpole_sites'][site_name]
                fp_strings.append(site_name + ': ' + ', '.join(state_list))
            fp_string = '\n'.join(fp_strings)
            # define align keywords
            text_kwrds = {'ha': 'left' if np.cos(np.deg2rad(fp_midline)) > 0 else 'right',
                          'va': 'bottom' if np.sin(np.deg2rad(fp_midline)) > 0 else 'top',
                          'fontsize': 'xx-small', 'fontfamily': 'monospace',
                          'backgroundcolor': '#bbbbbb99'}
            # draw the actual flagpole?
            figure_axis.plot([fp_x_base, fp_x_offs], [fp_y_base, fp_y_offs], color='k')
            if detailed_toggle:
                final_string = fp_string
            else:
                fp_annot = ' internal states\nnot shown' if len(fp_strings) > 1 else ' internal state\nnot shown'
                final_string = str(len(fp_strings)) + fp_annot
            figure_axis.text(s=final_string, x=fp_x_offs, y=fp_y_offs, **text_kwrds)


class KappaContactMap:
    """Represent a contact map. Initializer expects a format like that found in the KaSim witness files, `inputs.ka`,
    and is designed to read in from said files. Example usage:
>>> import matplotlib.pyplot as plt
>>> from KaSaAn.core import KappaContactMap

>>> my_contact_map = KappaContactMap('inputs.ka')
>>> fig, ax = plt.subplots(figsize=(6, 6))

>>> my_contact_map.move_agent_to('Fitz', 5, 5)
>>> my_contact_map.move_agent_to('Foo', 10, 15)
>>> my_contact_map.move_agent_to('Bar', 12.5, 2.5)
>>> my_contact_map.move_agent_to('Baz', 0, 12.5)

>>> my_contact_map.rotate_all_sites_of('Foo', 190)
>>> my_contact_map.rotate_all_sites_of('Baz', -180)
>>> my_contact_map.rotate_all_sites_of('Fitz', 30)
>>> my_contact_map.rotate_all_sites_of('Bar', -10)

>>> my_contact_map.draw(ax, draw_state_flagpole=True)
>>> ax.axis('off')
>>> plt.tight_layout()
>>> plt.show()
    """
    def __init__(self, file_name: str):
        # type internal structures
        self._raw_string_list: List[str]
        self._parsed_kappa: Dict[str: dict]
        self._agent_graphics: Dict[str, dict]
        self._bond_types: Dict[dict]
        self._bond_spline_points: List[dict]

        # basic parse of the file into a sanitized structure
        self._raw_string_list = _file_name_to_string_list(file_name)
        parsed_kappa = {}
        for raw_agent_exp in self._raw_string_list:
            agent_name, agent_site_data = _raw_string_to_agent_sites_bond_types(raw_agent_exp)
            parsed_kappa[agent_name] = agent_site_data
        self._parsed_kappa = parsed_kappa

        # create structure used for storing location and plotting of agents and sites, then initialize it
        self._agent_graphics = _parsed_kappa_to_default_graphics(self._parsed_kappa)
        self._agent_graphics = _initialize_sites_graphic_structure(self._agent_graphics, scale_wedges=True)

        # create structure for storing the splines that mark bonds
        self._bond_types = _get_bond_types(self._parsed_kappa)
        self._bond_spline_points = _define_bond_spline_points(self._bond_types, self._agent_graphics)

    def move_agent_to(self, agent_name: str, new_x: float, new_y: float):
        """Change the location of an agent's center by specifying new coordinates, in MatPlotLib "data units"."""
        self._agent_graphics[agent_name]['loc_x'] = new_x
        self._agent_graphics[agent_name]['loc_y'] = new_y
        # update
        self._agent_graphics = _initialize_sites_graphic_structure(self._agent_graphics)
        self._bond_spline_points = _define_bond_spline_points(self._bond_types, self._agent_graphics)

    def move_agent_by(self, agent_name: str, delta_x: float, delta_y: float):
        """Move the location of an agent's center by some amount, in MatPlotLib "data units"."""
        self._agent_graphics[agent_name]['loc_x'] += delta_x
        self._agent_graphics[agent_name]['loc_y'] += delta_y
        # update
        self._agent_graphics = _initialize_sites_graphic_structure(self._agent_graphics)
        self._bond_spline_points = _define_bond_spline_points(self._bond_types, self._agent_graphics)

    def rotate_all_sites_of(self, agent_name: str, degrees: float):
        """Rotate all the sites on an agent by this many degrees; positive rotates counter-clockwise."""
        # rotate binding sites
        for site_name in self._agent_graphics[agent_name]['bnd_sites'].keys():
            self._agent_graphics[agent_name]['bnd_sites'][site_name]['theta1'] += degrees
            self._agent_graphics[agent_name]['bnd_sites'][site_name]['theta2'] += degrees
        # rotate flagpole site
        self._agent_graphics[agent_name]['flagpole_loc']['theta1'] += degrees
        self._agent_graphics[agent_name]['flagpole_loc']['theta2'] += degrees
        # update
        self._bond_spline_points = _define_bond_spline_points(self._bond_types, self._agent_graphics)

    def swap_sites_of(self, agent_name: str, site_1: str, site_2: str):
        """Swap the positions of two specific sites on a given agent (flagpole not eligible as it's a meta-site; use
         `rotate_all_sites_of`)."""
        s1_t_1 = self._agent_graphics[agent_name]['bnd_sites'][site_1]['theta1']
        s1_t_2 = self._agent_graphics[agent_name]['bnd_sites'][site_1]['theta2']
        s2_t_1 = self._agent_graphics[agent_name]['bnd_sites'][site_2]['theta1']
        s2_t_2 = self._agent_graphics[agent_name]['bnd_sites'][site_2]['theta2']
        self._agent_graphics[agent_name]['bnd_sites'][site_1]['theta1'] = s2_t_1
        self._agent_graphics[agent_name]['bnd_sites'][site_1]['theta2'] = s2_t_2
        self._agent_graphics[agent_name]['bnd_sites'][site_2]['theta1'] = s1_t_1
        self._agent_graphics[agent_name]['bnd_sites'][site_2]['theta2'] = s1_t_2
        # update
        self._bond_spline_points = _define_bond_spline_points(self._bond_types, self._agent_graphics)

    def set_site_color_of(self, agent_name: str, site_name: str, new_color):
        """Change the color of a wedge to a new color. Valid options are anything MatPlotLib accepts as a color, e.g.
        `#0f0f0f` (hex RGB[A]), `(0.5, 0.5, 0.5)` (decimal RGB[A]), `xkcd:puke green` (XKCD color survey names)."""
        self._agent_graphics[agent_name]['bnd_sites'][site_name]['facecolor'] = new_color

    def draw(self, target_axis: mpl.axes.Axes, draw_state_flagpole: bool = True):
        """Draw the contact map onto the supplied axis. If `draw_state_flagpole` is `True`, the flagpole will display
        all internal state data. If `False`, it will only display a summary with the number of sites omitted. By
        default, agents are positioned in a square grid, spaced 10 units apart, on the 1st quadrant (e.g. four agents
        would be at coordinates [0,0], [0, 10], [10, 0], and [10, 10])."""
        # draw splines
        spline_list = [_create_spline(bond_entry) for bond_entry in self._bond_spline_points.values()]
        target_axis.add_collection(PatchCollection(spline_list, match_original=True))
        # draw wedges: sites and flagpole
        site_wedges = _list_binding_wedges(self._agent_graphics)
        flag_wedges = _list_flagpole_wedges(self._agent_graphics)
        target_axis.add_collection(PatchCollection(site_wedges, match_original=True))
        target_axis.add_collection(PatchCollection(flag_wedges, match_original=True))
        # draw labels for agents and sites
        _annotate_wedges_and_agents(self._agent_graphics, target_axis)
        # draw flagpole with its text
        _draw_flagpole(self._agent_graphics, target_axis, draw_state_flagpole)
        # update limits, set aspect ratio
        target_axis.autoscale()
        target_axis.set_aspect('equal')

