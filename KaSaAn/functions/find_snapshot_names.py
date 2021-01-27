#! /usr/bin/env python3

import pathlib
import warnings
from typing import List
from .numerical_sort import numerical_sort


def find_snapshot_names(target_directory: str = '.', name_pattern: str = 'snap*.ka') -> List[str]:
    """Given a target directory (default <./>), and a snapshot naming scheme (default <snap*.ka>), return a list of
     snapshot names sorted ascendingly by a numerical specifier. By default, KaSim inserts the event number into a
     snapshot's name."""
    target_path = pathlib.Path(target_directory)
    if not target_path.exists():
        raise ValueError('Directory <' + target_directory + '> not found.')
    snap_names = [str(file_path) for file_path in target_path.glob(name_pattern)]
    if len(snap_names) < 2:
        warnings.warn('Found <{}> snapshots in directory <{}> using file naming pattern <{}>.'.format(
            len(snap_names), target_directory, name_pattern))
    sorted_names = sorted(snap_names, key=numerical_sort)
    return sorted_names
