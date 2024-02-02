import sys
import glob
import numpy
import skimage
import tqdm


def jsonlike_print(name, arr):
    print('"' + name + '": "', end='')
    if isinstance(arr, int):
        print(arr, end='')
    elif isinstance(arr, float):
        print(arr, end='')
    elif isinstance(arr, numpy.ndarray):
        print(*arr.tolist(), sep=',', end='')
    print('",')


foldername = sys.argv[1]
pixel_size = float(sys.argv[2])  # mm per pixel

files = glob.glob(foldername + '/*.npz')
files.sort()

areas = numpy.zeros(len(files)-1)
eq_diams = numpy.zeros_like(areas)
axis_major_lengths = numpy.zeros_like(areas)
axis_minor_lengths = numpy.zeros_like(areas)

for i in tqdm.tqdm(range(1, len(files))):  # ASSUMING FIRST REGION IS THE BOUNDARY
    data = numpy.load(files[i])
    vol = data['volume'].astype('uint8')

    regions = skimage.measure.regionprops(vol,spacing=(pixel_size, pixel_size, pixel_size))
    # print(len(regions))
    # there should really only be one region...
#     for j, region in enumerate(regions):
    # print(f'REGION {j}')
    areas[i-1] = regions[0]['area']
    eq_diams[i-1] = regions[0]['equivalent_diameter_area']
    axis_major_lengths[i-1] = regions[0]['axis_major_length']
    axis_minor_lengths[i-1] = regions[0]['axis_minor_length']

jsonlike_print('number_of_particles', len(areas))
jsonlike_print('mm_per_pixel', pixel_size)
jsonlike_print('area', areas)
jsonlike_print('equivalent_diameter', eq_diams)
jsonlike_print('axis_major_length', axis_major_lengths)
jsonlike_print('axis_minor_length', axis_minor_lengths)
jsonlike_print('aspect_ratio', axis_major_lengths/axis_minor_lengths)
