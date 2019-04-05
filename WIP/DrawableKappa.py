#!/usr/bin/env python3

from typing import List
from KaSaAn.core import KappaRule


class DrawableRule:
    def __init__(self, input_rule: KappaRule):
        # [agent name, [site name, bond data, bond operation, [state data, state operation]]]
        self._rule_elements: List[str, List[str, str, str, List[str, bool]]]

        # [index in master list, draw location, [index in site list, draw location]]
        self._agent_mapping: List[int, int, List[int, int]]

        # [1st agent id, 1st agent site id, 2nd agent id, 2nd agent site id, status / color to draw]
        self._drawing_splines: List[float, float, float, float, str]

        # [1st agent id, ]
        self._drawing_wedges: List[]

        #
        self._drawing_annotations: List[]