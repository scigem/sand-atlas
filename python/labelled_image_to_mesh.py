import os
import sys
import numpy
import skimage
import tqdm
import tifffile

filename = sys.argv[1]
extension = filename.split('.')[-1]
if not os.path.exists(filename[:-len(extension)-1]):
    os.mkdir(filename[:-len(extension)-1])

if (extension.lower() == 'tif') or (extension.lower() == 'tiff'):
    labelled_data = tifffile.memmap(filename)
elif (extension.lower() == 'raw'):
    shape = tuple(numpy.array(filename.split(
        '_')[-1][:-4].split('x'), dtype='int'))
    labelled_data = numpy.memmap(filename, shape=shape)

print('Loaded data')

num_particles = numpy.amax(labelled_data)
print(f'Found {num_particles} labels')

props = skimage.measure.regionprops(labelled_data)
print('Calculated region properties')

for i in tqdm.tqdm(range(1, num_particles)):
    # print(i, props[i].label)
    x_min, y_min, z_min, x_max, y_max, z_max = props[i].bbox
    crop = labelled_data[x_min:x_max, y_min:y_max, z_min:z_max]
    # import matplotlib.pyplot as plt
    # plt.hist(crop.flatten(), bins=[-0.5, 0.5, 1.5, 2.5,
    #          3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5])
    # plt.show()

    this_particle = crop == props[i].label

    # tifffile.imwrite(f'particle_{i}.tiff', this_particle.astype('uint8'))

    # now get meshed surface
    # try:
    vertices, faces, normals, values = skimage.measure.marching_cubes(
        this_particle, level=0.95)
    # except RuntimeError:
    #     print(f'Failed to get mesh for particle {i}')
    #     vertices = []
    #     faces = []
    # save everything to hard disk for this particle
    outname = filename[:-len(extension)-1] + f'/particle_{i}.npz'
    numpy.savez(outname, vertices=vertices, faces=faces, volume=this_particle)
