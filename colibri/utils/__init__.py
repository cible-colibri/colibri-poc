import os

from pkg_resources import resource_filename

# We define the paths for the various data folders
data_path = {'weather': resource_filename('colibri', os.path.join('data', 'weather'))}