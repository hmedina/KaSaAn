#! /usr/bin/env python3

import re


def numerical_sort(value):
    parts = re.compile(r'(\d+)').split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts
