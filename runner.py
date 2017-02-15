#! python.exe
import kappa_snapshot_analysis
from importlib import reload
reload(kappa_snapshot_analysis); from kappa_snapshot_analysis import KappaSnapshot

# Read the file & create the inner representation of the snapshot
mySnap = KappaSnapshot('snap.ka')

# To display the expression of the first complex with abundance of 1
print(mySnap.get_complexes_with_abundance(1)[0].kappa_expression)

# To display the complex with the most elements & its size
print(mySnap.get_largest_complex().kappa_expression)
print(mySnap.get_largest_complex().get_size_of_complex())
