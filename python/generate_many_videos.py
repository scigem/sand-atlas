import os
import sys
import glob

# Pass in a path to a labelled image stack
filename = sys.argv[1]

# Step 1: convert labelled image to a set of meshes
# os.system('python labelled_image_to_mesh.py ' + filename)

foldername = ''.join(filename.split('.')[:-1])
# Step 2: convert each mesh to a small video
files = glob.glob(foldername + '/*.npz')
for file in files:
    # os.system('/Applications/Blender.app/Contents/MacOS/Blender --background --python mesh_to_blender.py -- ' + file)
    os.system("ffmpeg -y -framerate 30 -pattern_type glob -i '" + file[:-4] +
              "/*.png' -c:v libx264 -pix_fmt yuv420p " + file[:-4] + ".mp4")

os.system("mv " + filename[:-4] + "/*.mp4 ../assets/videos/hostun-sand")
