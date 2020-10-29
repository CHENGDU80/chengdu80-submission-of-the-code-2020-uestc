import sys
import pickle

name = sys.argv[1]

with open(name, 'rb') as f:
    d = pickle.load(f)
print(d)
