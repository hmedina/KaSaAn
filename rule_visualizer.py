#! /usr/bin/python3

import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches
from matplotlib.collections import PatchCollection
import matplotlib.path as mpath


########################################################################################################################
# Functions
########################################################################################################################
def process_rule(kappa_rule):
    # This function digests a kappa rule into its constituent components
    # Remove trailing comment and leading/trialing whitespaces
    digested_rule = kappa_rule.split('//')
    kappa_rule = digested_rule[0].strip()
    if len(digested_rule) > 1:
        rule_comment = digested_rule[1].strip()
    else:
        rule_comment = ''
    # Parse rule into basic components
    rule_components = re.match(pattern="('.+')?\s?(.+)\s*@\s*([a-zA-Z0-p\.]+)\s*{?([a-zA-Z0-9\.']+)?}?", string=kappa_rule)
    rule_name = rule_components.group(1).strip() if rule_components.group(1) else ''
    rule_expr = rule_components.group(2).strip() if rule_components.group(2) else None
    rule_rate_pri = rule_components.group(3).strip() if rule_components.group(3) else None
    rule_rate_uni = rule_components.group(4).strip() if rule_components.group(4) else None
    rule_rates = [rule_rate_pri, rule_rate_uni]
    assert rule_expr, 'Problem: no rule expression found in <<' + kappa_rule + '>>'
    assert rule_rate_pri, 'Problem: no primary rate found in <<' + kappa_rule + '>>'
    # Uniform separation of agents
    rule_expr = rule_expr.replace('),', ') ')
    rule_expr = re.sub(pattern='\s\s+', repl=' ', string=rule_expr)
    return rule_expr, rule_name, rule_rates, rule_comment


def process_expression(kappa_expression):
    # Uniform separation of agents
    kappa_expression = kappa_expression.replace('),', ') ')
    kappa_expression = re.sub(pattern='\s\s+', repl=' ', string=kappa_expression)
    # This function digests a kappa expression (no names, no rates, no comments)
    expression_agents = kappa_expression.split(') ') #Split expression into separate agents
    agent_list = []
    for entry in expression_agents:
        entry = str(entry)
        # Get agent's name
        agent = entry.split('(')
        agent_name = agent[0]
        assert agent_name, 'Problem: agent name not found in <<' + entry + '>>'
        agent_signature = agent[1].replace(',', ' ').split(' ')
        # Figure out which sites have bond information
        bond_sites = []
        flagpole_states = []
        for site in agent_signature:
            site_structure = re.match(pattern='([a-zA-Z]\w*)({\w+}|{\w+/\w+})?\[(\./\d+|\.|\d+|\d+/\.)\]({\w+}|{\w+/\w+})?', string=site)
            site_name = site_structure.group(1) if site_structure.group(1) else None
            assert site_name, 'Problem: site name not found in <<' + site + '>>'
            # Save state info if present; group 2 if leading bond data, group 4 of trailing bond data
            if site_structure.group(2):
                site_state = site_structure.group(2)
            elif site_structure.group(4):
                site_state = site_structure.group(4)
            else:
                site_state = None
            # Sort sites into two lists: bond-sites and state-only sites
            site_bond = site_structure.group(3)
            assert site_bond, 'Problem: no bond information found for <<' + site + '>>'
            if site_bond != '.':
                bond_sites.append({'site_name': site_name, 'site_bond':site_bond, 'site_theta': None})
            else:
                if site_state:
                    flagpole_states.append({'site_name': site_name, 'site_state': site_state[1:-1]})
                else:
                    flagpole_states.append({'site_name': site_name, 'site_state': '.'})
        # Add flagpole data if necessary
        if flagpole_states:
            state_sites = {'flagpole_theta': None, 'flagpole_states': flagpole_states}
        else:
            state_sites = []
        # Package data
        agent_list.append({'agent_name': agent_name, 'agent_theta': None, 'radius_to_agent': None,
                           'bond_sites': bond_sites, 'state_sites': state_sites})
    return agent_list

# ToDo: deal with wildcards


def define_thetas_and_radii(agent_list, base_radius_to_agent=1):
    # Layout in a hexagonal pattern: 6, 12, 18, 24 etc. per level
    layout_level = 1
    layout_base = 6
    agent_num = len(agent_list)
    agent_thetas = []
    agent_radii = []
    # Generate the agent thetas & radii, wrapping around as we climb levels
    if agent_num > layout_base:
        while len(agent_thetas) < agent_num:
            agent_thetas += list(np.linspace(start=0, stop=2*np.pi, endpoint=False, num=layout_base*layout_level)) #radians
            agent_radii += [base_radius_to_agent * layout_level] * layout_base*layout_level
            layout_level += 1
    else:
        agent_thetas += list(np.linspace(start=0, stop=2*np.pi, endpoint=False, num=agent_num)) #radians
        agent_radii += [base_radius_to_agent] * agent_num
    # Add the theta and radius data to each agent
    for agent in range(agent_num):
        agent_list[agent]['agent_theta'] = agent_thetas[agent]
        agent_list[agent]['radius_to_agent'] = agent_radii[agent]
        # Since we're grouping state-only sites into the flagpole site, we only consider for drawing the number of
        # binding sites, plus the flagpole site. Agents may have no state-only sites, therefore the flagpole site may
        # not be needed. This check assays if there is a flagpole site, and if so assigns it a theta
        bond_site_num = len(agent_list[agent]['bond_sites'])
        if agent_list[agent]['state_sites']:
            site_num = bond_site_num + 1
            site_thetas = np.linspace(start=0, stop=2*np.pi, endpoint=False, num=site_num) #in radians
            agent_list[agent]['state_sites']['flagpole_theta'] = site_thetas[-1]
        else:
            site_num = bond_site_num
            site_thetas = np.linspace(start=0, stop=2*np.pi, endpoint=False, num=site_num) #in radians
        # Define & assign thetas to each bond site
        for site in range(bond_site_num):
            agent_list[agent]['bond_sites'][site]['site_theta'] = site_thetas[site]
    return agent_list


def get_bond_termini(agent_list):
    # Read through the agent list and get the bond termini
    bond_termini_list = []
    for agent in agent_list:
        for site in agent['bond_sites']:
            bond_state = site['site_bond']
            #if this is unbound, ignore and move on
            if bond_state == '.':
                pass
            #in case we have a bond swap; ergo two bonds
            elif re.match(pattern='(\d+)/(\d+)', string=bond_state):
                b = re.match(pattern='(\d+)/(\d+)', string=bond_state)
                bond_termini_list.append({'bond_id': b.group(1),
                                          'agent_theta': agent['agent_theta'],
                                          'radius_to_agent': agent['radius_to_agent'],
                                          'site_theta': site['site_theta'],
                                          'status': '-'})
                bond_termini_list.append({'bond_id': b.group(2),
                                          'agent_theta': agent['agent_theta'],
                                          'radius_to_agent': agent['radius_to_agent'],
                                          'site_theta': site['site_theta'],
                                          'status': '+'})
            #in case we have bond deletion
            elif re.match(pattern='(\d+)/\.', string=bond_state):
                b = re.match(pattern='(\d+)/\.', string=bond_state)
                bond_termini_list.append({'bond_id': b.group(1),
                                          'agent_theta': agent['agent_theta'],
                                          'radius_to_agent': agent['radius_to_agent'],
                                          'site_theta': site['site_theta'],
                                          'status': '-'})
            #in case we have bond creation
            elif re.match(pattern='\./(\d+)', string=bond_state):
                b = re.match(pattern='\./(\d+)', string=bond_state)
                bond_termini_list.append({'bond_id': b.group(1),
                                          'agent_theta': agent['agent_theta'],
                                          'radius_to_agent': agent['radius_to_agent'],
                                          'site_theta': site['site_theta'],
                                          'status': '+'})
            #in case we have bond being kept
            elif re.match(pattern='\d+', string=bond_state):
                b = re.match(pattern='\d+', string=bond_state)
                bond_termini_list.append({'bond_id': b.group(0),
                                          'agent_theta': agent['agent_theta'],
                                          'radius_to_agent': agent['radius_to_agent'],
                                          'site_theta': site['site_theta'],
                                          'status': '='})
            else:
                raise TypeError('Unknown bond state <<' + bond_state + '>>')
    assert len(bond_termini_list) % 2 == 0, 'Problem: bond termini list is not of even length'
    return bond_termini_list


def pair_bond_termini(bond_termini_list):
    # Populate a dictionary, where the key is the bond identifier, and the values are the thetas and radii of where the
    # bond should point to
    bond_list = {}
    for bond_terminus in bond_termini_list:
        bond_name = bond_terminus['bond_id']
        agent_theta = bond_terminus['agent_theta']
        radius_to_agent = bond_terminus['radius_to_agent']
        site_theta = bond_terminus['site_theta']
        bond_status = bond_terminus['status']
        if bond_name not in bond_list:
            bond_list[bond_name] = {'agent_1_theta': agent_theta,
                                    'agent_1_radius': radius_to_agent,
                                    'site_1_theta': site_theta,
                                    'bond_status': bond_status}
        else:
            bond_list[bond_name]['agent_2_theta'] = agent_theta
            bond_list[bond_name]['agent_2_radius'] = radius_to_agent
            bond_list[bond_name]['site_2_theta'] = site_theta
            assert bond_status == bond_list[bond_name]['bond_status'], 'Bond termini mismatch in state.'
    return bond_list


def draw_agent_labels(agent_list, axis, with_identifiers=False):
    # Draw a name for each agent, i.e. their name + optionally an identifier
    agent_num = len(agent_list)
    for i in range(agent_num):
        agent = agent_list[i]
        x = agent['radius_to_agent'] * np.cos(agent['agent_theta'])
        y = agent['radius_to_agent'] * np.sin(agent['agent_theta'])
        if with_identifiers:
            text_to_print = agent['agent_name'] + ':' + str(i)
        else:
            text_to_print = agent['agent_name']
        axis.text(x=x, y=y, s=text_to_print,
                  verticalalignment='center', horizontalalignment='center')
    return axis


def draw_site_wedges(agent_list, radius_to_site, wedge_width, axis, with_identifiers=False):
    site_wedges = []
    agent_num = len(agent_list)
    for i in range(agent_num):
        agent = agent_list[i]
        x = agent['radius_to_agent'] * np.cos(agent['agent_theta'])
        y = agent['radius_to_agent'] * np.sin(agent['agent_theta'])
        agent_center = [x,y]
        # Number of wedges to draw in total (i.e. including flagpole)
        bond_site_num = len(agent['bond_sites'])
        if agent['state_sites']:
            wedge_num = bond_site_num + 1
        else:
            wedge_num = bond_site_num
        half_wedge_arc = (2 * np.pi) / (wedge_num * 2)
       # Define the bond sites wedges
        for bond_site in range(bond_site_num):
            midline_theta = agent['bond_sites'][bond_site]['site_theta']
            theta_1 = midline_theta - half_wedge_arc
            theta_2 = midline_theta + half_wedge_arc
            w = matplotlib.patches.Wedge(center=agent_center,
                                         r=radius_to_site,
                                         width=wedge_width,
                                         theta1=np.rad2deg(theta_1),
                                         theta2=np.rad2deg(theta_2),
                                         color='C' + str(bond_site))
            site_wedges.append(w)
            # Add labels on top of these wedges
            r = (radius_to_site + wedge_width) / 2
            # For the last site, figure out if we're supposed to write anything here of it its the flagpole site
            site_name = agent['bond_sites'][bond_site]['site_name']
            # Add the site's name to the figure, optionally with a unique identifier
            if with_identifiers:
                name_to_print = site_name + ':' + str(bond_site)
            else:
                name_to_print = site_name
            axis.text(x=r * np.cos(midline_theta) + agent_center[0],
                      y=r * np.sin(midline_theta) + agent_center[1],
                      s=name_to_print,
                      verticalalignment='center',
                      horizontalalignment='center')
        # Define the flagpole wedge, if required
        if agent['state_sites']:
            midline_theta = agent['state_sites']['flagpole_theta']
            theta_1 = midline_theta - half_wedge_arc
            theta_2 = midline_theta + half_wedge_arc
            w = matplotlib.patches.Wedge(center=agent_center,
                                         r=radius_to_site,
                                         width=wedge_width,
                                         theta1=np.rad2deg(theta_1),
                                         theta2=np.rad2deg(theta_2),
                                         color='C' + str(wedge_num))
            site_wedges.append(w)
    # Package wedges into patch collection; add to axis
    wedge_collection = PatchCollection(site_wedges, match_original=True)
    axis.add_collection(wedge_collection)
    return axis

# ToDo: deal with +10 color scheme


def draw_bond_splines(bond_list, radius_to_site, spline_offset, axis):
    # Each bond gets represented as a quadratic spline, where the points are:
    # A | terminus | sits at the "surface" of the first agent
    # D | terminus | sits at the "surface" of the second agent
    # B | anchor | sits along the theta angle projected out from point A, used to get squiggly lines
    # C | anchor | sits along the theta angle projected out from point B, used to get squiggly lines
    spline_list = []
    for bond_name in bond_list.keys():
        bond = bond_list[bond_name]
        # Center of 1st agent
        agent_1_x = bond['agent_1_radius'] * np.cos(bond['agent_1_theta'])
        agent_1_y = bond['agent_1_radius'] * np.sin(bond['agent_1_theta'])
        # Center of 2nd agent
        agent_2_x = bond['agent_2_radius'] * np.cos(bond['agent_2_theta'])
        agent_2_y = bond['agent_2_radius'] * np.sin(bond['agent_2_theta'])
        # Determine what color to use
        if bond['bond_status'] == '=':
            bond_color = 'k'
        elif bond['bond_status'] == '-':
            bond_color = 'r'
        elif bond['bond_status'] == '+':
            bond_color = 'g'
        else:
            print('Unknown bond status <<' + bond['bond_status'] + '>> for bond id <<' + bond_name + '>>, defaulting to black.')
            bond_color = 'k'
        # Get X,Y coordinates for all 4 control points of the quadratic spline
        a_x = radius_to_site * np.cos(bond['site_1_theta']) + agent_1_x
        a_y = radius_to_site * np.sin(bond['site_1_theta']) + agent_1_y
        b_x = (spline_offset + radius_to_site) * np.cos(bond['site_1_theta']) + agent_1_x
        b_y = (spline_offset + radius_to_site) * np.sin(bond['site_1_theta']) + agent_1_y
        c_x = (spline_offset + radius_to_site) * np.cos(bond['site_2_theta']) + agent_2_x
        c_y = (spline_offset + radius_to_site) * np.sin(bond['site_2_theta']) + agent_2_y
        d_x = radius_to_site * np.cos(bond['site_2_theta']) + agent_2_x
        d_y = radius_to_site * np.sin(bond['site_2_theta']) + agent_2_y
        # Pack into quadratic spline form
        path_data = [
            (mpath.Path.MOVETO, (a_x, a_y)),
            (mpath.Path.CURVE4, (b_x, b_y)),
            (mpath.Path.CURVE4, (c_x, c_y)),
            (mpath.Path.CURVE4, (d_x, d_y))
        ]
        #ax.plot([Ax,Bx,Cx,Dx],[Ay,By,Cy,Dy],'ro') #draw the spline's control points
        spline_codes, spline_vertices = zip(*path_data)
        path = mpath.Path(vertices=spline_vertices, codes=spline_codes)
        spline = matplotlib.patches.PathPatch(path, edgecolor=bond_color, facecolor='none', linewidth='3')
        spline_list.append(spline)
    axis.add_collection(PatchCollection(spline_list, match_original=True))
    return axis


def draw_flagpole(agent_list, radius_to_site, axis):
    flagpole_base_length = radius_to_site / 4
    for agent in agent_list:
        if agent['state_sites']:
            agent_x = agent['radius_to_agent'] * np.cos(agent['agent_theta'])
            agent_y = agent['radius_to_agent'] * np.sin(agent['agent_theta'])
            flagpole_theta = agent['state_sites']['flagpole_theta']
            site_num_offset = 0
            site_data = []
            # Coordinates for the flagpole base points
            flagpole_base_x = radius_to_site * np.cos(flagpole_theta) + agent_x
            flagpole_base_y = radius_to_site * np.sin(flagpole_theta) + agent_y
            arm_base_x = (flagpole_base_length + radius_to_site) * np.cos(flagpole_theta) + agent_x
            arm_base_y = (flagpole_base_length + radius_to_site) * np.sin(flagpole_theta) + agent_y
            # Alignment of the text boxes & text rotation: per pi/8 rotated quadrant (e.g. North|East|South|West)
            # Since MatPlotLib's text alignment is for the bounding box, it is far easier to layout horizontally or
            # vertically, not any other angle. Therefore text alignment & rotation will be chosen depending on which
            # quadrant is the flagpole getting drawn at.
            if flagpole_theta < np.pi/4:        #first half of East quadrant
                name_align_h = 'center'
                name_align_v = 'top'
                state_align_h = 'center'
                state_align_v = 'bottom'
                text_rotation = np.pi /2
                for site in agent['state_sites']['flagpole_states']:
                    center_x = (arm_base_x + 0.2 * radius_to_site * site_num_offset)
                    center_y = arm_base_y
                    name = site['site_name']
                    state = site['site_state']
                    site_data.append({'center_x': center_x, 'center_y': center_y, 'name': name, 'state': state})
                    site_num_offset += 1
            elif flagpole_theta < np.pi*3/4:    #north quadrant
                name_align_h = 'right'
                name_align_v = 'center'
                state_align_h = 'left'
                state_align_v = 'center'
                text_rotation = 0
                for site in agent['state_sites']['flagpole_states']:
                    center_x = arm_base_x
                    center_y = arm_base_y + 0.2 * radius_to_site * site_num_offset
                    name = site['site_name']
                    state = site['site_state']
                    site_data.append({'center_x': center_x, 'center_y': center_y, 'name': name, 'state': state})
                    site_num_offset += 1
            elif flagpole_theta < np.pi*5/4:    #west quadrant
                name_align_h = 'center'
                name_align_v = 'top'
                state_align_h = 'center'
                state_align_v = 'bottom'
                text_rotation = np.pi / 2
                for site in agent['state_sites']['flagpole_states']:
                    center_x = arm_base_x - 0.2 * radius_to_site * site_num_offset
                    center_y = arm_base_y
                    name = site['site_name']
                    state = site['site_state']
                    site_data.append({'center_x': center_x, 'center_y': center_y, 'name': name, 'state': state})
                    site_num_offset += 1
            elif flagpole_theta < np.pi*7/4:    #south quadrant
                name_align_h = 'right'
                name_align_v = 'center'
                state_align_h = 'left'
                state_align_v = 'center'
                text_rotation = 0
                for site in agent['state_sites']['flagpole_states']:
                    center_x = arm_base_x
                    center_y = arm_base_y - 0.2 * radius_to_site * site_num_offset
                    name = site['site_name']
                    state = site['site_state']
                    site_data.append({'center_x': center_x, 'center_y': center_y, 'name': name, 'state': state})
                    site_num_offset += 1
            else:                               #second half of East quadrant
                name_align_h = 'center'
                name_align_v = 'top'
                state_align_h = 'center'
                state_align_v = 'bottom'
                text_rotation = np.pi / 2
                for site in agent['state_sites']['flagpole_states']:
                    center_x = arm_base_x + 0.2 * radius_to_site * site_num_offset
                    center_y = arm_base_y
                    name = site['site_name']
                    state = site['site_state']
                    site_data.append({'center_x': center_x, 'center_y': center_y, 'name': name, 'state': state})
                    site_num_offset += 1
            # Draw the list of labels
            for site in site_data:
                # If site has a modification, draw a bounding box around it
                if re.match(pattern='.+/.+', string=site['state']):
                    bounding_box = {'facecolor': '1.0', 'edgecolor': '0.0', 'pad': 0, 'alpha': 0.5}
                else:
                    bounding_box = {}
                axis.text(x=site['center_x'], y=site['center_y'], s=site['name'] + ':', bbox=bounding_box,
                          rotation=np.rad2deg(text_rotation), ha=name_align_h, va=name_align_v)
                axis.text(x=site['center_x'], y=site['center_y'], s=':' + site['state'], bbox=bounding_box,
                          rotation=np.rad2deg(text_rotation), ha=state_align_h, va=state_align_v)
            # Draw the actual flagpole: base to arm, arm to last site
            axis.plot([flagpole_base_x, arm_base_x, site_data[-1]['center_x']],
                      [flagpole_base_y, arm_base_y, site_data[-1]['center_y']])
    return axis

########################################################################################################################
# Tools to swap positions, of agents, of sites
########################################################################################################################
# ToDo: add tools to swap positions of agents, sites


########################################################################################################################
# Draw it all
########################################################################################################################

#my_rule = "'some rule' A(b[.],s[.]{x}),B(a[.]) -> A(b[1],x{u}),B(a[1]) @ 1 {2} //some comment @ some line"
my_rule = "'some rule' A(b[./1],f[.]{p/h},c[2],foo[.]{bar}),B(a[./1],c[3/.]),C(a[2],b[3/.]) @ 1 {2} //some comment @ some line"
my_complex = "X(a[1] b[.] c[2]), X(a[.] b[1] c[3]),Y(a[.] b[4] d[3]), Y(a[4] b[.] d[.]), Y(a[.] b[5] d[2]), Y(a[5] b[6] d[.]),Y(a[6] b[.] d[7]), X(a[.] b[8] c[7]), X(a[8] b[.] c[9]), Y(a[.] b[.] d[9])"

# Parameters for resolution & scale of figure (e.g. radius to agent from center, radius of wedge)
my_rad_to_agent = 1                       #distance to center of agents from axes origin 0,0
my_rad_to_site = my_rad_to_agent * 1/4    #distance from center of agent to outer edge of wedge
my_wedge_width = my_rad_to_site * 1/2     #width of a wedge
my_spline_offset = my_rad_to_site         #distance between point & control-point for quadratic splines

# Get the agent list
my_expression, my_rule_name, my_rule_rates, my_rule_comment = process_rule(my_rule)

# Assign the theta angles
my_agent_list = process_expression(my_expression)
my_agent_list = define_thetas_and_radii(my_agent_list, my_rad_to_agent)

# Calculate bond splines
my_bond_termini = get_bond_termini(my_agent_list)
my_bond_list = pair_bond_termini(my_bond_termini)

# Define the figure
my_fig = plt.figure()
my_ax = my_fig.add_subplot(1, 1, 1, aspect=1)
my_ax.axis('off')
margin_distance = my_rad_to_agent + 2 * my_rad_to_site
my_ax.set_xlim(left=-margin_distance, right=margin_distance)
my_ax.set_ylim(bottom=-margin_distance, top=margin_distance)

# Annotate figure with rule name & rates
plt.title(my_rule_name, loc='left')
pretty_print_rates = '@ ' + my_rule_rates[0] + ('{' + my_rule_rates[1] + '}' if len(my_rule_rates) > 1 else '')
plt.title(pretty_print_rates, loc='right')

# Draw stuff
my_ax = draw_agent_labels(my_agent_list, my_ax)
my_ax = draw_site_wedges(my_agent_list, my_rad_to_site, my_wedge_width, my_ax)
my_ax = draw_bond_splines(my_bond_list, my_rad_to_site, my_spline_offset, my_ax)
my_ax = draw_flagpole(my_agent_list, my_rad_to_site, my_ax)

plt.show()
# To view the snapshot:
#plt.close()
#my_agent_list = process_expression(my_complex)
#my_agent_list = process_expression(my_expression)
#my_agent_list = define_thetas_and_radii(my_agent_list, my_rad_to_agent)
#my_bond_termini = get_bond_termini(my_agent_list)
#my_bond_list = pair_bond_termini(my_bond_termini)