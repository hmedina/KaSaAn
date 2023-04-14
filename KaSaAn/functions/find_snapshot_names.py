#! /usr/bin/env python3

from pathlib import Path
from typing import List, Union
from .numerical_sort import numerical_sort
import warnings


def find_snapshot_names(target_directory: Union[str, Path] = '.', name_pattern: str = 'snap*.ka') -> List[str]:
    """Given a target directory (default `./`), and a snapshot naming scheme (default `snap*.ka`), return a list of
     snapshot names sorted ascending by a numerical specifier. By default, KaSim inserts the event number into a
     snapshot's name."""
    if isinstance(target_directory, Path):
        target_path = target_directory
    elif isinstance(target_directory, str):
        target_path = Path(target_directory)
    else:
        raise ValueError(
            'Expected a string or a Pathlib.Path object for parameter "target_directory", got {}'.format(
                type(target_directory)))
    if not target_path.exists():
        raise ValueError('Directory {} not found'.format(target_directory))
    snap_names = [str(file_path) for file_path in target_path.glob(name_pattern)]
    if len(snap_names) < 2:
        warnings.warn('Found <{}> snapshots in directory <{}> using file naming pattern <{}>.'.format(
            len(snap_names), target_directory, name_pattern))
    sorted_names = sorted(snap_names, key=numerical_sort)
    return sorted_names
