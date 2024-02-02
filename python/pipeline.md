# User submission of labelled data
1. User sends us an enquiry
2. We send cloudstor link to upload tiffs
3. We download tiffs
4. Create JSON file with name `{your_material}-sand.json`:
  - Get number of particles from labelled tiff and put into JSON file.
  - Get names with a ChatGPT request something like: "Generate 1000 common Canadian mens names from the Ottawa region as a python list on one line using double quotes". Repeat for female names and surnames. Copy these into `names.json` file.
  - Run `generate_names.py` and copy across to JSON file
  - Run `generate_many_videos.py` to compile the videos, make the meshes and do the particle shape analysis.
  - Copy shape analysis data into JSON file.
  - Move `all_particles.webm` video to appropriate place in `PRJ-SciGEMData` folder on RDS. Also zip the meshes and move them to the same place. Put these paths into JSON file. Optionally also upload the source data and put the path in the JSON file, or point towards an existing version online.
  - Run `get_particle_properties.py` and move the data to the JSON file.
5. Check everything works locally by running `bundle exec jekyll serve` and navigating to the page.
6. Once everything looks good, run `git add {path_to_your_json_file}.json`, then `git commit -am "Added {your_material} sand"` and `git push` to push to GitHub.

# User submission of unlabelled data --- NOT SUPPORTED
1. User sends us an enquiry
2. We send cloudstor link to upload tiffs
3. We download tiffs
4. Convert tiffs to hdf5
5. ilastik for segmentation
6. labelled image to mesh
7. meshes to blender