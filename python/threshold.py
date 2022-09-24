import sys
import numpy
import tifffile
from skimage.filters import threshold_otsu

filename = sys.argv[1]
extension = filename.split('.')[-1]
outname = filename[:-len(extension)-1] + '_binary'

print(filename)

if ( extension.lower() == 'tif' ) or ( extension.lower() == 'tiff'):
    data = tifffile.memmap(filename)
elif ( extension.lower() == 'raw' ):
    data = numpy.memmap(filename)

if len(sys.argv) > 2:
    threshold = int(sys.argv[2])
else:
    threshold = threshold_otsu(data)

binary = data > threshold

numpy.savez_compressed(outname + '_compressed.npz', binary)
# tifffile.imwrite(outname + '.tif', binary)
# numpy.save(outname + '.npy', binary)