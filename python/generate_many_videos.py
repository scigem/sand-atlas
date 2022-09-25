import os
import sys
import glob

# Pass in a path to a labelled image stack
filename = sys.argv[1]
sand_type = sys.argv[2]
foldername = ''.join(filename.split('.')[:-1])

# Step 1: convert labelled image to a set of meshes
os.system('python labelled_image_to_mesh.py ' + filename)

# Step 2: convert each mesh to a video
files = glob.glob(foldername + '/*.npz')
files.sort()

for file in files:
    # Use blender to render an animation of this grain rotating
    os.system('/Applications/Blender.app/Contents/MacOS/Blender --background --python mesh_to_blender.py -- ' + file)
    # Use ffmpeg to convert the animation into a webm video
    os.system("ffmpeg -y -framerate 30 -pattern_type glob -i '" + file[:-4] +
              "/*.png' -c:v libvpx-vp9 " + file[:-4] + ".webm")

# Step 3: Stitch videos together into a grid
files = glob.glob(foldername + '/*.webm')
files.sort()
num_particles = len(files)
num_grids = num_particles//12  # discard any extras

for i in range(num_grids):
    # Make a 4x3 grid
    os.system(f'ffmpeg -i {files[i+0]} -i {files[i+1]} -i {files[i+2]} -i {files[i+3]} -i {files[i+4]} -i {files[i+5]} -i {files[i+6]} -i {files[i+7]} -i {files[i+8]} -i {files[i+9]} -i {files[i+10]} -i {files[i+11]} -filter_complex "[0:v][1:v][2:v][3:v][4:v][5:v][6:v][7:v][8:v][9:v][10:v][11:v]xstack=inputs=12:layout=0_0|w0_0|w0+w1_0|w0+w1+w2_0|0_h0|w4_h0|w4+w5_h0|w4+w5+w6_h0|0_h0+h4|w8_h0+h4|w8+w9_h0+h4|w8+w9+w10_h0+h4" grid_{i}.webm')

# Now concatenate the grids together temporally
with open('sources.txt', 'w') as f:
    for i in range(num_grids):
        f.write(f'file grid_{i}.webm\n')
os.system("ffmpeg -f concat -safe 0 -i sources.txt -c copy all_particles.webm")

# Step 4: Cleanup
os.system("rm grid_*.webm")
os.system(f"mv all_particles.webm ~/code/sand-atlas/assets/sands/{sand_type}/")
