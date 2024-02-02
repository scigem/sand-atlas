import os
import sys
import numpy
import skimage
import tqdm
import tifffile
from stl import mesh

def write_poly(vertices, faces, filename):
    # Save the mesh to a POLY file
    with open(filename, 'w') as f:
        # Write the vertices
        f.write('POINTS\n')
        for i, vertex in enumerate(vertices):
            f.write(f'{i+1}: {vertex[0]} {vertex[1]} {vertex[2]}\n')

        # Write the faces
        f.write('POLYS\n')
        for i, face in enumerate(faces):
            f.write(f'{i+1}: {face[0]+1} {face[1]+1} {face[2]+1}\n')

        f.write('END')

filename = sys.argv[1]

make_stl = False
make_poly = True

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

# filter out small particles
j = 0
for i in tqdm.tqdm(range(1, num_particles)):
    if props[i].area > 100:
        j += 1

print(f'Only {j} particles are larger than 100 voxels')

nx, ny, nz = labelled_data.shape
j = 0

for i in tqdm.tqdm(range(1, num_particles)):
    if props[i].area > 100:
        # print(i, props[i].label)
        x_min, y_min, z_min, x_max, y_max, z_max = props[i].bbox

        if x_min == 0 or y_min == 0 or z_min == 0 or x_max == nx or y_max == ny or z_max == nz:
            print(f'Particle {i} touching edge of the box, skipping')
        else:
            crop = labelled_data[x_min:x_max, y_min:y_max, z_min:z_max]

            this_particle = crop == props[i].label

            this_particle = numpy.pad(this_particle, 1, mode='constant')

            # tifffile.imwrite(f'particle_{i}.tiff', this_particle.astype('uint8'))

            # now get meshed surface
            vertices, faces, normals, values = skimage.measure.marching_cubes(
                this_particle, level=0.5)

            # make an STL file
            if make_stl:
                mesh_data = mesh.Mesh(numpy.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
                for id, f in enumerate(faces):
                    for k in range(3):
                        mesh_data.vectors[id][k] = vertices[f[k]]

                if not os.path.exists(filename[:-len(extension)-1] + f'/stl/'):
                    os.mkdir(filename[:-len(extension)-1] + f'/stl/')
                stlname = filename[:-len(extension)-1] + f'/stl/particle_{j:05}.stl'
                mesh_data.save(stlname)

            if make_poly:
                if not os.path.exists(filename[:-len(extension)-1] + f'/poly/'):
                    os.mkdir(filename[:-len(extension)-1] + f'/poly/')
                polyname = filename[:-len(extension)-1] + f'/poly/particle_{j:05}.poly'
                write_poly(vertices, faces, polyname)                

            # save everything to hard disk for this particle
            outname = filename[:-len(extension)-1] + f'/particle_{j:05}.npz'
            numpy.savez(outname, vertices=vertices,
                        faces=faces, volume=this_particle)

            j += 1
print(f'{j} out of {num_particles} particles saved to disk')
