

def bestest_configs(project_dict, case):

    # add bestest conditions
    if case <= 395:
        for i, layer in enumerate(project_dict['archetype_collection']['layer_types']):
            project_dict['archetype_collection']['layer_types'][layer]['albedo'] = 0.9
        for i, window in enumerate(project_dict['archetype_collection']['window_types']):
            project_dict['archetype_collection']['window_types'][window]['x_length'] *= 1e-10
            project_dict['archetype_collection']['window_types'][window]['y_length'] *= 1e-10
        int_gains_trigger = 0.
        infiltration_trigger = 0.

    elif case < 440:
        for i, layer in enumerate(project_dict['archetype_collection']['layer_types']):
            project_dict['archetype_collection']['layer_types'][layer]['albedo'] = 0.9
        for i, win in enumerate(project_dict['archetype_collection']['window_types']):
            window = project_dict['archetype_collection']['window_types'][win]
            window['absorption'] = 0.
            window['transmittance'] = 0.
            int_gains_trigger = 0.
            infiltration_trigger = 0.

    if case == 430:
        for i, layer in enumerate(project_dict['archetype_collection']['layer_types']):
            project_dict['archetype_collection']['layer_types'][layer]['albedo'] = 0.4

    if case == 410:
        int_gains_trigger = 0.
        infiltration_trigger = 1.

    if case >= 420:
        int_gains_trigger = 1.
        infiltration_trigger = 1.

    return project_dict, int_gains_trigger, infiltration_trigger