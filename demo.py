#! /usr/bin/python3
from kappa_snapshot_analysis import KappaSnapshot

# Use this code in the interactive python console to re-load the class definition
# import kappa_snapshot_analysis; from importlib import reload
# reload(kappa_snapshot_analysis); from kappa_snapshot_analysis import *

# Read the file & create the inner representation of the snapshot
mySnap = KappaSnapshot('models/10.ka')
mySnap.plot_mass_distribution()

# To display the expression of the first complex with abundance of 3
print('The expression of the first complex with abundance of 3:')
print(mySnap.get_complexes_with_abundance(3)[0].kappa_expression)

# To display all the complexes with the maximum number of elements & their size
print('All the complexes with the maximum number of elements & their size:')
print([[item.kappa_expression, item.get_size_of_complex()] for item in list(mySnap.get_largest_complexes())])

# To display all the complexes with the least number of elements & their size
print('All the complexes with the least number of elements & their size:')
print([[item.kappa_expression, item.get_size_of_complex()] for item in list(mySnap.get_smallest_complexes())])

# To display the size distribution, and plot the mass distribution
print('Size distribution of complexes:')
print(mySnap.get_size_distribution())
mySnap.plot_mass_distribution()
