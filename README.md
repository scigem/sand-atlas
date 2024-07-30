# The Sand Atlas

**Important**: This repository contains only the material used to produce The Sand Atlas website. The actual particle data is located on a different server. On [the website](https://sand-atlas.scigem.com/) you can navigate to the page for the sand you are interested in and download the particle data from there.

[See it live here](https://sand-atlas.scigem.com/)

# Installation

## Website
If you would like to help us improve the Sand Atlas, you should:
1. Clone this repository
2. Install ruby if it is not already on your computer (https://www.ruby-lang.org/en/documentation/installation/).
3. In the terminal, inside the package folder run `bundle install`. This will install the requried packages so that we can build the website.
4. To run a local server to be able to see the Sand Atlas, run `bundle exec jekyll serve`. Open the browser to `http://localhost:4000/` to see the website.

## Processing pipeline
The scripts to convert a user submitted labelled `tiff` file are stored in the `python` folder. The master script, which calls the other scripts sequentially, is `generate_many_videos.py`. This can be run with `python generate_many_videos.py path_to_labelled_tiff name_of_sand`. This will produce meshes of all the files and videos of those meshes rotating. Each particle is tagged with a unique name. The names are pulled from a list of geolocated names stored in `names.json`. You can produce more names by asking ChatGPT to "Generate 1000 common surnames from the XXXXX region as a python list on one line using double quotes". This should be repeated for first names.

## User submissions
When someone wants to give us data, they start off with either a direct email or by filling out the web form on the homepage of the Sand Atlas. From there:
1. We send a [FileSender](https://filesender.aarnet.edu.au/) link to them requesting the upload of raw and labelled tiffs. We also ask for as much as possible of the following information:
    1. Title
    2. Short description
    3. Photo of the sand
    4. Latitude and longitude of source location
    5. Source data URL (if already hosted somewhere)
    6. Publication URL (if already published somewhere)
    7. Source license (if source data already licensed). If not previously licensed, we recommend [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
    8. Mineralogy
    9. Resolution (mm per voxel)
10. Once received, we download the tiffs
11. Convert labelled image to meshes
12. Use blender to render each mesh to a video
13. Host meshes and videos at https://data.scigem-eng.sydney.edu.au/
14. Put all of this information into the sand atlas (metadata in a json file at `_data/sands/`) and push to the repository to update the website.
