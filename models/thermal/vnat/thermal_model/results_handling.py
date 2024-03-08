import numpy as np

def initialise_results(index_states, Space_list, Boundary_list, n_steps, results_definition = 'all'):
    # generate global dict where results can be saved
    results = {}
    for res in index_states.keys():
            results[res] = np.zeros((index_states[res]['n_elements'], n_steps))
    results['outdoor_temperatures'] = np.zeros((len(Boundary_list), n_steps))
    results['ground_temperature'] = np.zeros((1, n_steps))
    results['solar_direct'] = np.zeros((1, n_steps))
    results['solar_diffuse'] = np.zeros((1, n_steps))
    results['hvac_flux_vec'] = np.zeros((len(Space_list), n_steps))
    results['setpoint'] = np.zeros((len(Space_list), n_steps))
    results['window_losses'] = np.zeros((len(Space_list), n_steps))
    results['wall_losses'] = np.zeros((len(Space_list), n_steps))
    results['window_gains'] = np.zeros((len(Space_list), n_steps))
    results['ventilation_gains'] = np.zeros((len(Space_list), n_steps))

    # define here which variables you want to save and plot (if empty list, all variables will be saved)
    if results_definition == 'all':
        res_list = ['outdoor_temperatures', 'ground_temperature', 'solar_direct', 'solar_diffuse', 'hvac_flux_vec',
                    'spaces_air', 'spaces_mean_radiant', 'windows', 'boundaries',
                    'window_losses', 'window_gains', 'wall_losses', 'ventilation_gains']
    elif results_definition == 'custom':
        res_list = ['spaces_air']  # select this one if you only want some of them
    else:
        res_list = []  # tun on this one to check simulation speed without data storage


    return results, res_list