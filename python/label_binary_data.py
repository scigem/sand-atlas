import sys
import numpy
import tifffile
from skimage.measure import label, regionprops
from skimage.morphology import closing

cube = numpy.ones((5, 5, 5), dtype='uint8')

filename = sys.argv[1]
extension = filename.split('.')[-1]
outname = filename[:-len(extension)-1] + '_labelled'

print('Loading data...', end='')
if ( extension.lower() == 'tif' ) or ( extension.lower() == 'tiff'):
    data = tifffile.memmap(filename)
elif ( extension.lower() == 'raw' ):
    data = numpy.memmap(filename)
elif ( extension.lower() == 'npz' ):
    data = numpy.load(filename, allow_pickle=True)['arr_0']
print('Done')

print('Labelling data...', end='')
closed = closing(data, cube)

labelled = label(closed)
print('Done')

print(f'Saving data to {outname + ".npz"}')
numpy.savez_compressed(outname + '.npz', labelled)