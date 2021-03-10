#!/usr/bin/env python3
from setuptools import setup

setup(
    entry_points={
        'console_scripts': [
            'kappa_catalytic_potential = KaSaAn.scripts.catalytic_potential:main',
            'kappa_observable_plotter = KaSaAn.scripts.observable_plotter:main',
            'kappa_observable_coplotter = KaSaAn.scripts.observable_coplotter:main',
            'kappa_snapshot_largest_complex_time = KaSaAn.scripts.graph_largest_complex_composition:main',
            'kappa_snapshot_visualizer_patchwork = KaSaAn.scripts.snapshot_visualizer_patchwork:main',
            'kappa_snapshot_visualizer_network = KaSaAn.scripts.snapshot_visualizer_network:main',
            'kappa_snapshot_visualizer_subcomponent = KaSaAn.scripts.snapshot_visualizer_subcomponent:main',
            'kappa_trace_movie_maker = KaSaAn.scripts.trace_movie_maker:main',
        ]
    }
)
