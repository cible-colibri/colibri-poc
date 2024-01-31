import numpy as np


def gen_p_visc():
    # kinematic viscosity
    Temp_vec    =   np.array([10,20,30,40,50,60,70,80,90])
    kin_visco   =   np.array([1.308,1.004,0.801,0.658,0.554,0.475,0.414,0.365,0.326])*1e-6
    p_visc = np.polyfit(Temp_vec,kin_visco,3)
    return p_visc

p_visc = gen_p_visc()

def gen_tube_base():
    # materials:
    # 0=Iron
    # 1=Copper
    # 2=PEHD
    # for the moment and to test, take only identical pipe sections
    Dint_list = np.array([[25., 32., 40., 50., 63., 75., 90., 110., 125., 160.],
                         [25., 32., 40., 50., 63., 75., 90., 110., 125., 160.],
                         [25., 32., 40., 50., 63., 75., 90., 110., 125., 160.]]) / 1000.  # diameter in m
    TH_tu_list = np.array([[2.3, 2.9, 3.7, 4.6, 5.8, 6.8, 8.2, 10., 11.4, 14.6],
                          [2.3, 2.9, 3.7, 4.6, 5.8, 6.8, 8.2, 10., 11.4, 14.6],
                          [2.3, 2.9, 3.7, 4.6, 5.8, 6.8, 8.2, 10., 11.4, 14.6]]) / 1000.  # thickness in m
    Dext_list = np.array([[93., 93., 93., 113., 128., 164., 164., 164., 185., 250.],
                         [93., 93., 93., 113., 128., 164., 164., 164., 185., 250.],
                         [93., 93., 93., 113., 128., 164., 164., 164., 185., 250.]]) / 1000.  # diameter in m

    TH_is_list = Dext_list - (Dint_list + 2 * TH_tu_list)  # thickness of insulation
    k_list = np.array([0.04*1e-3, 0.015*1e-3, 0.01*1e-3])
    lambda_list = np.array([52., 372., 0.38])
    tube_base = {'diameter_internal': Dint_list,
                 'thickness_tube': TH_tu_list,
                 'diameter_external': Dext_list,
                 'thickness_insulation': TH_is_list,
                 'pipe_roughness': k_list,
                 'pipe_conductivity': lambda_list}
    return tube_base

tube_base = gen_tube_base()