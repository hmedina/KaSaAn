#!/usr/bin/env python3

import re
from typing import List, Dict
from KaSaAn.core import KappaRule, KappaPort, KappaCounter


# To render edit notation, to render snapshot components, I need to render essentially
# KappaComplex; all else are decorations, like names or rates, which should be optional

class DrawableKappa:
    def __init__(self, input_kappa: KappaRule):
        #What is to be drawn where
        # [index in master list, agent center index, [index in site list, site center index]]
        self._agent_mapping: List[int, int, List[int, int]]

        #Mapped entities ready to be drawn: sites / wedges, bonds / splines, flagpole aggregator, names
        # [site name, parent's center, site's index]
        self._mapped_sites: List[str, int, int]
        # [identifier, agent A index, site A index, agent B index, site B index, operation]
        self._mapped_bonds: List[str, int, int, int, int, str]
        # [parent's center, site's index, [state, operation?]]
        self._mapped_flagpole: List[int, int, List[str, bool]]
        # [agent name, index]
        self._mapped_agent_names: List[str, int]

        #The actual location of stuff in canvas coordinates
        # [site name, [center X, center Y], width, height, theta, color]
        self._drawing_wedges: List[str, List[float, float], float, float, float, str]
        # [[Ax, Ay], [Bx, By], [Cx, Cy], [Dx, Dy], color]
        self._drawing_splines: List[List[float, float], List[float, float], List[float, float], List[float, float], str]
        # [agent name, [center X, center Y]]
        self._drawing_names: List[str, List[float, float]]

        # Parse the input expression & figure out what sites to draw as full wedges, what sites so group into the
        # flagpole, and make the list of bonds to draw
        # [agent name, agent operation, [site name, state data, state operation], [state data, state operation]]
        self._sites_to_draw: List[str, str, List[str, str, bool], List[str, bool]]
        self._sites_to_draw = []

        self._bonds_to_draw = {}
        for bond in input_kappa.get_bond_identifiers():
            self._bonds_to_draw[bond] = {'agent_A': None, 'agent_B': None, 'site_A': None, 'site_B': None}
        #ToDo bond identifiers are not good idnetifiers: the following is sound syntax "Bob(s1[2/.], s2[2/.], s3[./2], s4[./2]) @ 1" so I need to create identifiers, and then somehow match them...
        #ToDo add get_created_bonds method to rule? get_deleted_bonds?
        for i_agent, agent in enumerate(input_kappa.get_agents()):
            agent_name = agent.get_agent_name()
            agent_oper = agent.get_abundance_change_operation()
            agent_sign = agent.get_agent_signature()
            bond_sites = []
            flag_sites = []
            for i_site, site in enumerate(agent_sign):
                if type(site) is KappaPort:
                    site_name = site.get_port_name()
                    state_data = site.get_port_int_state()
                    state_oper = site.has_state_operation()
                    # assign to either the list of full-fledged sites, or to the flapole site
                    if site.has_bond_operation():
                        bond_sites.append([site_name, state_data, state_oper])
                    else:
                        flag_sites.append([state_data, state_oper])
                    # deal with bond (re)construction
                    old_bond = site.get_port_current_bond()
                    new_bond = site.get_port_future_bond()
                    if re.match('\d+', old_bond):
                        if old_bond in self._bonds_to_draw:
                            self._bonds_to_draw[old_bond]['agent_B'] = i_agent
                            self._bonds_to_draw[old_bond]['site_B'] = i_site
                        else:
                            self._bonds_to_draw[old_bond]['agent_A'] = i_agent
                            self._bonds_to_draw[old_bond]['site_A'] = i_site
                            self._bonds_to_draw[old_bond]['oper'] = site.get_port_bond_operation()
                    if re.match('\d+', new_bond):
                        if new_bond in self._bonds_to_draw:
                            self._bonds_to_draw[new_bond]['agent_B'] = i_agent
                            self._bonds_to_draw[new_bond]['site_B'] = i_site
                        else:
                            self._bonds_to_draw[new_bond]['agent_A'] = i_agent
                            self._bonds_to_draw[new_bond]['site_A'] = i_site
                            self._bonds_to_draw[new_bond]['oper'] = site.get_port_bond_operation()
                elif type(site) is KappaCounter:
                    site_name = site.get_counter_name()
                    state_data = site.get_counter_state()
                    state_oper = True if site.get_counter_delta() else False
                    flag_sites.append([site_name, state_data, state_oper])
                else:
                    raise TypeError('Signature must be composed of either KappaPort or KappaCounter; got <'
                                    + type(site) + '> instead for site <' + str(site) + '>')
            self._sites_to_draw.append([agent_name, agent_oper, bond_sites, flag_sites])

            self._bonds_to_draw