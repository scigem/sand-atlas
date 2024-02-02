import os
import sys
import glob
import json
import numpy
import matplotlib.image
from tqdm import tqdm

font = os.path.expanduser("~/Library/Fonts/Montserrat-Medium.ttf")
# debug = True
debug = False
if debug:
    silence = ''
else:
    silence = ' > /dev/null 2>&1'

# Pass in a path to a labelled image stack
filename = sys.argv[1]
sand_type = sys.argv[2]
foldername = ''.join(filename.split('.')[:-1])

if not os.path.exists('blank.webm'):
    matplotlib.image.imsave('blank.png', numpy.zeros((1000, 1000, 4)))
    os.system("ffmpeg -y -loop 1 -i blank.png -c:v libvpx-vp9 -t 2 blank.webm" + silence)

# Step 1: convert labelled image to a set of meshes
print('Converting labelled image to meshes...')
if os.path.exists(foldername + '/particle_00000.npz'):
    print('    Meshes already exist, skipping step 1')
else:
    os.system('python labelled_image_to_mesh.py ' + filename)

# Step 2: Render each grain using blender, then convert to a video with ffmpeg
print('Rendering videos...')
files = glob.glob(foldername + '/*.npz')
files.sort()

with open(f'../_data/sands/{sand_type}-sand.json') as f: json_data = json.load(f)
ids = json_data['id'].replace("'",'').split(', ')

for i,file in tqdm(enumerate(files), total=len(files)):
    if not os.path.exists(file[:-4] + ".webm"):
        # Use blender to render an animation of this grain rotating
        os.system('/Applications/Blender.app/Contents/MacOS/Blender --background -t 4 --python mesh_to_blender.py -- ' + file + " > /dev/null 2>&1")
        # Use ffmpeg to convert the animation into a webm video
        os.system("ffmpeg -y -framerate 30 -pattern_type glob -i '" + file[:-4] + "/*.png' " +  '-c:v libvpx-vp9 ' +
                '-vf "drawtext=text='+ids[i]+f':x=(w-tw)/2:y=h-th-10:fontcolor=white:fontsize=72:fontfile={font}" ' +
                file[:-4] + ".webm" + silence)
        # Clean up the rendered images
        os.system('rm -rf ' + file[:-4] + '/*.png')
        os.system('rmdir ' + file[:-4])

# Step 3: Stitch videos together into a grid
print('Stitching videos together...')
files = glob.glob(foldername + '/*.webm')
files.sort()
num_particles = len(files)
num_grids = int(numpy.ceil(num_particles/12))  # round
for i in range(num_particles, num_grids*12): # pad with blank videos
    files.append('blank.webm')

print(f'    Making {num_grids} grids')
for i in range(num_grids):
    # Make a 4x3 grid
    if not os.path.exists(f'grid_{i}.webm'):
        # print(f'ffmpeg -y -i {files[i*12+0]} -i {files[i*12+1]} -i {files[i*12+ 2]} -i {files[i*12+ 3]} ' +
        #         f'-i {files[i*12+4]} -i {files[i*12+5]} -i {files[i*12+ 6]} -i {files[i*12+ 7]} ' + 
        #         f'-i {files[i*12+8]} -i {files[i*12+9]} -i {files[i*12+10]} -i {files[i*12+11]} ' +
        #         f'-filter_complex "[0:v][1:v][2:v][3:v][4:v][5:v][6:v][7:v][8:v][9:v][10:v][11:v]xstack=inputs=12:layout=0_0|w0_0|w0+w1_0|w0+w1+w2_0|0_h0|w4_h0|w4+w5_h0|w4+w5+w6_h0|0_h0+h4|w8_h0+h4|w8+w9_h0+h4|w8+w9+w10_h0+h4" ' +
        #         f'grid_{i}.webm' + silence)
        os.system(f'ffmpeg -y -i {files[i*12+0]} -i {files[i*12+1]} -i {files[i*12+ 2]} -i {files[i*12+ 3]} ' +
                f'-i {files[i*12+4]} -i {files[i*12+5]} -i {files[i*12+ 6]} -i {files[i*12+ 7]} ' + 
                f'-i {files[i*12+8]} -i {files[i*12+9]} -i {files[i*12+10]} -i {files[i*12+11]} ' +
                f'-filter_complex "[0:v][1:v][2:v][3:v][4:v][5:v][6:v][7:v][8:v][9:v][10:v][11:v]xstack=inputs=12:layout=0_0|w0_0|w0+w1_0|w0+w1+w2_0|0_h0|w4_h0|w4+w5_h0|w4+w5+w6_h0|0_h0+h4|w8_h0+h4|w8+w9_h0+h4|w8+w9+w10_h0+h4" ' +
                f'grid_{i}.webm' + silence)

# Now concatenate the grids together temporally
print('    Concatenating grids together...')
with open('sources.txt', 'w') as f:
    for i in range(num_grids):
        f.write(f'file grid_{i}.webm\n')
os.system("ffmpeg -y -f concat -safe 0 -i sources.txt -c copy all_particles.webm" + silence)

# Step 4: Cleanup
print('Cleaning up...')
if not debug: os.system("rm grid_*.webm")
# # Reduce file size if necessary
# # os.system("ffmpeg -i all_particles.webm -crf 28 all_particles_smaller.mp4")
os.system("ffmpeg -y -i all_particles.webm -crf 45 all_particles_smaller.webm" + silence)
# os.system(
#     f"mv all_particles_smaller.webm ~/code/sand-atlas/assets/sands/{sand_type}-sand/all_particles.webm")
