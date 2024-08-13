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
    silence = ""
else:
    silence = " > /dev/null 2>&1"

# Pass in a path to a labelled image stack
filename = sys.argv[1]
sand_type = sys.argv[2]
foldername = "".join(filename.split(".")[:-1])

print("Rendering videos for IG...")
files = glob.glob(foldername + "/stl_ORIGINAL/*.stl")
files.sort()

if not os.path.exists("media"):
    os.makedirs("media")

for i, file in tqdm(enumerate(files), total=len(files)):
    if not os.path.exists(file[:-4] + ".mp4"):
        # Use blender to render an animation of this grain rotating
        os.system(
            "/Applications/Blender.app/Contents/MacOS/Blender --background -t 4 --python mesh_to_blender.py -- "
            + file
            + " 120 "  # 120 frames to make a 4 second video
            + " > /dev/null 2>&1"
        )
        # Use ffmpeg to convert the animation into a webm video
        os.system(
            "ffmpeg -y -framerate 30 -pattern_type glob -i '"
            + file[:-4]
            + "/*.png' "
            + "-c:v libvpx-vp9 "
            # + '-vf "drawtext=text='+ids[i]+f':x=(w-tw)/2:y=h-th-10:fontcolor=white:fontsize=72:fontfile={font}" '
            + file[:-4]
            + ".mp4"
            + silence
        )
        # Clean up the rendered images
        os.system("rm -rf " + file[:-4] + "/*.png")
        os.system(
            "mv "
            + file[:-4]
            + ".mp4 "
            + "media/"
            + sand_type
            + "-"
            + str(i).zfill(5)
            + ".mp4"
        )
        os.system("rmdir " + file[:-4])
