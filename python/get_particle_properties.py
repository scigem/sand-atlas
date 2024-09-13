import sys
import os
import numpy
import skimage
import tifffile, nrrd
import pandas as pd
import json

labelled_filename = sys.argv[1] # path to labelled image
raw_filename = sys.argv[2] # path to raw image
json_file = sys.argv[3] # path to json file

with open(json_file) as f:
    json_data = json.load(f)
    pixel_size = float(json_data["microns_per_pixel"])*1e-6

sand_type = json_file.split('/')[-1].split('.')[0]
outfolder = '/'.join(json_file.split('/')[:-3]) + '/assets/sands/' + sand_type + '/'
if not os.path.exists(outfolder):
    os.makedirs(outfolder)
outname = outfolder + 'summary.csv'

d = []
for filename in [labelled_filename, raw_filename]:
    extension = filename.split('.')[-1]

    if ( extension.lower() == 'tif' ) or ( extension.lower() == 'tiff'):
        try:
            data = tifffile.memmap(filename)
        except:
            data = tifffile.imread(filename)
    elif ( extension.lower() == 'raw' ):
        # only used for Max's data
        data = numpy.memmap(filename, dtype='uint16', mode='r', shape=(1651,1651,1651))
    elif ( extension.lower() == 'npz' ):
        data = numpy.load(filename, allow_pickle=True)['arr_0']
    elif ( extension.lower() == 'nrrd' ):
        data, header = nrrd.read(filename)
    d.append(data)

# d[0] = d[0][::8,::8,::8]
# d[1] = d[1][::8,::8,::8]

props = skimage.measure.regionprops_table(d[0],intensity_image=d[1],spacing=(pixel_size, pixel_size, pixel_size), properties=('area','equivalent_diameter','major_axis_length','minor_axis_length'))
df = pd.DataFrame(props)
df = df.drop(index=0) # drop the background
df['aspect_ratio'] = df['major_axis_length']/df['minor_axis_length']

def beautify_column_names(df):
    df.columns = df.columns.str.replace('_', ' ').str.title()
    return df

df = beautify_column_names(df)

print(f'Saving data to {outname}')
df.to_csv(outname, index_label='Particle ID')