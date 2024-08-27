from colibri.core.project import Project
from colibri.data.backbone.config_test import config
import colibri.datamodel.schemes.node_schemes
from colibri.datamodel.schemes.object_schemes import boundary_scheme, root_scheme

import json
import os

def test_generate_schemes():

    schemes_to_update = [
        {
        'path': 'node_schemes.py',
        'content':
            [{
                'template': colibri.datamodel.schemes.node_schemes.space_scheme,
                'config_key': 'Spaces',
                'scheme_names': ['space_scheme', 'ponctual_junction_scheme', 'linear_junction_scheme']
            }]
        },
        {
            'path': 'object_schemes.py',
            'content': [{
                'template': colibri.datamodel.schemes.object_schemes.boundary_scheme,
                'config_key': 'Boundaries',
                'scheme_names': ['root_scheme', 'boundary_scheme']
            }]
        }
    ]

    generate_schemes(schemes_to_update)

    pass

def generate_schemes(schemes_to_update):
    project = Project("pfc")
    scheme_from_config = project.scheme_from_config(config)

    for scheme_to_update in schemes_to_update:
        for content in scheme_to_update['content']:
            scheme_template = content['template']
            config_key = content['config_key']
            mode = "w"
            for scheme_name in content['scheme_names']:
                scheme_template['parameters'] = scheme_from_config[config_key]
                dump_scheme(scheme_to_update['path'], scheme_name, scheme_template,mode)
                mode = "a"
            if config_key in scheme_from_config:
                del scheme_from_config[config_key]

    # schemes for models
    for cls, scheme in scheme_from_config.items():
        scheme_name = cls.replace("<class '",'').replace("'>",'_scheme').replace('.', '_')
        dump_scheme("object_schemes.py", scheme_name, scheme, "a")
    pass

def dump_scheme(file_name, scheme_name, scheme, mode="w"):
    generated_schemes_path = os.path.join('generated', file_name)
    with open(generated_schemes_path, mode) as text_file:
        text_file.write(scheme_name + " = ")
        text_file.write(json.dumps(scheme, indent=4).replace('null', 'None'))
        text_file.write("\n")

# generate schemes one-by-one
# # node schemes
# scheme = colibri.datamodel.schemes.node_schemes.space_scheme
# scheme['parameters'] = scheme_from_config['Spaces']
# dump_scheme('node_schemes.py', 'space_scheme', scheme, "w")
# del scheme_from_config['Spaces']
#
# # object schemes
# scheme = root_scheme
# dump_scheme('object_schemes.py', 'root_scheme', scheme, "w")
#
# scheme = boundary_scheme
# scheme['parameters'] = scheme_from_config['Boundaries']
# dump_scheme('object_schemes.py', 'boundary_scheme', scheme, "a")
# del scheme_from_config['Boundaries']
