#! python.exe
import re



snap_file_name = 'snap.ka'
with open(snap_file_name, 'r') as kf:
    raw_complex_size = []
    raw_complex_num = []
    for line in kf:
        if (line[0] != '#') & (line != '\n'):
            ka_complex = re.search('%init:\s(\d+)\s(.+)', line)
    # Make sure we have both length & abundance of each complex
    assert len(raw_complex_size) == len(raw_complex_num)