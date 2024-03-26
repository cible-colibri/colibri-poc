import numpy as np
import matplotlib.pyplot as plt
from models.thermal.DetailedBuilding.RyCj import get_states_from_index


def store_results(t, my_T, my_weather):

    # store all defined results
    my_T.results['solar_direct'][0, t] = my_weather.solar_direct[t]
    my_T.results['solar_diffuse'][0, t] = my_weather.solar_diffuse[t]
    my_T.results['setpoint'][:, t] = my_T.setpoint
    for res in my_T.res_list:
        if res == 'outdoor_temperatures':
            my_T.results['outdoor_temperatures'][0:len(my_T.project.building_data.boundary_list), t] = my_weather.ext_temperature[t]
        elif res == 'ground_temperature':
            my_T.results['ground_temperature'][0, t] = my_weather.ground_temperature[t]
        elif res == 'hvac_flux_vec':
            my_T.results['hvac_flux_vec'][0:my_T.n_spaces, t] = my_T.hvac_flux_vec
        elif res == 'ventilation_gains':
            my_T.results['ventilation_gains'][0:my_T.n_spaces, t] = my_T.ventilation_gains * (my_T.ventilation_gains < 0.) * (my_T.op_mode[0] == 'heating')
        elif res == 'window_losses':
            my_T.results['window_losses'][0:my_T.n_spaces, t] = my_T.window_losses * (my_T.window_losses < 0.) * (my_T.op_mode[0] == 'heating')
        elif res == 'window_gains':
            my_T.results['window_gains'][0:my_T.n_spaces, t] = my_T.window_gains * (my_T.op_mode[0] == 'heating')
        elif res == 'wall_losses':
            my_T.results['wall_losses'][0:my_T.n_spaces, t] = my_T.wall_losses * (my_T.wall_losses < 0.) * (my_T.op_mode[0] == 'heating')
        elif 'solar' in res:
            pass
        else:
            my_T.results[res][0:my_T.index_states[res]['n_elements'], t] = np.array(get_states_from_index(my_T.states, my_T.index_states, res))


def convergence_plot(found, t, it, name_plot, to_plot=False):
    if to_plot:
        # if np.mod(t, 24) == 0:
        plt.plot(found, 'r-+')
        plt.title(name_plot + ' : ' + str(np.round(found[-1], 1)) + ' iterations : ' + str(it+1))
        plt.show()


def print_results(my_T):

    print('###################################################################')
    h_power = my_T.results['hvac_flux_vec'] * (my_T.results['hvac_flux_vec'] >= 0)
    c_power = my_T.results['hvac_flux_vec'] * (my_T.results['hvac_flux_vec'] < 0)
    h_energy = h_power.cumsum(axis=1)/1000.
    c_energy = c_power.cumsum(axis=1) / 1000.

    print('###################################################################')
    print('Heating energy : ', np.round(h_energy[0,-1]/1000., 1))
    print('Cooling energy : ', np.round(c_energy[0,-1]/1000., 1))
    print('Heating peak : ', np.round(np.max(h_power)/1000., 1))
    print('Cooling peak : ', np.round(np.min(c_power)/1000., 1))
    print('Max. temperature : ', np.round(np.max(my_T.results['spaces_air']), 1))
    print('Mean temperature : ', np.round(np.mean(my_T.results['spaces_air']), 1))
    print('Min. temperature : ', np.round(np.min(my_T.results['spaces_air']), 1))
    print('###################################################################')


def plot_results(my_T, to_plot=False):
    if to_plot:

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex='all')
        ax1.plot(my_T.results['outdoor_temperatures'].T)
        ax1.plot(my_T.results['ground_temperature'].T)
        ax1.set_ylabel('Temp [°C]')
        # plt.xlim([5000, 6000])
        plt.grid()
        plt.legend(['direct outdoor_temperatures', 'ground_temperature'])
        ax1.set_title('Outdoor temperatures')

        ax2.plot(my_T.results['solar_direct'].T)
        ax2.plot(my_T.results['solar_diffuse'].T)
        ax2.set_ylabel('flux [W]')
        plt.grid()
        plt.legend(['direct normal', 'diffuse_horizontal'])
        ax2.set_title('Solar radiation')

        plt.suptitle('External conditions')

        fig, (ax3, ax4, ax5) = plt.subplots(3, 1, sharex='all')

        ax3.plot(my_T.results['spaces_mean_radiant'].T)
        ax3.plot(my_T.results['spaces_air'].T)
        ax3.plot(my_T.results['setpoint'].T, 'k--')
        ax3.set_ylabel('Temp [°C]')
        plt.grid()
        plt.legend(['Setpoint', 'air_temperature', 'radiant_temperature'])
        ax3.set_title('Space air and mean radiant temperatures')

        ax4.plot(my_T.results['windows'].T)
        ax4.set_ylabel('Temp [°C]')
        plt.grid()
        ax4.set_title('Window surface temperatures')

        ax5.plot(my_T.results['boundaries'].T)
        ax5.set_xlabel('Time [h]')
        ax5.set_ylabel('Temp [°C]')
        plt.grid()
        ax5.set_title('Wall node temperatures')

        plt.suptitle('All temperatures in house.json')

        fig, ax = plt.subplots()
        h_power = my_T.results['hvac_flux_vec'] * (my_T.results['hvac_flux_vec'] >=0)
        c_power = my_T.results['hvac_flux_vec'] * (my_T.results['hvac_flux_vec'] < 0)
        ax.plot(h_power.T)
        ax.plot(c_power.T)
        h_energy = h_power.cumsum(axis=1)/1000.
        c_energy = c_power.cumsum(axis=1) / 1000.
        ax.plot(h_energy.T)
        ax.plot(c_energy.T)
        ax.set_xlabel('Time [h]')
        ax.set_ylabel('Flux [W]')
        plt.grid()
        plt.title('Hvac power')


        plt.show()

        # plt.figure()
        # plt.plot(my_T.results['wall_losses'].T, 'k')
        # plt.plot(my_T.results['window_losses'].T, 'r')
        # plt.plot(my_T.results['ventilation_gains'].T, 'b')
        # plt.plot(my_T.results['window_gains'].T, 'g')
        # plt.legend(['Wall losses', 'Window losses', 'Ventilation losses', 'Window gains'])
        # plt.show()
        # window_losses = np.sum(my_T.results['window_losses'])/1000.
        # wall_losses = np.sum(my_T.results['wall_losses']) / 1000.
        # ventilation_losses = np.sum(my_T.results['ventilation_gains']) / 1000.
        # window_gains = np.sum(my_T.results['window_gains']) / 1000.
        # losses = window_losses + wall_losses + ventilation_losses
        # window_loss_share = np.round(window_losses / losses * 100., 1)
        # wall_loss_share = np.round(wall_losses / losses * 100., 1)
        # ventilation_loss_share = np.round(ventilation_losses / losses * 100., 1)
        # print('Walls : ', wall_loss_share, 'Windows : ', window_loss_share, 'Ventilation : ', ventilation_loss_share)
