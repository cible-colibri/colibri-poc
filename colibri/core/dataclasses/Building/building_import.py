# -*- coding: utf-8 -*-
import json
import numpy as np
from collections import namedtuple
from colibri.models.thermal.DetailedBuilding.RyCj import gen_wall_model


def import_project(file_name):
    f = open(file_name)
    return json.load(f)


def import_spaces(project_dict):
    space_list = project_dict['nodes_collection']['space_collection']
    Space_list = []
    space_param_list = ['volume', 'reference_area', 'altitude', 'air_permeability']
    for space in space_list:
        Space = namedtuple('Space', space_param_list)
        Space.label = space
        for i in Space._fields:
            setattr(Space, i, space_list[space][i])
        Space_list.append(Space)

    return Space_list


def import_emitters(project_dict):
    space_list = project_dict['nodes_collection']['space_collection']
    Emitter_list = []
    emitter_param_list = ['radiative_share','time_constant']
    for space in space_list:
        for obj in space_list[space]['object_collection']:
            if obj['type'] == 'emitter':
                emitter = project_dict['archetype_collection']['emitter_types'][obj['type_id']]
                Emitter = namedtuple('Emitter', emitter_param_list)
                Emitter.label = obj['id']
                Emitter.zone_name = space
                for i in Emitter._fields:
                    setattr(Emitter, i, emitter[i])
                Emitter_list.append(Emitter)
    return Emitter_list


def import_boundaries(project_dict):
    boundary_list       = project_dict['boundary_collection']
    boundary_type_list  = project_dict['archetype_collection']['boundary_types']
    layer_list          = project_dict['archetype_collection']['layer_types']

    # load Boundaries and save in List of Boundaries, Windows
    Boundary_list   = []
    Window_list     = []
    checker = 0
    bound = 0
    for boundary in boundary_list:
        # set parameter names in Boundary namedtuple (same coding later as in classes)
        bound_param_list = ['thermal_conductivity', 'specific_heat', 'density', 'thickness', 'light_reflectance', 'albedo', 'emissivity', 'discret']
        Boundary = namedtuple('Boundary', bound_param_list)
        Boundary.label = boundary
        # initialise each field with an empty array, to be filled in later on
        for i in Boundary._fields:
            setattr(Boundary, i, [])
        # get general parameters of Boundary
        Boundary.area    = boundary_list[boundary]['area']
        Boundary.side_1  = boundary_list[boundary]['side_1']
        Boundary.side_2  = boundary_list[boundary]['side_2']
        Boundary.tilt    = boundary_list[boundary]['tilt']
        Boundary.azimuth = boundary_list[boundary]['azimuth']

        type_id = boundary_list[boundary]['type_id']
        # get thermal parameters of boundary
        boundary_type = boundary_type_list[type_id]
        layer_matrix = np.zeros((len(boundary_type['layers']), 8))

        for layer_type in boundary_type['layers']:
            for param in bound_param_list:
                if param == 'discret':
                    value = 1  # in general, 1 node per layer is enough - i.e. in addition to the internal layers each wall has surface layers on each surface
                else:
                    value = layer_list[layer_type['type_id']][param]
                getattr(Boundary, param).append(value)

        Boundary = gen_wall_model(Boundary)
        for obj in boundary_list[boundary]['object_collection']:
            if obj['type'] == 'window':
                # search for window characteristics in window archetypes
                window = project_dict['archetype_collection']['window_types'][obj['type_id']]
                # now go through windows
                window_param_list = []
                Window = namedtuple('Windows', window_param_list)
                # initialise each field with an empty array, to be filled in later on
                # for i in Window._fields:
                #     setattr(Window, i, [])
                Window.label = obj['id']
                Window.x_length = window['x_length']
                Window.y_length = window['y_length']
                Window.area     = Window.x_length * Window.y_length
                Window.side_1   = Boundary.side_1
                Window.side_2   = Boundary.side_2
                Window.tilt     = Boundary.tilt
                Window.azimuth  = Boundary.azimuth
                Window.bound_nb = bound
                Window.bound_name = boundary
                if 'u_value' in window.keys():
                    Window.u_value = window['u_value']
                else:
                    Window.u_value = 3.0
                if 'emissivity' in window.keys():
                    Window.emissivity = window['emissivity']
                else:
                    Window.emissivity = [0.85, 0.85]
                if 'transmittance' in window.keys():
                    Window.transmittance = window['transmittance']
                else:
                    Window.transmittance = 0.7475*(1-0.035) # 0.787*(1-0.035)#
                if 'absorption' in window.keys():
                    Window.absorption = window['absorption']
                else:
                    Window.absorption = 0.08

                Window_list.append(Window)
                Boundary.area -= Window.area
        checker += 1
        # save both, Boundary and Window in list of elements
        Boundary_list.append(Boundary)
        bound += 1

    return Boundary_list, Window_list
