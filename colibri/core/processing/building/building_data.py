import json
import copy
from collections import namedtuple

from colibri.core.processing.building.building_import import import_spaces, import_boundaries
from colibri.core.model import Model
from colibri.utils.enums_utils import Roles, Units

default_dict_space = {'constant_internal_gains': 200,
                      'constant_internal_gains_m2': None,
                      'air_change_rate': 0.41,
                      'set_point_heating': 20.,
                      'set_point_cooling': 27.,
                      'op_modes': ['heating', 'cooling']}


class BuildingData(Model):

    def __init__(self, building_file : str = None):
        self.name = "building_data"
        super(BuildingData, self).__init__(self.name)

        self.Boundaries = self.field("Boundaries", [], role=Roles.OUTPUTS, unit=Units.UNITLESS)
        self.Spaces = self.field("Spaces", [], role=Roles.OUTPUTS, unit=Units.UNITLESS)
        self.Emitters = self.field("Emitters", [], role=Roles.OUTPUTS, unit=Units.UNITLESS)

        self.TintWall = self.field("TintWall", [], role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)

        self.Qwall = self.field("Qwall", {}, role=Roles.INPUTS, unit=Units.UNITLESS)

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
        self.spaces = import_spaces(self.project_dict)
        for space in self.spaces:
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
        self.space_list = self.project_dict['nodes_collection']['space_collection']
        for space in self.spaces:
            space.emitters = []
            if 'object_collection' in self.space_list[space.label]:
                for obj in self.space_list[space.label]['object_collection']:
                    if obj['type'] == 'emitter':
                        emitter = self.project_dict['archetype_collection']['emitter_types'][obj['type_id']]
                        list_param = list(obj.keys()) + list(emitter.keys())
                        Emitter = namedtuple('Emitter', list_param)

                        for key, param in obj.items():
                            setattr(Emitter, key, param)
                        for key, param in emitter.items():
                            setattr(Emitter, key, param)

                        Emitter.label = obj['id']
                        Emitter.zone_name = space.label

                        # for proto archi - remove this or add efficiency/maxQ or add to json
                        if not hasattr(Emitter, 'efficiency'):
                            setattr(Emitter, 'efficiency', 0.9)
                        if not hasattr(Emitter, 'maxQ'):
                            setattr(Emitter, 'maxQ', 1)
                        if not hasattr(Emitter, 'qProvided'):
                            setattr(Emitter, 'qProvided', 1)

                        emitter_list.append(Emitter)

                        space.emitters.append(Emitter)

        self.emitter_list = emitter_list

        # get boundaries data
        self.boundary_list, self.window_list = import_boundaries(self.project_dict)

        self.TintWall = []
        for boundary in self.boundary_list:
            boundary.space = self.space_for_boundary(boundary)
            boundary.space.boundaries.append(boundary)
            self.TintWall.append(20.0) # TODO: replace by boundary.Tint

        self.Boundaries = self.boundary_list
        self.Spaces = self.spaces
        self.Emitters = self.emitter_list

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        for id, value in self.Qwall.items():
            boundary = self.boundary_from_ID(id)
            boundary.Qwall = value

    def simulation_done(self, time_step: int = 0):
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass

    def get_zone_index(self, zone_name):
        for index, space in enumerate(self.spaces):
            if space.label == zone_name:
                return index
        return None

    def space_for_boundary(self, boundary):
        for space in self.spaces:
            if space.label == boundary.side_1 or space.label == boundary.side_2:
                return space
        return None

    def boundary_from_ID(self, id):
        for boundary in self.boundary_list:
            if boundary.label == id:
                return boundary
        return None