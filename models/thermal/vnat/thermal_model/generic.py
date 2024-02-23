import numpy as np
import matplotlib.pyplot as plt
from models.thermal.vnat.thermal_model.RyCj import set_U_from_index, get_states_from_index


def store_results(t, my_T, my_weather):

    # store all defined results
    my_T.results['solar_direct'][0, t] = my_weather.solar_direct[t]
    my_T.results['solar_diffuse'][0, t] = my_weather.solar_diffuse[t]
    my_T.results['setpoint'][:, t] = my_T.setpoint
    for res in my_T.res_list:
        if res == 'outdoor_temperatures':
            my_T.results['outdoor_temperatures'][0:len(my_T.Boundary_list), t] = my_weather.ext_temperature[t]
        elif res == 'ground_temperature':
            my_T.results['ground_temperature'][0, t] = my_weather.ground_temperature[t]
        elif res == 'hvac_flux':
            my_T.results['hvac_flux'][0:len(my_T.Space_list), t] = my_T.hvac_flux
        elif res == 'ventilation_gains':
            my_T.results['ventilation_gains'][0:len(my_T.Space_list), t] = my_T.ventilation_gains * (my_T.ventilation_gains < 0.) * (my_T.op_mode[0] == 'heating')
        elif res == 'window_losses':
            my_T.results['window_losses'][0:len(my_T.Space_list), t] = my_T.window_losses * (my_T.window_losses < 0.) * (my_T.op_mode[0] == 'heating')
        elif res == 'window_gains':
            my_T.results['window_gains'][0:len(my_T.Space_list), t] = my_T.window_gains * (my_T.op_mode[0] == 'heating')
        elif res == 'wall_losses':
            my_T.results['wall_losses'][0:len(my_T.Space_list), t] = my_T.wall_losses * (my_T.wall_losses < 0.) * (my_T.op_mode[0] == 'heating')
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
    h_power = my_T.results['hvac_flux'] * (my_T.results['hvac_flux'] >= 0)
    c_power = my_T.results['hvac_flux'] * (my_T.results['hvac_flux'] < 0)
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
        plt.figure()
        ax1 = plt.subplot(3, 2, 1)
        plt.plot(my_T.results['outdoor_temperatures'].T)
        plt.plot(my_T.results['ground_temperature'].T)
        plt.ylabel('Temp [°C]')
        plt.ylim([-15, 30])
        # plt.xlim([5000, 6000])
        plt.grid()
        plt.legend(['direct outdoor_temperatures', 'ground_temperature'])
        plt.title('Outdoor temperatures')
        ax2 = plt.subplot(3, 2, 2, sharex=ax1)
        plt.plot(my_T.results['solar_direct'].T)
        plt.plot(my_T.results['solar_diffuse'].T)
        plt.ylabel('flux [W]')
        plt.ylim([0, 1000.])
        plt.grid()
        plt.legend(['direct normal', 'diffuse_horizontal'])
        plt.title('Solar radiation')
        ax3 = plt.subplot(3, 2, 3, sharex=ax1)
        plt.plot(my_T.results['setpoint'].T, 'k--')
        plt.plot(my_T.results['spaces_air'].T)
        plt.plot(my_T.results['spaces_mean_radiant'].T)
        plt.ylabel('Temp [°C]')
        plt.ylim([10, 35])
        plt.grid()
        plt.legend(['Setpoint', 'air_temperature', 'radiant_temperature'])
        plt.title('Space air and mean radiant temperatures')
        ax4 = plt.subplot(3, 2, 4,  sharex=ax1)
        plt.plot(my_T.results['windows'].T)
        plt.ylabel('Temp [°C]')
        plt.ylim([-10, 35])
        plt.grid()
        plt.title('Window surface temperatures')
        ax5 = plt.subplot(3, 2, 5,  sharex=ax1)
        plt.plot(my_T.results['boundaries'].T)
        plt.xlabel('Time [h]')
        plt.ylabel('Temp [°C]')
        plt.ylim([-10, 40])
        plt.grid()
        plt.title('Wall node temperatures')
        ax6 = plt.subplot(3, 2, 6,  sharex=ax1)
        h_power = my_T.results['hvac_flux'] * (my_T.results['hvac_flux'] >=0)
        c_power = my_T.results['hvac_flux'] * (my_T.results['hvac_flux'] < 0)
        plt.plot(h_power.T)
        plt.plot(c_power.T)
        h_energy = h_power.cumsum(axis=1)/1000.
        c_energy = c_power.cumsum(axis=1) / 1000.
        plt.plot(h_energy.T)
        plt.plot(c_energy.T)
        plt.xlabel('Time [h]')
        plt.ylabel('Flux [W]')
        plt.ylim([-8000, 6000.])
        plt.grid()
        plt.title('Hvac power')
        plt.suptitle('All temperatures in house.json')
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
