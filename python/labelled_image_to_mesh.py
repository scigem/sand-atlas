import os
import sys
import numpy
import skimage
import tqdm
import tifffile
import subprocess

# from stl import mesh

blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"  # Adjust this to your Blender installation
blender_script_path = os.path.expanduser(
    "~/code/sand-atlas/python/vdb.py"
)  # Adjust this to the path of your Blender script


def write_poly(vertices, faces, filename):
    # Save the mesh to a POLY file
    with open(filename, "w") as f:
        # Write the vertices
        f.write("POINTS\n")
        for i, vertex in enumerate(vertices):
            f.write(f"{i+1}: {vertex[0]} {vertex[1]} {vertex[2]}\n")

        # Write the faces
        f.write("POLYS\n")
        for i, face in enumerate(faces):
            f.write(f"{i+1}: {face[0]+1} {face[1]+1} {face[2]+1}\n")

        f.write("END")


filename = sys.argv[1]

debug = True

extension = filename.split(".")[-1]
if not os.path.exists(filename[: -len(extension) - 1]):
    os.mkdir(filename[: -len(extension) - 1])

for subfolder in ["npy", "stl_3", "stl_10", "stl_30", "stl_100", "stl_ORIGINAL", "vdb"]:
    if not os.path.exists(filename[: -len(extension) - 1] + f"/{subfolder}/"):
        os.mkdir(filename[: -len(extension) - 1] + f"/{subfolder}/")


print("Loading data... ", end="")

if (extension.lower() == "tif") or (extension.lower() == "tiff"):
    labelled_data = tifffile.memmap(filename)
elif extension.lower() == "raw":
    shape = tuple(numpy.array(filename.split("_")[-1][:-4].split("x"), dtype="int"))
    labelled_data = numpy.memmap(filename, shape=shape)
    # if debug:
    # tifffile.imwrite(filename[:-4] + ".tif", labelled_data.astype("uint16"))
elif extension.lower() == "npz":
    labelled_data = numpy.load(filename, allow_pickle=True)["arr_0"]
    if debug:
        # tifffile.imwrite(filename[:-4] + ".tif", labelled_data.astype("uint16"))
        import matplotlib.pyplot as plt

        plt.imshow(labelled_data[500, :, :])
        plt.colorbar()
        plt.show()


print("Done")

num_particles = numpy.amax(labelled_data)
print(f"Found {num_particles} labels")

props = skimage.measure.regionprops(labelled_data)
print("Calculated region properties")

# filter out small particles
j = 0
for i in tqdm.tqdm(range(1, num_particles)):
    if props[i].area > 100:
        j += 1

print(f"Only {j} particles are larger than 100 voxels")

nx, ny, nz = labelled_data.shape
j = 0

for i in tqdm.tqdm(range(1, num_particles)):
    if props[i].area > 100:
        # print(i, props[i].label)
        x_min, y_min, z_min, x_max, y_max, z_max = props[i].bbox

        if (
            x_min == 0
            or y_min == 0
            or z_min == 0
            or x_max == nx
            or y_max == ny
            or z_max == nz
        ):
            print(f"Particle {i} touching edge of the box, skipping")
        else:
            crop = labelled_data[x_min:x_max, y_min:y_max, z_min:z_max]

            this_particle = crop == props[i].label

            this_particle = numpy.pad(this_particle, 1, mode="constant")

            outname = filename[: -len(extension) - 1] + f"/npy/particle_{j:05}.npy"
            numpy.save(outname, this_particle)

            subprocess.run(
                [
                    blender_path,
                    "--background",
                    "--python",
                    blender_script_path,
                    "--",
                    outname,
                ]
            )

            j += 1
print(f"{j} out of {num_particles} particles saved to disk")
