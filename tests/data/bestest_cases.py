

def bestest_configs(project_dict, case):

    # add bestest conditions
    if case <= 395:
        for i, layer in enumerate(project_dict['archetype_collection']['layer_types']):
            project_dict['archetype_collection']['layer_types'][layer]['albedo'] = 0.9
        for i, window in enumerate(project_dict['archetype_collection']['window_types']):
            project_dict['archetype_collection']['window_types'][window]['x_length'] *= 1e-10
            project_dict['archetype_collection']['window_types'][window]['y_length'] *= 1e-10
        for i, space in enumerate(project_dict['nodes_collection']['space_collection']):
            project_dict['nodes_collection']['space_collection'][space]['constant_internal_gains'] = 0
            project_dict['nodes_collection']['space_collection'][space]['air_change_rate'] = 0

    elif case < 440:
        for i, layer in enumerate(project_dict['archetype_collection']['layer_types']):
            project_dict['archetype_collection']['layer_types'][layer]['albedo'] = 0.9
        for i, win in enumerate(project_dict['archetype_collection']['window_types']):
            window = project_dict['archetype_collection']['window_types'][win]
            window['absorption'] = 0.
            window['transmittance'] = 0.
        for i, space in enumerate(project_dict['nodes_collection']['space_collection']):
            project_dict['nodes_collection']['space_collection'][space]['constant_internal_gains'] = 0
            project_dict['nodes_collection']['space_collection'][space]['air_change_rate'] = 0

    if case == 430:
        for i, layer in enumerate(project_dict['archetype_collection']['layer_types']):
            project_dict['archetype_collection']['layer_types'][layer]['albedo'] = 0.4

    if case == 410:
        for i, space in enumerate(project_dict['nodes_collection']['space_collection']):
            project_dict['nodes_collection']['space_collection'][space]['constant_internal_gains'] = 0
            project_dict['nodes_collection']['space_collection'][space]['air_change_rate'] = 0.41

    if case >= 420:
        for i, space in enumerate(project_dict['nodes_collection']['space_collection']):
            project_dict['nodes_collection']['space_collection'][space]['constant_internal_gains'] = 200
            project_dict['nodes_collection']['space_collection'][space]['air_change_rate'] = 0.41

    return project_dict