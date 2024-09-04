import sys
import numpy
import tifffile
import nrrd
from skimage.filters import threshold_otsu, gaussian

filename = sys.argv[1]
extension = filename.split('.')[-1]
outname = filename[:-len(extension)-1] + '_binary'

# blur = 3

print(f'Loading {filename}')

if ( extension.lower() == 'tif' ) or ( extension.lower() == 'tiff'):
    try:
        data = tifffile.memmap(filename)
    except:
        data = tifffile.imread(filename)
elif ( extension.lower() == 'raw' ):
    data = numpy.memmap(filename)
elif ( extension.lower() == 'nrrd' ):
    data, header = nrrd.read(filename)

if len(sys.argv) > 2:
    threshold = int(sys.argv[2])
else:
    print('Using Otsu thresholding...')
    threshold = threshold_otsu(data)

# print('Adding blur...')
# if blur:
#     data = skimage.filters.gaussian(data, sigma=blur)

print(f'Thresholding at {threshold}')
binary = data > threshold

print(f'Saving data')
# numpy.savez_compressed(outname + '_compressed.npz', binary)
tifffile.imwrite(outname + '.tif', binary)#, compression='zlib')
# numpy.save(outname + '.npy', binary)