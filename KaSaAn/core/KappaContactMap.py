#!/usr/bin/env python3
"""Contains `KappaContactMap`, class for representing and fine-tuning the layout of a contact map."""

import colorsys
import random
import re
import matplotlib as mpl
import matplotlib.path
import matplotlib.patches as mpp
import matplotlib.axes as mpa
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import networkx as nx
import networkx.drawing.layout as nxl
import numpy as np
from typing import List, Dict, Tuple


valid_graph_layouts = {
    'random': nxl.random_layout,
    'spring': nxl.spring_layout,
    'spectral': nxl.spectral_layout,
    'kamada-kawai': nxl.kamada_kawai_layout,
    'planar': nxl.planar_layout,
    'circular': nxl.circular_layout,
    'shell': nxl.shell_layout,
    'spiral': nxl.spiral_layout,
    'bipartite': nxl.bipartite_layout,
    # 'multipartite': nxl.multipartite_layout   # unclear what a good subset_key indication would be
}


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


def _create_spline(point_dict: dict, bond_width=3) -> mpp.PathPatch:
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
    spline = mpp.PathPatch(path, edgecolor='k', facecolor='none', linewidth=bond_width)
    return spline


def _list_binding_wedges(agent_graphic_struct: dict) -> List[mpp.Wedge]:
    """Create a list of wedges from the binding data in the structure."""
    wedge_list = []
    for agent_name in agent_graphic_struct.keys():
        for site_name in agent_graphic_struct[agent_name]['bnd_sites'].keys():
            wedge_parms = agent_graphic_struct[agent_name]['bnd_sites'][site_name]
            this_wedge = mpp.Wedge(**wedge_parms, label=site_name)
            wedge_list.append(this_wedge)
    return wedge_list


def _list_flagpole_wedges(agent_graphic_struct: dict) -> List[mpp.Wedge]:
    """Create a list of wedges for the flagpoles in the structure."""
    wedge_list = []
    for agent_name in agent_graphic_struct.keys():
        if agent_graphic_struct[agent_name]['flagpole_sites']:
            wedge_parms = agent_graphic_struct[agent_name]['flagpole_loc']
            this_wedge = mpp.Wedge(**wedge_parms)
            wedge_list.append(this_wedge)
    return wedge_list


def _annotate_wedges_and_agents(agent_graphic_struct: dict, figure_axis: mpa.Axes):
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


def _draw_flagpole(agent_graphic_struct: dict, figure_axis: mpa.Axes, detailed_toggle: bool):
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

    def _update_center_of(self, agent_name: str):
        wedge_center = (self._agent_graphics[agent_name]['loc_x'], self._agent_graphics[agent_name]['loc_y'])
        for this_site in self.get_binding_site_names_of(agent_name):
            self._agent_graphics[agent_name]['bnd_sites'][this_site]['center'] = wedge_center
        if self._agent_graphics[agent_name]['flagpole_sites']:
            self._agent_graphics[agent_name]['flagpole_loc']['center'] = wedge_center

    def get_agent_names(self) -> list[str]:
        """Returns the list of agent names in this contact map."""
        return list(self._parsed_kappa.keys())

    def get_binding_site_names_of(self, agent_name: str) -> list[str]:
        """Returns the list of names for the binding sites belonging to an agent."""
        return list(self._agent_graphics[agent_name]['bnd_sites'].keys())

    def move_agent_to(self, agent_name: str, new_x: float, new_y: float):
        """Change the location of an agent's center by specifying new coordinates, in MatPlotLib "data units"."""
        self._agent_graphics[agent_name]['loc_x'] = new_x
        self._agent_graphics[agent_name]['loc_y'] = new_y
        # update
        self._update_center_of(agent_name)
        self._bond_spline_points = _define_bond_spline_points(self._bond_types, self._agent_graphics)

    def move_agent_by(self, agent_name: str, delta_x: float, delta_y: float):
        """Move the location of an agent's center by some amount, in MatPlotLib "data units"."""
        self._agent_graphics[agent_name]['loc_x'] += delta_x
        self._agent_graphics[agent_name]['loc_y'] += delta_y
        # update
        self._update_center_of(agent_name)
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

    def resize_wedges_of(self, agent_name: str, new_size: float):
        """Resize the wedges of an agent; default size is sqrt of agent's number of wedges, in coordinate-space units."""
        for some_site in self.get_binding_site_names_of(agent_name):
            old_ratio = self._agent_graphics[agent_name]['bnd_sites'][some_site]['r'] / self._agent_graphics[agent_name]['bnd_sites'][some_site]['width']
            self._agent_graphics[agent_name]['bnd_sites'][some_site]['r'] = new_size
            self._agent_graphics[agent_name]['bnd_sites'][some_site]['width'] = new_size / old_ratio
        if self._agent_graphics[agent_name]['flagpole_sites']:
            self._agent_graphics[agent_name]['flagpole_loc']['r'] = new_size
            self._agent_graphics[agent_name]['flagpole_loc']['width'] = new_size / old_ratio
        self._bond_spline_points = _define_bond_spline_points(self._bond_types, self._agent_graphics)

    def draw(self, target_axis: mpa.Axes, draw_state_flagpole: bool = True):
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

    def _derive_multigraph(self) -> nx.classes.multigraph:
        """Derive a multigraph representation of this contact map, with sites as nodes bound to their parent agent."""
        net = nx.MultiGraph()
        # each agent becomes a connected graph
        for this_agent, agent_data in self._parsed_kappa.items():
            local_weight: int = 10 + np.power(len(self._agent_graphics[this_agent]['bnd_sites'].keys()), 2)
            for site_name, site_data in agent_data.items():
                if any(site_data['bnd_states']):
                    net.add_node(this_agent, ka_type='agent')
                    net.add_node(site_name + '@' + this_agent, ka_type='site')
                    net.add_edge(this_agent, site_name + '@' + this_agent, weight=local_weight)
            if any(self._agent_graphics[this_agent]['flagpole_sites']):
                net.add_node('flag@' + this_agent, ka_type='site')
                net.add_edge(this_agent, 'flag@' + this_agent, weight=local_weight)
        # connect agent graphs via bond types
        for bond_data in self._bond_types.values():
            p1 = bond_data['st_1'] + '@' + bond_data['ag_1']
            p2 = bond_data['st_2'] + '@' + bond_data['ag_2']
            net.add_edge(p1, p2, weight=1)
        return net

    def layout_from_graph(self, algorithm_name: str, debug_render=False):
        """Attempt a graph-based layout. Valid algorithm names are found in
         the module `networkx.drawing.layout`."""

        def _relative_theta(parent, site) -> float:
            """Helper function to get the relative angle of an agent's site from the graph."""
            site_rel_x = pos[site][0] - pos[parent][0]
            site_rel_y = pos[site][1] - pos[parent][1]
            ang: float = np.angle(complex(site_rel_x, 0) + complex(0, site_rel_y))
            if ang >= 0:
                return ang
            else:
                return np.pi + (np.pi + ang)    # deal with wrap-around: Pi - (-difference); ang is negative

        def _auto_layout(layout_name: str) -> Dict[str, Tuple[float, float]]:
            """Helper function to set common parameters and report a specific exeption type for planar graphs. The
             layout function is selected by the calling script, and is a member of `networkx.drawing.layout`"""
            pos: Dict[str, Tuple[float, float]]

            kywds = dict(G=net_rep, center=(0, 0), scale=3*np.sqrt(len(net_rep.nodes())))

            match layout_name:
                case 'random':
                    s = kywds.pop('scale')
                    pos = valid_graph_layouts[layout_name](**kywds)
                    pos = nxl.rescale_layout_dict(pos, scale=s)
                case 'spring':
                    pos = valid_graph_layouts[layout_name](**kywds)
                case 'spectral':
                    pos = valid_graph_layouts[layout_name](**kywds)
                case 'kamada-kawai':
                    pos = valid_graph_layouts[layout_name](**kywds)
                case 'planar':
                    try:
                        pos = valid_graph_layouts[layout_name](**kywds)
                    except nx.exception.NetworkXException as e:
                        raise ValueError("Plain graph was not planar, so planar layout is invalid.") from e
                case 'circular':
                    pos = valid_graph_layouts[layout_name](**kywds)
                case 'shell':
                    # layout agents in shells by decreasing connectivity
                    agents_degrees: Dict[str, int] = {}
                    for a_bond in self._bond_types.values():
                        if a_bond['ag_1'] != a_bond['ag_2']:
                            if a_bond['ag_1'] in agents_degrees:
                                agents_degrees[a_bond['ag_1']] += 1
                            else:
                                agents_degrees[a_bond['ag_1']] = 1
                            if a_bond['ag_2'] in agents_degrees:
                                agents_degrees[a_bond['ag_2']] += 1
                            else:
                                agents_degrees[a_bond['ag_2']] = 0
                    agents_by_connectivity = sorted(agents_degrees.items(), key=lambda item: item[1])
                    agents_by_shell: List[List[str]] = []
                    stop_ix = 3
                    while agents_by_connectivity:
                        stop_ix = min(stop_ix, len(agents_by_connectivity))
                        this_shell: List[str] = []
                        for _ in range(0, stop_ix):
                            this_shell.append(agents_by_connectivity.pop()[0])
                        agents_by_shell.append(this_shell)
                        stop_ix *= 2
                    pos_ag = valid_graph_layouts[layout_name](nlist=agents_by_shell, **kywds)
                    # layout sites using spring layout, given fixed positions for agents
                    for n_id, n_type in net_rep.nodes.data('ka_type'):
                        if n_type == 'site':
                            parent = n_id.split('@')[1]
                            pos_ag[n_id] = pos_ag[parent]
                    pos = valid_graph_layouts['spring'](pos=pos_ag, fixed=list(self._agent_graphics), **kywds)
                case 'spiral':
                    pos = valid_graph_layouts[layout_name](equidistant=True, **kywds)
                case 'bipartite':
                    ag_data: List[Tuple[str, int]] = []
                    for this_agent, agent_data in self._agent_graphics.items():
                        num_sites: int = len(agent_data['bnd_sites'].keys())
                        ag_data.append((this_agent, num_sites))
                    ag_data.sort(key=lambda item: item[1], reverse=True)
                    n = int(np.floor(np.sqrt(len(ag_data))))
                    top_n = [item[0] for item in ag_data[0:n]]
                    pos = valid_graph_layouts[layout_name](nodes=top_n, **kywds)
                case _:
                    raise ValueError('Invalid layout {} requested. Options are: {}'.format(layout_name,
                                                                                           valid_graph_layouts.keys()))
            return pos

        net_rep: nx.multigraph = self._derive_multigraph()
        pos = _auto_layout(algorithm_name)

        # debug image
        if debug_render:
            import matplotlib.pyplot as plt
            _, ax = plt.subplots()
            # intra-agent edges
            nx.draw_networkx_edges(G=net_rep, pos=pos, ax=ax, edge_color='tab:gray', label='intra-agent', width=5,
                                   edgelist=[(u, v, w) for (u, v, w) in net_rep.edges.data("weight") if w != 1])
            # inter-agent edges
            nx.draw_networkx_edges(G=net_rep, pos=pos, ax=ax, edge_color='tab:brown', label='inter-agent', width=1,
                                   edgelist=[(u, v, w) for (u, v, w) in net_rep.edges.data("weight") if w == 1])
            # sites
            nx.draw_networkx_nodes(G=net_rep, pos=pos, ax=ax, node_color='tab:orange', label='site',
                                   nodelist=[n for n in net_rep.nodes() if net_rep.nodes[n]['ka_type'] == 'site'])
            # agent centers
            nx.draw_networkx_nodes(G=net_rep, pos=pos, ax=ax, node_color='tab:blue', label='agent',
                                   nodelist=[n for n in net_rep.nodes() if net_rep.nodes[n]['ka_type'] == 'agent'])
            # annotate nodes
            nx.draw_networkx_labels(G=net_rep, pos=pos, ax=ax, labels={item: item.split('@')[0] for item in pos})
            ax.legend()
            ax.autoscale()
            ax.set_aspect('equal')
            ax.set_title('Debug plain graph view')

        # layout agents, define wedge order, figure out flagpole, sort sites
        agent_wedge_order: Dict[str: List[Tuple[str, float]]] = {}
        for n_id, n_type in net_rep.nodes.data('ka_type'):
            if n_type == 'agent':
                # layout agents
                self.move_agent_to(agent_name=n_id, new_x=pos[n_id][0], new_y=pos[n_id][1])
                # define desired wedge order
                ag_sites: List[str] = list(nx.classes.function.neighbors(net_rep, n_id))
                if len(ag_sites) >= 2:
                    site_thetas: List[Tuple[str, float]] = []
                    for this_site in ag_sites:
                        site_thetas.append((this_site, _relative_theta(n_id, this_site)))
                    agent_wedge_order[n_id] = sorted(site_thetas, key=lambda item: item[1])
        # to define rotation & flagpole position, average inter-agent (outgoing) vectors
        agent_outs: Dict[str: Dict[str: float]] = {}
        for node_1, node_2, edge_data in net_rep.edges.data():
            if edge_data['weight'] == 1:
                site_1_name, site_1_parent = node_1.split('@')
                site_2_name, site_2_parent = node_2.split('@')
                if site_1_parent != site_2_parent:
                    t1 = _relative_theta(site_1_parent, node_1)
                    t2 = _relative_theta(site_2_parent, node_2)
                    if site_1_parent not in agent_outs:
                        agent_outs[site_1_parent] = {site_1_name: t1}
                    else:
                        agent_outs[site_1_parent][site_1_name] = t1
                    if site_2_parent not in agent_outs:
                        agent_outs[site_2_parent] = {site_2_name: t2}
                    else:
                        agent_outs[site_2_parent][site_2_name] = t2
        ag_headings: Dict[str: float] = {}
        for agent_name, site_outs in agent_outs.items():
            ag_headings[agent_name] = np.mean(list(site_outs.values()))
        # define stop of rotation, and correct warp-arounds
        #  if there is a flagpole, that's the final wedge
        #  otherwise, find the last wedge
        for agent_name, wedge_order in agent_wedge_order.items():
            if ('flag@' + agent_name) in [item[0] for item in wedge_order]:
                flagpole_ix = [item[0] for item in wedge_order].index('flag@' + agent_name)
                if flagpole_ix != (len(wedge_order) - 1):
                    for ix in range(len(wedge_order)):
                        site_name, site_theta = wedge_order[ix]
                        if site_theta > wedge_order[flagpole_ix][1]:
                            wedge_order[ix] = (site_name, site_theta - 2 * np.pi)
                agent_wedge_order[agent_name] = sorted(wedge_order, key=lambda item: item[1])
            else:
                _, final_wedge_theta = wedge_order[-1]
                for ix in range(len(wedge_order)):
                    site_name, site_theta = wedge_order[ix]
                    if site_theta > final_wedge_theta:
                        wedge_order[ix] = (site_name, site_theta - 2 * np.pi)
                agent_wedge_order[agent_name] = sorted(wedge_order, key=lambda item: item[1])
        # swap sites to match order
        for this_agent, desired_order in agent_wedge_order.items():
            desired_order: Dict[str: float] = dict(desired_order)
            current_order: List[Tuple[str, float]] = [(k, v['theta1']) for k, v in
                                                      self._agent_graphics[this_agent]['bnd_sites'].items()]
            current_order.sort(key=lambda item: item[1])
            # bubble sort
            #  Since the graphic structure is quite divorced, I track manually indexes.
            #  The final element of each iteration is as its correct position, so I move
            #  the index that points to that position to terminate the loop earlier.
            for final_wedge_ix in range(len(current_order) - 1, -1, -1):
                for ix in range(0, final_wedge_ix):
                    site_a, curr_a = current_order[ix]
                    site_b, curr_b = current_order[ix + 1]
                    obs_a: float = desired_order[site_a + '@' + this_agent]
                    obs_b: float = desired_order[site_b + '@' + this_agent]
                    if (obs_a < obs_b) & (not curr_a < curr_b):
                        self.swap_sites_of(this_agent, site_a, site_b)
                        current_order = [(k, v['theta1']) for k, v in
                                         self._agent_graphics[this_agent]['bnd_sites'].items()]
                        current_order.sort(key=lambda item: item[1])
                    elif (obs_a > obs_b) & (not curr_a > curr_b):
                        self.swap_sites_of(this_agent, site_a, site_b)
                        current_order = [(k, v['theta1']) for k, v in
                                         self._agent_graphics[this_agent]['bnd_sites'].items()]
                        current_order.sort(key=lambda item: item[1])
                    else:
                        pass
        # rotate agent to match orientation
        #  If agent has a flagpole, use that as the anchor, as wedges were sorted against that.
        #  Otherwise, if agent has one wedge, it's pointing to [-1, 0] by default, so 180 degrees.
        #  Otherotherwise, get outgoing sites (computed previously) and average their orientations to define the
        #  current agent's heading.
        for n_id, n_type in net_rep.nodes.data('ka_type'):
            if n_type == 'agent':
                has_flagpole: bool = bool(self._agent_graphics[n_id]['flagpole_sites'])
                ag_wedges: int = len(self._agent_graphics[n_id]['bnd_sites'])
                if has_flagpole:
                    f_dict = self._agent_graphics[n_id]['flagpole_loc']
                    curr_theta: float = (f_dict['theta1'] + f_dict['theta2']) / 2
                    desi_theta: float = np.rad2deg(_relative_theta(n_id, 'flag@' + n_id))
                else:
                    desi_theta: float = np.rad2deg(ag_headings[n_id])
                    if ag_wedges == 1:
                        curr_theta = 180
                    else:
                        curr_thetas = []
                        for site_name in agent_outs[n_id].keys():
                            d = self._agent_graphics[n_id]['bnd_sites'][site_name]
                            curr_thetas.append((d['theta1'] + d['theta2']) / 2)
                        curr_theta = np.mean(curr_thetas)
                self.rotate_all_sites_of(n_id, desi_theta - curr_theta)
