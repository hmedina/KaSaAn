#! python.exe
from kappa_snapshot_analysis import KappaSnapshot

# Use this code in the interactive python console to re-load the class definition
# import kappa_snapshot_analysis; from importlib import reload
# reload(kappa_snapshot_analysis); from kappa_snapshot_analysis import KappaSnapshot

# Read the file & create the inner representation of the snapshot
mySnap = KappaSnapshot('snap.ka')

# To display the expression of the first complex with abundance of 3
print(mySnap.get_complexes_with_abundance(3)[0].kappa_expression)

# To display the complex with the most elements & its size
print(mySnap.get_largest_complexes().kappa_expression)
print(mySnap.get_largest_complexes().get_size_of_complex())

# To display or plot the size distribution
print(mySnap.get_size_distribution())

import matplotlib.pyplot as plt
import numpy as np

t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2*np.pi*t)
plt.plot(t, s)

plt.xlabel('time (s)')
plt.ylabel('voltage (mV)')
plt.title('About as simple as it gets, folks')
plt.grid(True)
plt.savefig("test.png")
plt.show()