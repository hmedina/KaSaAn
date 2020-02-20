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
            'kappa_catalytic_potential = KaSaAn.scripts.catalytic_potential:main',
            'kappa_observable_plotter = KaSaAn.scripts.observable_plotter:main',
            'kappa_observable_coplotter = KaSaAn.scripts.observable_coplotter:main',
            'kappa_snapshot_visualizer_patchwork = KaSaAn.scripts.snapshot_visualizer_patchwork:main',
            'kappa_snapshot_visualizer_network = KaSaAn.scripts.snapshot_visualizer_network:main',
            'kappa_trace_movie_maker = KaSaAn.scripts.trace_movie_maker:main',
        ]
    }
)
