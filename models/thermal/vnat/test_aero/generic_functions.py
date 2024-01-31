import numpy as np


def interpolate_function(input_act, interpolate_matrix):
    input_list = interpolate_matrix[0]
    output_list = interpolate_matrix[1]

    # check if input_act is out of range of data points

    if input_act < input_list[0]:  # saturate at lowest value in input_list
        result = output_list[0]
    elif input_act > input_list[-1]:    # saturate at highest value in input_list
        result = output_list[-1]
    else:
        # go through data set and interpolate
        for i in range(len(input_list) - 1):
            if (input_act > input_list[i]) and (input_act <= input_list[i + 1]):
                input_diff = input_list[i+1] - input_list[i]
                if input_diff == 0.:  # input_list must be monotone, if not fail !
                    result = 0.
                    raise ValueError('Wrong interpolation matrix')
                else:  # interpolate
                    alpha = (output_list[i+1] - output_list[i]) / input_diff
                    q = output_list[i+1] - alpha * input_list[i+1]
                    result = alpha * input_act + q
            else:
                result = min(output_list)

    return result

