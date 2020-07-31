#! /usr/bin/env python3

import re
from typing import List, Union


def numerical_sort(value: str) -> List[Union[float, str]]:
    """Helper function to sort strings by their numerical components. Supports decimal notation, and multiple numerical
     components per string. Returns a list of the string and numerical elements, where the numerical elements have been
     converted into floats. E.g.:

    >>> numerical_sort('bla/blo/snap_t.56.6,95.6,55.ka')
    ['bla/blo/snap_t.', 56.6, ',', 95.6, ',', 55.0, '.ka']
    """
    parts = re.compile(r'(\d+(?:\.\d+)?)').split(value)
    parts[1::2] = map(float, parts[1::2])
    return parts
