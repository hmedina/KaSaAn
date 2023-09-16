#! /usr/bin/env python3

import matplotlib.pyplot as plt
from KaSaAn.core import KappaContactMap

my_contact_map = KappaContactMap('inputs.ka')
fig, ax = plt.subplots(figsize=(6, 6))

my_contact_map.move_agent_to('Fitz', 10, 10)
my_contact_map.move_agent_to('Foo', 20, 30)
my_contact_map.move_agent_to('Bar', 25, 5)
my_contact_map.move_agent_to('Baz', 0, 25)

my_contact_map.rotate_all_sites_of('Foo', 190)
my_contact_map.rotate_all_sites_of('Baz', -180)
my_contact_map.rotate_all_sites_of('Fitz', 30)
my_contact_map.rotate_all_sites_of('Bar', -10)

my_contact_map.draw(ax, draw_state_flagpole=True)
ax.axis('off')
plt.tight_layout()

fig.savefig('contact_map.png')
plt.show()
