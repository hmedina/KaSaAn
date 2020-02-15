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
    install_requires=[
        'matplotlib>=3.0.2<3.1.2',
        'numpy>=1.16<1.17',
        'squarify>=0.3.0<0.5.0',
        'networkx>=2.4<2.5',
    ],
    python_requires='==3.7',
    entry_points={
        'console_scripts': [
            'catalytic_potential_of_folder = KaSaAn.scripts.catalytic_potential:main',
            'kappa_trace_plotter = KaSaAn.scripts.kappa_trace_plotter:main',
            'kappa_trace_coplotter = KaSaAn.scripts.kappa_trace_coplotter:main',
            'plot_filtered_distributions = KaSaAn.scripts.plot_filtered_distributions:main',
            'prefixed_snapshot_analyzer = KaSaAn.scripts.prefixed_snapshot_analyzer:main',
            'snapshot_visualizer = KaSaAn.scripts.snapshot_visualizer:main',
            'trace_movie_maker = KaSaAn.scripts.trace_movie_maker:main',
        ]
    }
)
