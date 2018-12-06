#! /usr/bin/python3

from KaSaAn import KappaSnapshot

# Use this code in the interactive python console to re-load the class definition
# import kappa4_snapshot_analysis; from importlib import reload
# reload(kappa4_snapshot_analysis); from kappa4_snapshot_analysis import *

print('This is a demo showing some of the analysis one can do on a Kappa snapshot.')

# Read the file & create the inner representation of the snapshot
print('First, we read the file:')
print(">>> mySnap = KappaSnapshot('./models/cyclic_polyvalent_polymers_snap.ka')")
mySnap = KappaSnapshot('./models/linear_polymer_snap.ka')

# To display the expression of the first complex with abundance of 3
print('\nThe expression of the first complex with abundance of 3 can be obtained by:')
print(">>> mySnap.get_complexes_with_abundance(3)[0].kappa_expression")
print(mySnap.get_complexes_with_abundance(3)[0].kappa_expression)

# To display all the complexes with the maximum number of elements & their size
print('\nThe largest complexes & their size can be obtained with:')
print(">>> [[item.kappa_expression, item.get_size_of_complex()] for item in list(mySnap.get_largest_complexes())]")
print([[item.kappa_expression, item.get_size_of_complex()] for item in list(mySnap.get_largest_complexes())])

# To display all the complexes with the least number of elements & their size
print('\nThe smallest complexes & their size can be obtained with:')
print(">>> [[item.kappa_expression, item.get_size_of_complex()] for item in list(mySnap.get_smallest_complexes())]")
print([[item.kappa_expression, item.get_size_of_complex()] for item in list(mySnap.get_smallest_complexes())])

# To display the size distribution, and plot the mass distribution
print('\nTo get the size distribution of complexes:')
print(">>> mySnap.get_size_distribution()")
print(mySnap.get_size_distribution())
