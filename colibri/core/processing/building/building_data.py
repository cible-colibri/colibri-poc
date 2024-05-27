import json
import copy
from collections import namedtuple

from colibri.core.processing.building.building_import import import_spaces, import_boundaries


default_dict_space = {'constant_internal_gains': 200,
                      'constant_internal_gains_m2': None,
                      'air_change_rate': 0.41,
                      'set_point_heating': 20.,
                      'set_point_cooling': 27.,
                      'op_modes': ['heating', 'cooling']}


class BuildingData():
    def __init__(self, building_file : str = None):
        if building_file == None:
            self.project_dict = {}
            self.space_list = []
            return;

        if not isinstance(building_file, dict):
            with open(building_file, 'r') as f:
                self.project_dict = json.load(f)
        else:
            self.project_dict = building_file

        # get spaces and add default parameters
        #TODO: create dataclass for space ?
        space_list = self.project_dict['nodes_collection']['space_collection']
        self.space_list = import_spaces(self.project_dict)
        for space in self.space_list:
            for param, val in default_dict_space.items():
                if getattr(space, param, None) is None:
                    setattr(space, param, copy.deepcopy(val))

            if getattr(space, 'constant_internal_gains_m2') is not None:
                reference_area = getattr(space, 'reference_area')
                gains_m2 = getattr(space, 'constant_internal_gains_m2')
                setattr(space, 'constant_internal_gains', reference_area * gains_m2)

        # get emitters data
        # get emitters data
        emitter_list = []
        for space in space_list:
            if 'object_collection' in space_list[space]:
                for obj in space_list[space]['object_collection']:
                    if obj['type'] == 'emitter':
                        emitter = self.project_dict['archetype_collection']['emitter_types'][obj['type_id']]
                        list_param = list(obj.keys()) + list(emitter.keys())
                        Emitter = namedtuple('Emitter', list_param)

                        for key, param in obj.items():
                            setattr(Emitter, key, param)
                        for key, param in emitter.items():
                            setattr(Emitter, key, param)

                        Emitter.label = obj['id']
                        Emitter.zone_name = space
                        emitter_list.append(Emitter)

        self.emitter_list = emitter_list

        # get boundaries data
        self.boundary_list, self.window_list = import_boundaries(self.project_dict)

    def get_zone_index(self, zone_name):
        for index, space in enumerate(self.space_list):
            if space.label == zone_name:
                return index
        return None
