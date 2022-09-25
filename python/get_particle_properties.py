import sys
import glob
import numpy
import skimage
import tqdm

foldername = sys.argv[1]

files = glob.glob(foldername + '/*.npz')
files.sort()

for i in tqdm.tqdm(range(1, len(files[:2]))):
    data = numpy.load(files[i])
    vol = data['volume'].astype('uint8')

    regions = skimage.measure.regionprops(vol)
    for region in enumerate(regions):
        print(f'REGION {i}')
        for prop in region:
            print(prop, region[prop])
