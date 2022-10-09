import sys
import numpy
import matplotlib.pyplot as plt

filename = sys.argv[1]
data = numpy.load(filename, mmap_mode='r')['arr_0']

plt.imshow(data[:,:,100])
plt.show()