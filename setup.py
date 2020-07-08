#!/usr/bin/env python3
from setuptools import setup

"""This package provides tools for analyzing Kappa entities, notably snapshots, and visualizing snapshots and rules."""

setup(
    name='KaSaAn',
    version='0.1.dev0',
    packages=['KaSaAn'],
    package_dir={'': '.'},
    url='https://github.com/hmedina/KaSaAn',
    license='MIT',
    author='Hector Medina',
    author_email='hector.f.medina.a@gmail.com',
    description='Kappa snapshot analysis & WIP tools.',
    long_description=__doc__,
    extras_require={
        'MPL': ['matplotlib>=3.0.2<3.0.3'],
        'sqr': ['squarify>=0.3.0<0.5.0'],
    },
    entry_points={
        'console_scripts': [
            'prefixed_snapshot_analyzer = KaSaAn.scripts.prefixed_snapshot_analyzer:main',
            'plot_filtered_distributions = KaSaAn.scripts.plot_filtered_distributions:main [MPL,sqr]',
            'catalytic_potential_of_folder = KaSaAn.scripts.catalytic_potential:main',
            'snapshot_visualizer = KaSaAn.scripts.snapshot_visualizer:main [MPL,sqr]',
            'trace_movie_maker = KaSaAn.scripts.trace_movie_maker:main [MPL,sqr]'
        ]
    },
    test_suite='unittests'
)
