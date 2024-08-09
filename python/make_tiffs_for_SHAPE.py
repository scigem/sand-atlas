import os
import sys
import glob
import numpy
import tqdm
import tifffile
import nrrd

foldername = sys.argv[1]
files = glob.glob(foldername + '/*.npz')
files.sort()

if not os.path.exists('SHAPE'):
    os.mkdir('SHAPE')

for i, file in tqdm.tqdm(enumerate(files)):
    data = numpy.load(file, allow_pickle=True)
    this_particle = data["volume"]
    tifffile.imwrite(f'SHAPE/particle_{i}.tiff', this_particle.astype('uint8'))
    # nrrd.write(f'SHAPE/particle_{i}.nrrd', this_particle.astype('uint8'))

