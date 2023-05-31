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

print('Loading data... ', end='')

if (extension.lower() == 'tif') or (extension.lower() == 'tiff'):
    labelled_data = tifffile.memmap(filename)
elif (extension.lower() == 'raw'):
    shape = tuple(numpy.array(filename.split(
        '_')[-1][:-4].split('x'), dtype='int'))
    labelled_data = numpy.memmap(filename, shape=shape)
elif ( extension.lower() == 'npz' ):
    labelled_data = numpy.load(filename, allow_pickle=True)['arr_0']

print('Done')

num_particles = numpy.amax(labelled_data)
print(f'Found {num_particles} labels')

props = skimage.measure.regionprops(labelled_data)
print('Calculated region properties')

nx, ny, nz = labelled_data.shape
j = 0

for i in tqdm.tqdm(range(1, num_particles)):
    # print(i, props[i].label)
    x_min, y_min, z_min, x_max, y_max, z_max = props[i].bbox

    if x_min == 0 or y_min == 0 or z_min == 0 or x_max == nx or y_max == ny or z_max == nz:
        print(f'Particle {i} touching edge of the box, skipping')
    else:
        crop = labelled_data[x_min:x_max, y_min:y_max, z_min:z_max]

        this_particle = crop == props[i].label

        # tifffile.imwrite(f'particle_{i}.tiff', this_particle.astype('uint8'))

        # now get meshed surface
        vertices, faces, normals, values = skimage.measure.marching_cubes(
            this_particle, level=0.95)

        # save everything to hard disk for this particle
        outname = filename[:-len(extension)-1] + f'/particle_{j:03}.npz'
        numpy.savez(outname, vertices=vertices,
                    faces=faces, volume=this_particle)

        j += 1
print(f'{j} out of {num_particles} particles saved to disk')
