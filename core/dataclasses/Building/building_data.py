import json
from collections import namedtuple

from core.dataclasses.Building.building_import import import_spaces, import_boundaries


class BuildingData():
    def __init__(self, building_file : str = None):
        if building_file == None:
            self.project_dict = {}
            self.space_list = []
            return;

        f = open(building_file)
        self.project_dict = json.load(f)

        space_list = self.project_dict['nodes_collection']['space_collection']
        self.space_list = import_spaces(self.project_dict)
        Emitter_list = []
        emitter_param_list = ['radiative_share', 'time_constant']
        for space in space_list:
            for obj in space_list[space]['object_collection']:
                if obj['type'] == 'emitter':
                    emitter = self.project_dict['archetype_collection']['emitter_types'][obj['type_id']]
                    Emitter = namedtuple('Emitter', emitter_param_list)

                    for key, param in obj.items():
                        setattr(Emitter, key, param)
                    for key, param in emitter.items():
                        setattr(Emitter, key, param)

                    Emitter.label = obj['id']
                    Emitter.zone_name = space
                    Emitter_list.append(Emitter)

        self.emitter_list = Emitter_list

        self.boundary_list, self.window_list = import_boundaries(self.project_dict)

    def get_zone_index(self, zone_name):
        for index, space in enumerate(self.space_list):
            if space.label == zone_name:
                return index
        return None

