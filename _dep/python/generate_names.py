import sys
import json
import numpy as np

def jsonlike_print(name, arr):
    print('"' + name + '": "', end='')
    # print(*arr, sep=',', end='')
    print(arr)
    print('"')

with open('names.json', 'r') as f: names = json.load(f)

region = sys.argv[1]
num = int(sys.argv[2])
local_names = names[region]

names = []
for i in range(num):
    if np.random.rand() < 0.5:
        names.append(
            local_names['male'][np.random.randint(len(local_names['male']))] + ' ' + local_names['surname'][np.random.randint(len(local_names['surname']))]
            )
    else:
        names.append(
            local_names['female'][np.random.randint(len(local_names['female']))] + ' ' + local_names['surname'][np.random.randint(len(local_names['surname']))]
        )
# print(names)
jsonlike_print('id', names)
