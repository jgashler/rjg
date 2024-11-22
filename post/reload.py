from importlib import reload
import sys

l = sys.modules.keys()

rrr = []

for j in l:
    if 'rjg' in j:
        rrr.append(j)
        
for r in rrr:
    reload(r)