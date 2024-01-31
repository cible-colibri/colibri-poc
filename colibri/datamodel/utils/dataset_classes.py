# -*- coding: utf-8 -*-
"""
Module that creates utils classes for manipulating COLIBRI V1 datamodel : create, add, connect objects based on archetype_scheme and object_scheme.
"""

# ========================================
# External imports
# ========================================

import copy
import warnings
import random
import ast
import inspect
import math

# ========================================
# Internal imports
# ========================================

from colibri.datamodel.schemes import object_schemes
from colibri.datamodel.schemes import archetype_schemes, node_schemes

# ========================================
# Constants
# ========================================

# ========================================
# Variables
# ========================================

# ========================================
# Functions
# ========================================

def check_dict_equality(dict1, dict2, keys_to_exclude=None):
    '''
    Check if two dict are equal in values and subvalues. Totally or by excluding some key (using keys_to_exclude)
     Parameters
     ----------
     dict1 : dict,
         first dict to compare
     dict2 : str,
         second dict to compare
     keys_to_exclude : list (optional),
         list of keys to exclude from the comparison

     Returns
     -------
     result : bool,
        True if dicts are equal, False if not
     '''

    if keys_to_exclude is None:
        keys_to_exclude = []

    # Check if the same keys are present in both dicts (excluding keys_to_exclude)
    common_keys = set(dict1.keys()) & set(dict2.keys())  # Intersection of keys in both dicts
    if (len(common_keys) != len(dict1.keys())) or (len(common_keys) != len(dict2.keys())):
        warnings.warn("WARNING, dict1 and dict2 have not the same amount of key. The comparison will be only on common keys)")

    keys_to_check = common_keys - set(keys_to_exclude)  # Removing keys to exclude

    are_values_equal = all(dict1[key] == dict2[key] for key in keys_to_check)

    return are_values_equal


# ========================================
# Classes
# ========================================
class Scheme():
    '''Create a dataset object based on scheme function'''

    def __init__(self, type_name, mode="archetype", dataset=None, logs = True, **inputs):
        '''Load and fill object based on scheme and optional inputs parameter
        Parameters
        ----------
        type_name : str,
            name of the COLIBRI object
        mode : str,
            "archetype" or "object" :
            - if "archetype" : the archetype scheme (properties that can be factorized/mutualised between object) associated to the type_name object is load and filled
            - else : the object scheme (properties that are unique for each object) associated to the type_name object is load and filled
        dataset : DataSet object,
            DataSet object in which the object creation will be used
        logs : bool,
            Allows the print of logs or not
        **inputs : param,
            any other parameter that user want to set amoung scheme parameters.

        Returns
        -------
        '''

        self.type_name = type_name
        self.dataset = dataset
        self.mode = mode
        self.logs = logs

        if self.mode == "archetype":
            try:
                # Access schema based on type name
                self.scheme = getattr(archetype_schemes, f'{type_name}_types_scheme')
            except AttributeError:
                raise ValueError(f"No scheme found for object of type: {type_name}")
        elif self.mode == "node":
            try:
                # Access schema based on type name
                self.scheme = getattr(node_schemes, f'{type_name}_scheme')
            except AttributeError:
                raise ValueError(f"No scheme found for object of type: {type_name}")
        else:
            try:
                # Access schema based on type name
                self.scheme = getattr(object_schemes, f'{type_name}_scheme')
            except AttributeError:
                raise ValueError(f"No scheme found for object of type: {type_name}")

        # check **inputs
        for var in inputs:
            if var not in list(self.scheme["parameters"].keys()) +["id"]: #exception is made for id
                warnings.warn(f"Inputs parameter {var} is not a {self.type_name} {self.mode} available parameter")

    def check_input(self, input_value, param_name):
        '''
        Check if a user input value is correct
        Parameters
        ----------
        input_value : various,
            input value choose by user for a given parameter
        param_name : str,
            name of the parameter in order to control if the input_value is acceptable for this parameter

        Returns
        -------
        result : dict,
            return a dict with the following format : {"validity" : bool True or False, "message":str in case of error message to explain why the validity is False}

        '''

        # check format
        format = self.scheme["parameters"][param_name]["format"]
        if format is not None:
            if (format == "int") and not isinstance(input_value, int):
                return {"validity": False,
                        "message": f"The given value for {param_name} : {input_value} do not respect the expected format : {format}"}
            if format == "float":
                try:
                    float(input_value)
                except:
                    return {"validity": False,
                        "message": f"The given value for {param_name} : {input_value} do not respect the expected format : {format}"}
            if format in ["enum","string"] and not isinstance(input_value, str):
                return {"validity": False,
                        "message": f"The given value for {param_name} : {input_value} do not respect the expected format : {format}"}

        # check choices for enum
        if self.scheme['parameters'][param_name]["format"] == "enum":
            if input_value not in self.scheme['parameters'][param_name]['choices']:
                return {"validity": False, "message" : f"The given value for {param_name} : {input_value} is not available in {param_name} choices.\n"
                                 f"Please choose among the following list : {self.scheme['parameters'][param_name]['choices']}"}
        # check min
        if self.scheme["parameters"][param_name]["min"] is not None:
            if float(input_value) < self.scheme['parameters'][param_name]['min']:
                return {"validity": False,
                        "message": f"The given value for {param_name} : {input_value} is not acceptable since the minimum acceptable value for {param_name} is set to {self.scheme['parameters'][param_name]['min']}"}

        # check max
        if self.scheme["parameters"][param_name]["max"] is not None:
            if float(input_value) > self.scheme['parameters'][param_name]['max']:
                return {"validity": False,
                        "message": f"The given value for {param_name} : {input_value} is not acceptable since the maximum acceptable value for {param_name} is set to {self.scheme['parameters'][param_name]['max']}"}

        return {"validity":True, "message":None}


    def initiate_data(self, inputs):
        '''function that initiate the object based on its scheme and a dict of optional inputs by user
        Parameters
        ----------
        inputs : dict (optional),
            dict with scheme parameter has key to set value
        Returns
        -------
        '''
        # Initiate data based on inputs parameter and/or default values set in scheme
        self.data = copy.deepcopy(self.scheme["structure"])

        default_to_all = False
        for key, value in self.data.items():
            if key in inputs.keys():

                check = self.check_input(inputs[key], key)
                if not check["validity"]:
                    raise ValueError(check["message"])

                self.data[key] = inputs[key]

            elif isinstance(self.data[key], list):
                if len(self.data[key])>0:
                    for sub_key in self.data[key][0].keys():
                        if sub_key in self.scheme["parameters"].keys():
                            self.data[key][0][sub_key] = self.scheme["parameters"][sub_key]["default"]
                        elif sub_key == "type":  # reference for other archetype ("type" is a reserved key)
                            type_element = self.data[key][0][sub_key]
                            if self.dataset is not None:  # we can search inside the dataset archetype collection to initiate the type_id
                                if f"{self.data[key][0][sub_key]}_collection" in self.dataset.archetype_collection.keys():
                                    if len(self.dataset.archetype_collection[f"{self.data[key][0][sub_key]}_collection"]) > 0:
                                        type_id = "no"
                                        if self.dataset.assist_mode == True:
                                            type_id = input(
                                                f"Please, reference at least one {type_element} for {key} parameter amoung {type_element}_collection :\n {str(self.dataset.archetype_collection[f'{type_element}_collection'].keys())}\n If you type 'no', we will choose the first one ==> ")

                                        if type_id in self.dataset.archetype_collection[f'{type_element}_collection'].keys():
                                            self.data[key][0]["type_id"] = type_id
                                            print(
                                                f"Successfully link {type_element} to {type_id} element of {type_element}_collection \n -----------------------------") if self.logs else None
                                        else:
                                            self.data[key][0]["type_id"] = \
                                                list(self.dataset.archetype_collection[f"{type_element}_collection"].keys())[
                                                    0]  # we take the first key of the dict, i.e the first id found in the collection
                                            warnings.warn(
                                                f"Automatically link {type_element} reference for {key} parameter to the first element of {type_element}_collection : \n id {self.data[key][0]['type_id']} and label {self.dataset.archetype_collection[f'{type_element}_collection'][self.data[key][0]['type_id']]['label']}")
                                    else:
                                        raise
                                        ValueError(
                                            f"{self.type_name} archetype need to reference at least one {type_element} element of archetype_collection and no one exist.\n Please create at least one before creating {self.type_name} object")
                                else:
                                    raise
                                    ValueError(
                                        f"{self.type_name} archetype need to reference at least one {type_element} element of archetype_collection and no one exist.\n Please create at least one before creating {self.type_name} object")
                            else:
                                warnings.warn(
                                    f"{self.type_name} archetype need to reference at least one {type_element} element of archetype_collection. Therefore it need to be linked to a dataset class element to correctly be instantiated") if self.logs else None

            else:
                if key in self.scheme["parameters"].keys():
                    value = "default"
                    if self.dataset is not None:
                        if (self.dataset.assist_mode == True) and (not default_to_all):
                            print("=======parameter value editor======") if self.logs else None
                            value = input(
                                f"Please, give a value for {key}: \n {self.describe(key) if self.logs else None} \n if you want to use default value if it exists, type 'default'. If you want use default value for all archetype parameter type 'default to all' ==> ")
                            if value == "default to all":
                                default_to_all = True

                    if (value != "default") and not default_to_all:
                        check = self.check_input(value, key)
                        if not check["validity"]:
                            raise ValueError(check["message"])
                        self.data[key] = value
                        print(f"Successfully set {key} value to id to {value} \n -----------------------------") if self.logs else None
                    else:
                        if self.scheme["parameters"][key]["default"] is not None:
                            self.data[key] = self.scheme["parameters"][key]["default"]
                            print(
                                f"Successfully set default {key} value to id to {self.scheme['parameters'][key]['default']} \n -----------------------------") if self.logs else None
                        else:
                            print(
                                f"WARNING : no default value existing for {key}, value keep at None \n -----------------------------") if self.logs else None

    def describe(self, parameter_name=None):
        '''
        Provide help and documentation about the current object parameters
        Parameters
        ----------
        parameter_name : str (optional),
            string name of a parameter

        Returns
        -------
        documentation : print(str),
            return print documentation on the parameter name or all parameters if parameter_name = None
        '''

        if parameter_name is not None:
            if parameter_name in self.scheme["parameters"].keys():
                documentation = f"{parameter_name} : \n {self.scheme['parameters'][parameter_name]['info']} \n"
                for metadata in self.scheme['parameters'][parameter_name].keys() - ['info']:
                    if self.scheme['parameters'][parameter_name][metadata] is not None:
                        documentation += f"- {metadata} : {self.scheme['parameters'][parameter_name][metadata]}, \n"

                return print(documentation)
            else:
                raise ValueError(
                    f"{parameter_name} is not a {self.type_name} available parameter. \n Please use 'describe()' to access all available parameter for this object")

        else:
            documentation = f"Here the list of parameters use for {self.mode} configuration of {self.type_name} object : \n"
            for key in self.scheme["parameters"]:
                documentation += f"- {key} : {self.scheme['parameters'][key]['info']}"
                if self.scheme['parameters'][key]['unit'] is not None:
                    documentation += f" in {self.scheme['parameters'][key]['unit']}, \n"
                else:
                    documentation += " \n"

            return print(documentation)

class Node(Scheme):
    '''Create a Node of a given type among type_name : space, linear_junction, ponctual_junction...'''

    def __init__(self, type_name, dataset=None, logs = True, **inputs):
        '''
        Load and fill object based on scheme and optional inputs parameter
        Parameters
        ----------
        type_name : str,
            type name of the COLIBRI node element
        dataset : DataSet object,
            DataSet object in which the object creation will be used
        logs : bool,
            Allows the print of logs or not
        **inputs : param,
            any other parameter that user want to set amoung node scheme parameters.

        Returns
        -------

        '''

        super().__init__(type_name=type_name, mode="node", dataset=dataset, logs = logs, **inputs)

        self.initiate_data(inputs)

class Object(Scheme):
    '''Create an boundary linked object'''

    def __init__(self, dataset=None, logs = True, **inputs):
        '''
        Load and fill object based on scheme and optional inputs parameter
        Parameters
        ----------
        dataset : DataSet object,
            DataSet object in which the object creation will be used
        logs : bool,
            Allows the print of logs or not
        **inputs : param,
            any other parameter that user want to set amoung generic object scheme parameters.

        Returns
        -------

        '''

        super().__init__(type_name="boundary_object", mode="object", dataset=dataset, logs = logs, **inputs)

        self.initiate_data(inputs)

class Archetype(Scheme):
    '''Create an archetype for a given object type'''

    def __init__(self, type_name, dataset=None, logs = True, **inputs):
        '''
        Load and fill archetype based on scheme and optional inputs parameter
        Parameters
        ----------
        type_name : str,
            type name of the COLIBRI archetype element
        dataset : DataSet object,
            DataSet object in which the object creation will be used
        logs : bool,
            Allows the print of logs or not
        **inputs : param,
            any other parameter that user want to set amoung archetype scheme parameters.

        Returns
        -------

        '''

        super().__init__(type_name=type_name, mode="archetype", dataset=dataset, logs = logs, **inputs)

        self.initiate_data(inputs)

class Boundary(Scheme):
    '''Create a boundary object'''

    def __init__(self, dataset=None, logs = True, **inputs):
        '''
        Load and fill boundary and its optional inputs parameter
        Parameters
        ----------
        dataset : DataSet object,
            DataSet object in which the object creation will be used
        logs : bool,
            Allows the print of logs or not
        **inputs : param,
            any other parameter that user want to set amoung boundary object scheme parameters.

        Returns
        -------

        '''
        super().__init__(type_name="boundary", mode="object", dataset=dataset, logs = logs, **inputs)

        self.initiate_data(inputs)

class DataSet():
    '''Create a new full COLIBRI input dataset'''

    def __init__(self, assist_mode = True, logs = True, geojson = None):
        '''
        Create a COLIBRI DataSet class
        Parameters
        ----------
        assist_mode : bool,
            Allows you to activate or not the input help in case of missing fields. If not, no help will be provided and missing values ​​will be set to default values ​​when they exist
        logs : bool,
            If True, log print are enable. If False, logs print are disable.
        geojson : dict (optional),
            Allows to load an existing COLIBRI geojson file to initiate the DataSet
        '''

        if geojson is not None:
            try:
                #TODO : quicktest to see if it is a correct colibri geojson more precise than a try/except ?

                self.building_land = geojson["building_land"]
                self.nodes_collection = geojson["nodes_collection"]
                self.boundary_collection = geojson["boundary_collection"]
                self.archetype_collection = geojson["archetype_collection"]

                self.id_list = []
                for boundary_id in self.boundary_collection.keys():
                    self.id_list.append(boundary_id)
                    if self.boundary_collection[boundary_id]["segments"] is None: #means it is not a 3D project
                        self.d3_model = False
                        break
                    else:
                        self.d3_model = True

                for node_type in self.nodes_collection.keys():
                    for node_id in self.nodes_collection[node_type].keys():
                        self.id_list.append(node_id)

                for archetype_type in self.archetype_collection.keys():
                    for archetype_id in self.archetype_collection[archetype_type].keys():
                        self.id_list.append(archetype_id)

            except Exception as e:
                raise ValueError(f"Error in loading json as COLIBRI json.\n It seems that the given geojson is not a COLIBRI geojson :\n {e}")

        else:

            self.building_land = {}
            self.nodes_collection = {}
            self.boundary_collection = {}
            self.archetype_collection = {}
            self.id_list = [] #a way to be sure that all id stay unique inside DataSet
            self.d3_model = True #By default, DataSet is set as a 3D representation of the building. If 3D info are not given, it will be set as False (1D model)

        self.list_archetype_type = [name.replace("_types_scheme", "") for name in dir(archetype_schemes) if
                                    name.endswith('_scheme')]
        self.list_node_type = [name.replace("_scheme", "") for name in dir(node_schemes) if name.endswith('_scheme')]
        self.list_object_type = [name.replace("_scheme", "") for name in dir(object_schemes) if
                                 name.endswith('_scheme')]
        self.logs = logs
        self.assist_mode = assist_mode

    def generate_json(self):
        '''
        Export the complete building dataset
        Parameters
        ----------
        Returns
        -------
        json : dict,
        '''

        self.json = {
            "building_land" : self.building_land,
            "nodes_collection" : self.nodes_collection,
            "boundary_collection" : self.boundary_collection,
            "archetype_collection" : self.archetype_collection
        }

        return self.json

    def generate_unique_id(self, prefixe):
        '''
        generate a unique dataset id constructed on the following model {prefixe}_random number
        Parameters
        ----------
        prefixe : str,
            prefixe used for create the id
        Returns
        -------
        id : str,
            unique dataset id
        '''

        while True:  # Loop until a unique id is found
            random_number = random.randint(1, 9999)
            id = f"{prefixe}_{random_number}"
            if id not in self.id_list:
                self.id_list.append(id)
                return id

    def add_archetype(self, type_name, archetype_id = None, **inputs):
        '''Add an archetype to the type_name_collection in dataset
        Parameters
        ----------
        type_name : str,
            object type among the authorized list
        archetype_id : str (optional),
            unique string id
        inputs** (kwargs) (optional),
            all parameter added to add_archetype argument would be use to set type scheme parameter value instead of default values
        Returns
        -------
        archetype_id : str,
            id of the archetype added
        '''

        if type_name not in self.list_archetype_type:
            raise ValueError(f"{type_name} is not a available archetype or object type for COLIBRI dataset. Please choose your type_name among : {self.list_archetype_type}")

        if archetype_id is None :
            archetype_id = input("You can set your own archetype_id (string) to be easily use afterwards. We will only check that each id is unique. Do you want to set your archetype id ? If you want to generate a random id, type 'no', else type your id ==> ")
            if archetype_id == "no":
                archetype_id = self.generate_unique_id(f"{type_name}_archetype")
                print(f"Successfully set {type_name} archetype id to {archetype_id}\n -----------------------------") if self.logs else None
            elif archetype_id in self.id_list:
                archetype_id = self.generate_unique_id(f"{type_name}_archetype")
                print(f"The id given was already use. Set {type_name} archetype id to this id {archetype_id}") if self.logs else None


        needs_label = False
        if inputs is not None:
            if "label" in inputs:
                label = inputs["label"]
            else:
                needs_label = True
        else:
            needs_label = True
            inputs = {}

        if (needs_label):
            label = input("You can set your own label (string) for your archetype. It is not used in the calcul but will be display in front interface software. If you want to use the id also as label, type 'no', else type your label ==> ")
            if label == "no":
                label = archetype_id
            inputs["label"] = label
            print(f"Successfully set label to {label}") if self.logs else None

        archetype = Archetype(type_name,self, self.logs, **inputs)

        #Test if an archetype with the same characteristic already exists and if yes ask if we really wants to create a second one if this is the case
        is_archetype_already_exist = False
        if f"{type_name}_types" in self.archetype_collection.keys():
            for archetype_key, archetype_item in self.archetype_collection[f"{type_name}_types"].items():
                if check_dict_equality(archetype_item, archetype.data, keys_to_exclude=["label"]):
                    is_archetype_already_exist = True
                    same_archetype_id = archetype_key
                    same_archetype_label = archetype_item["label"]
                    break

            if is_archetype_already_exist:
                choice = input(f"A identical archetype already exist with the same properties : id '{same_archetype_id}' and label : '{same_archetype_label}'."
                      f"\n Do you want to use it (type 'yes') or keep create a new one with id {archetype_id} and label {label} (type 'no') ? ==> ")
                if choice == "yes":
                    return same_archetype_id

        #add a new archetype to the collection
        if f"{type_name}_types" not in self.archetype_collection.keys():
            self.archetype_collection[f"{type_name}_types"] = {}

        self.archetype_collection[f"{type_name}_types"][archetype_id] = archetype.data

        rapport = f"{type_name} archetype added successfully to dataset with id {archetype_id} and the following data : \n"
        rapport += f"{archetype.data}"
        rapport += "\n -----------------------------"

        print(rapport) if self.logs else None

        return archetype_id

    def check_id(self, id, type_name, mode = "archetype"):
        '''
        Check if a given object or archetype id exist in the dataset
        Parameters
        ----------
        id : str,
            id to test
        type_name : str,
            type of the object (boundary, ...)
        mode : str,
            choice between :
            - "archetype" : the id will be search among archetype id for the category type_name
            - "object" : the id will be search among object id for the category type_name


        Returns
        -------
        is_present : bool,
            True if id exist, False if not
        message : str,
            information about the existing keys

        '''
        message = ""
        if mode == "object":
            if type_name == "boundary":
                relevant_dict = self.boundary_collection
            elif type_name in ["space", "ponctual_junction", "boundary_condition", "linear_junction"]:
                relevant_dict = self.nodes_collection[f"{type_name}_collection"]
            else: #it is an object link to a boundary
                #need to scan id and make a specific return
                for boundary in self.boundary_collection.keys():
                    for object in boundary["object_collection"]:
                        if object["type"] == type_name and object["id"] == id:
                                is_present = True
                                message = f"{id} is present as an {type_name} object link to {boundary} boundary"
                                return is_present, message

                is_present = False
                message = f"{id} was not find as an existing {type_name} object link to a boundary"

        else: #it is an archetype
            relevant_dict = self.archetype_collection[f"{type_name}_types"]

        if (id in relevant_dict.keys()):
            is_present = True
            message = f"{id} is present among the existing id for {type_name} {mode} : {relevant_dict.keys()}"
        else:
            is_present = False
            message = f"{id} is NOT present among the existing id for {type_name} {mode} : {relevant_dict.keys()}"

        return is_present, message

    def warn_and_set_to_1d_model(self):
        '''Set datamodel to 1D model only'''
        warnings.warn(
            "WARNING : You don't use 2D/3D representation of your boundary by settings 'segment' parameter."
            "\nTherefore your data set model will set as 1D model only\n"
            "(no 3D representation, no known adjacency between boundary."
        )
        self.d3_model = False

    def calculate_segment_length(self, point1, point2):
        '''Calculate euclidian distance between two point [x,y]'''
        x1, y1 = point1
        x2, y2 = point2

        segment_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        return segment_length

    def create_segment_and_area_from_coordinates(self, ordered_coordinates_list = None, ordered_name_list = None):
        '''
        create segments and calculate area from given or ask coordinates
        Parameters
        ----------
        ordered_coordinates_list : list,
            list of x,y coordinates [[x,y],[x1,y1...] in lambert93 (meters unit) used to describe the shape of a boundary in a plane reference coordinnates systems [0,0] is always one of the point of the boundary shape (the bottom left).
            Important : coordinates needs to be set in CLOCKWISE order.

        Returns
        -------
        segments : list,
            list of initiate segment (without junction yet) in COLIBRI boundary segment format

        '''

        if ordered_coordinates_list is None:
            user_input = "start"
            ordered_coordinates_list = [[0,0]]
            print("\nPlease enter each coordinates in the format [x, y] to describe the shape of the boundary in its 2D reference frame."
                                   "\nPLEASE RESPECT THE CLOCKWISE ORDER OF THE POINT BY FOLLOWING SEGMENT BETWEEN EACH POINT.\nTYPE '' OR 'end' when finished."
                                   "\nThe first point always starts with [0, 0] and has already been provided (no need to set it again)."
                                   "\nPlace the other points relative to this one, ideally considering it as the bottom-left point of your shape (in order to have positive x and y values ideally)")
            i=2
            print("Point number 1 : [0,0] saved \n")
            while (user_input not in ["end",""]):
                user_input = input(f"Please enter point number {i} in the format [x, y] (type 'end' if you have entered all points) ==> ")
                try:
                    if isinstance(ast.literal_eval(user_input), list):
                        ordered_coordinates_list.append(ast.literal_eval(user_input))
                        print(f"Point number {i} : {ast.literal_eval(user_input)} saved \n") if self.logs else None
                        i+=1

                except Exception as e:
                    print(e)
                    if user_input not in ["end",""]:
                        print(
                            f"{user_input} is not a valid coordinnates or a valid end of input. If you have finished setting your coordinnates, type 'end' in the next prompt ==> ")

        #create segment
        segments = []
        no_to_all = False
        for i in range(len(ordered_coordinates_list)):
            if i==len(ordered_coordinates_list) -1:
                point1 = ordered_coordinates_list[i]
                point2 = ordered_coordinates_list[0]
            else:
                point1 = ordered_coordinates_list[i]
                point2 = ordered_coordinates_list[i+1]

            if ordered_name_list is None:
                if not no_to_all:
                    segment_id = input(f"Do you want to set/name the unique id of the segment between {point1} and {point2} ? If you want to generate a random id, type 'no' (just for this segment) or 'no to all' (for all segment), else type your id ==> ")

                if segment_id == "no to all":
                    no_to_all = True
                if segment_id =="no" or no_to_all:
                    segment_id = self.generate_unique_id("segment")
            else:
                if len(ordered_name_list) != len(ordered_coordinates_list):
                    raise ValueError("The list of segment name is not complete compared to the list of points provided."
                                     "\nIt needs to have the same length because nb_segment = nb_points in any closed form.")
                else:
                    segment_id = ordered_name_list[i]

            segments.append(
                {
                    "id" : segment_id,
                    "points" : [point1,point2],
                    "junction" : None,
                    "length" : self.calculate_segment_length(point1, point2)
                }
            )

        #calculate area
        def calculate_area(points_list):
            '''calculate area from list of shape points'''
            # Ensure the polygon is closed by adding the first point to the end of the list
            points = copy.deepcopy(points_list)
            points.append(points[0])

            area = 0
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                area += (x1 * y2) - (x2 * y1)
            area = abs(area) / 2

            return area

        area = calculate_area(ordered_coordinates_list)

        print(f"Segments created : {segments}\nCorresponding area : {area} m²") if self.logs else None

        return segments, area

    def add_node(self, node_type, node_id = None, **node_inputs):
        '''

        Parameters
        ----------
        node_type : str,
            type of node to create (use dataset.describe() to know the complete list of node) among : space, linear_junction,...
        node_id : str (optional),
            unique string id
        **node_inputs (optional): dict,
            dict with all the node properties and associated value that user want to set

        Returns
        -------

        '''

        if node_type not in self.list_node_type:
            raise ValueError(f"{node_type} is not a available node type for COLIBRI dataset. Please choose your type_name among : {self.list_node_type}")

        if node_id is None :
            node_id = input("You can set your own node_id (string) to be easily use afterwards. We will only check that each id is unique.\nDo you want to set your node id ? If you want to generate a random id, type 'no', else type your id ==> ")
            if node_id == "no":
                node_id = self.generate_unique_id(f"{node_type}")
                print(f"Successfully set {node_type} archetype id to {node_id}\n -----------------------------") if self.logs else None
            elif node_id in self.id_list:
                node_id = self.generate_unique_id(f"{node_type}")
                print(f"The id given was already use. Set {node_type} node id to this id {node_id}") if self.logs else None

        node = Node(node_type, self, self.logs, **node_inputs)

        if f"{node.data['node_type']}_collection" not in self.nodes_collection.keys():
            self.nodes_collection[f"{node.data['node_type']}_collection"] = {}

        self.nodes_collection[f"{node_type}_collection"][node_id] = node.data

    def add_boundary(self, boundary_id = None, archetype_id = None, boundary_inputs = None, archetype_inputs = None):
        '''

        Parameters
        ----------
        boundary_id : str,
            unique id for the boundary
        archetype_id : str,
            unique id for the archetype of the boundary (properties that can be factorized/mutualised between boundary objects)
        boundary_inputs : dict,
            dict with all the unique boundary properties (orientation, area, segments...) name and associated value that user want to set
            Notes : you can use "points_coordinates" to provide a list of coordinates points of the boundary shape of side 1 in the following format [[x1,y1],[x2,y2]...] with the first point x1,y1 [0,0] and points declared in clockwise order (important)
        archetype_inputs : dict,
            dict with all the factorize/archetype boundary properties (layers,...) name and associated value that user want to set

        Returns
        -------

        '''

        if boundary_id is None:
            boundary_id = input(
                "You can set your own boundary_id (string) to be easily use afterwards. We will only check that each id is unique. Do you want to set your boundary id ? If you want to generate a random id, type 'no', else type your id ==> ")
            if boundary_id == "no":
                boundary_id = self.generate_unique_id("boundary")
                print(f"Successfully set boundary id to {boundary_id}") if self.logs else None
            elif boundary_id in self.id_list:
                boundary_id = self.generate_unique_id("boundary")
                print(f"The id given was already use. Set boundary id to this id {boundary_id}") if self.logs else None

        if "segments" not in boundary_inputs.keys():
            if "area" not in boundary_inputs.keys():
                shape_choice = input("Please provide at least an area (type 'area') for the boundary or describe its shape using x,y meter unit coordinates (type 'coords') ==> ")
                if shape_choice !="coords":
                    if self.d3_model:
                        self.warn_and_set_to_1d_model()
                    area = input("Please, type the area of the boundary in m² ==> ")
                    boundary_inputs[
                        "segments"] = None  # we set segments to None because we don't use the 2D/3D representation of the building
                    boundary_inputs["area"] = float(area)

                else:
                    if "points_coordinates" in boundary_inputs.keys():
                        if isinstance(boundary_inputs["points_coordinates"], list) and len(boundary_inputs["points_coordinates"][0])==2:
                            coordinates = boundary_inputs["points_coordinates"]
                        else:
                            raise ValueError("points_coordinates doesn't respect the expected format. Please to provide a list of coordinates points of the boundary side 1 shape in the following format [[x1,y1],[x2,y2]...] with the first point x1,y1 [0,0] and points declared in clockwise order when looking at side 1 (important)")
                    else:
                        coordinates = None

                    boundary_inputs["segments"], boundary_inputs["area"] = self.create_segment_and_area_from_coordinates(coordinates)

            elif self.d3_model:
                self.warn_and_set_to_1d_model()
            boundary_inputs["segments"] = None #we set segments to None because we don't use the 2D/3D representation of the building

        boundary = Boundary(self, **boundary_inputs)

        if archetype_id is None:
            if f"{boundary.type_name}_types" not in self.archetype_collection.keys():
                self.archetype_collection[f'{boundary.type_name}_types'] = {}
                archetype_id = self.add_archetype(boundary.type_name, archetype_id = None, **archetype_inputs)
            else:
                prompt = "No boundary archetype (type_id) have been link to this boundary. Do you wish to link it to an existant one or create a new one ?\n " \
                     "type 'new' for a new one or type the id_name among the existing boundary archetype type :\n"
                for arch_id in self.archetype_collection[f"{boundary.type_name}_types"].keys():
                    prompt += f"- '{arch_id}' (label : {self.archetype_collection[f'{boundary.type_name}_types'][arch_id]['label']} )"

                archetype_id = input(prompt +" ==> ")

            if archetype_id not in self.archetype_collection[f'{boundary.type_name}_types'].keys() or archetype_id == "new": #need to create archetype
                archetype_id = self.add_archetype(type_name = "boundary", archetype_id=None, **archetype_inputs)

        #reference type_id to boundary
        if archetype_id in self.archetype_collection[f'{boundary.type_name}_types'].keys():
            boundary.data["type_id"] = archetype_id
        else:
            raise ValueError(f"{archetype_id} is not an available archetype id. Please start again and create a new one or choose among : {list(self.archetype_collection[f'{boundary.type_name}_types'].keys())}")

        #check if space connexion to boundary exist and is correct :
        for side in ["side_1","side_2"]:
            available_node = ["exterior", "ground"]
            for node_type in self.nodes_collection.keys():
                available_node += list(self.nodes_collection[node_type].keys())
            if boundary.data[side] not in available_node:
                raise ValueError(f"{boundary.data[side]} is not an available node object (space or boundary_condition) authorized for side.\nPlease create it or correct it and start again with the boundary condition.")

        self.boundary_collection[boundary_id] = boundary.data

        print(f"Successfully created and added boundary with id {boundary_id} to dataset boundary collection w: {boundary.data} \n -----------------------------") if self.logs else None

    def add_object_to_boundary(self, boundary_id, type_name = None, object_archetype_id = None, object_archetype_inputs = None, **object_inputs):
        '''
        add a object/element to an existing boundary
        Parameters
        ----------
        boundary_id : str,
            id of the boundary
        type_name : str,
            name of the archetype type of object (terminal vent, window ...) we want to add to the boundary
        object_archetype_id : str,
            id of the archetype type if already exist
        object_archetype_inputs : dict,
            dict with all the archetype properties and associated value that user want to set if archetype is not already existing
        object_inputs : dict,
            dict with all the unique object properties (on_side, x_relative_position...) and associated value that user want to set


        Returns
        -------

        '''

        if object_inputs is None:
            object_inputs = {}

        if (type_name is None) or type_name not in self.list_archetype_type:
            type_name = input(f"Please choose a correct object type among {self.list_archetype_type}")

            if type_name not in self.list_archetype_type:
                raise ValueError(f"{type_name} is not a valid object. Please retry add_object_to_boundary.")

        object_inputs["type"] = type_name

        valid_id, message = self.check_id(boundary_id, "boundary", mode = "object")
        if not valid_id:
            raise ValueError(message)

        if "id" not in object_inputs.keys():
            object_inputs["id"] = input(
                "You can set your own id (string) to be easily use afterwards. We will only check that each id is unique."
                "\nDo you want to set your object id ? If you want to generate a random id, type 'no', else type your id ==> ")
            if object_inputs["id"] == "no":
                object_inputs["id"] = self.generate_unique_id(type_name)
                print(f"Successfully set {type_name} object id to {object_inputs['id']}") if self.logs else None
            elif object_inputs["id"] in self.id_list:
                object_inputs["id"] = self.generate_unique_id(type_name)
                print(f"The id given was already use. Set boundary id to this id {object_inputs['id']}") if self.logs else None

        if object_archetype_id is not None:

            valid_id, message = self.check_id(object_archetype_id, type_name, mode="archetype")
            if not valid_id:
                raise ValueError(message)
            need_to_create_archetype = False

        else:
            object_archetype_id = input(f"Do you want to link your object {type_name} to an existing archetype id among :\n"
                                        f"{self.archetype_collection[f'{type_name}_collection'].keys()} ?"
                                        f"\n If not, type a new id string and we will proceed to the creation of a new archetype element (with the typed id) in addition to the link of the object to the boundary")
            if object_archetype_id in self.archetype_collection[f'{type_name}_collection'].keys():
                print(f"object linked to existing archetype {type_name} : {object_archetype_id}") if self.logs else None
                need_to_create_archetype = False

            else:
                need_to_create_archetype = True

        if (need_to_create_archetype):
            object_archetype_id = self.add_archetype(type_name, object_archetype_id, **object_archetype_inputs)

        # ask to link to a archetype or create a new one
        object_inputs["type_id"] = object_archetype_id
        object_inputs["type"] = type_name
        object = Object(dataset=self, logs = self.logs, **object_inputs)

        #add object to boundary "object collection"
        self.boundary_collection[boundary_id]["object_collection"].append(object.data)

        print(f"Successfully added {type_name} object to boundary {boundary_id} with the following data :\n{object.data} \n -----------------------------") if self.logs else None

    def link_boundaries(self, boundary_list, segment_list_id : None, **inputs):
        '''
        Link multiple boundaries through a linear junction and a common segment.
        By construction of boundary, the connected segments have necessary the same length
        Parameters
        ----------
        boundary_list : list,
            list of str id of boundaries
        segment_list_id : list (optional),
            list of corresponding segment id for each boundary (same order of declaration as in boundary_list) concerned by the junction
        inputs : dict (optional),
            dict with all the node (linear_junction) properties and associated value that user want to set
        Returns
        -------

        '''

        #check user input
        for boundary_id in boundary_list:
            valid_boundary, message = self.check_id(boundary_id, "boundary", "object")
            if not valid_boundary:
                raise ValueError(message)


        if segment_list_id is None:
            segment_list_id = []
            for boundary_id in boundary_list:

                ask = f"Please choose the concerned boundary segment id for {boundary_id} among :"
                for segment in self.boundary_collection[boundary_id]["segments"]:
                    ask += f"- '{segment['id']}' ({segment['points']})"
                choose_segment = input(ask)

                if ask not in self.boundary_collection[boundary_id]["segments"]:
                    raise ValueError(f"{ask} is not a valid id for segment for boundary {boundary_id}")

        segment_list = []
        for i in range(len(boundary_list)):
            for segment in self.boundary_collection[boundary_list[i]]["segments"]:
                print(f"segment_id {segment['id']} and we search {segment_list_id[i]}")
                if segment["id"] == segment_list_id[i]:
                    choose_segment = segment
                    break
            if len(segment_list)>0 : #a first segment have already been set
                if choose_segment["length"] != segment_list[0]["length"]:
                    raise ValueError(f"Joint segment MUST HAVE the same length. {segment_list[0]['length']} meters excepted, {choose_segment['id']} is {choose_segment['length']} meters long")
            try:
                segment_list.append(choose_segment)
            except:
                raise ValueError(f"No segment with the id {segment_list_id[i]} was found in {boundary_list[i]} boundary")

        if inputs is None:
            inputs={}
        elif "length" in inputs.keys():
            if inputs["length"] != segment_list[0]["length"]:
                warnings.warn(f"The given length in inputs {inputs['length']} is not compatible with the length of segments choosen : {segment_list[0]['length']}. We keep the segment length : {segment_list[0]['length']}")

        #create linear junction
        inputs["length"] = segment_list[0]["length"]

        if "id" not in inputs.keys():
            inputs["id"] = input(
                "You can set your own id (string) to be easily use afterwards. We will only check that each id is unique."
                "\nDo you want to set your linear_junction id ? If you want to generate a random id, type 'no', else type your id ==> ")
            if inputs["id"] == "no":
                inputs["id"] = self.generate_unique_id(inputs)
                print(f"Successfully set linear object id to {inputs['id']}") if self.logs else None
            elif inputs["id"] in self.id_list:
                inputs["id"] = self.generate_unique_id("linear_junction")
                print(f"The id given was already use. Set linear id to this id {inputs['id']}") if self.logs else None

        node = Node("linear_junction", self, **inputs)

        if f"{node.data['node_type']}_collection" not in self.nodes_collection.keys():
            self.nodes_collection[f"{node.data['node_type']}_collection"] = {}

        self.nodes_collection[f"{node.data['node_type']}_collection"][ inputs["id"]] = node.data

        #reference node inside segment
        for i in range(len(boundary_list)):
            for segment in self.boundary_collection[boundary_list[i]]["segments"]:
                if segment["id"] == segment_list[i]["id"]:
                    segment["junction"] = {"nodes_type" : "linear_junction", "nodes_id" :inputs["id"]}
                    break

        print(
            f"Successfully created linear_junction {inputs['id']} with properties : {node.data} \n -----------------------------") if self.logs else None

    def connect_objects_to_node_junction(self, objects_linked_ids, junction_type, junction_id : None, **inputs):
        '''
        Create or add a list of object to an existing node junction
        Parameters
        ----------
        objects_linked_ids : list,
            list of object id
        junction_type : string,
            type of node junction among ponctual_junction, linear_junction... (any existing node type)
        junction_id : string,
            id of the junction
        inputs : dict,
            dict with all the node properties and associated value that user want to set

        Returns
        -------

        '''

        junction = Node(junction_type, self, **inputs)

        if junction_id is None:
           junction_id = input(
               "You can set your own id (string) to be easily use afterwards. We will only check that each id is unique."
               "\nDo you want to set your object id ? If you want to generate a random id, type 'no', else type your id ==> ")
           if junction_id == "no":
               junction_id = self.generate_unique_id(junction_type)
               print(f"Successfully set {junction_type} object id to {junction_id}") if self.logs else None
           elif junction_id in self.id_list:
               print(f"WARNING : The id given already exist. We assumed you wanted to link the object list to {junction_type} with the id {junction_id}") if self.logs else None



        if junction_id not in self.nodes_collection[f"{junction_type}_collection"]:
            self.nodes_collection[f"{junction_type}_collection"][junction_id] = junction.data

        #update object linked
        id_count = []
        for boundary in self.boundary_collection.keys():
            for object in boundary["object_collection"]:
                if object["id"] in objects_linked_ids:
                    junction_link = {'nodes_type' : junction_type,'nodes_id' : junction_id}
                    if junction_link not in object["junctions"]: #to avoid multiple same junction
                        object["junctions"].append(junction_link)
                        id_count.append(object["id"])

        print(f"Successfully add junction to the following object => {id_count}") if self.logs else None
        not_found = list(set(objects_linked_ids) - set(id_count))
        if len(not_found)>0:
            warnings.warn(f"WARNING The following objects were not found and connected => {not_found}")

    def describe(self, type_name = None, parameter_name = None, object_type = None):
        '''
        Provide help and documentation about dataset object parameters
        Parameters
        ----------
        type_name : str (optional),
            string name of object, archetype or node type
        parameter_name : str (optional),
            string name of a parameter of the given object type (type_name)
        type : str,
            indicate the object_type (in which scheme we want to search). If not set, we find the first one.
            possible values : "archetype", "object", "node"

        Returns
        -------
        documentation : str,
            return print documentation on the parameter name or all parameters if parameter_name = None
        '''

        if type_name is None:
            comment = f"COLIBRI dataset can be composed of the following objects, archetypes and nodes : \n"
            #object
            comment += f"COLIBRI object : \n"
            schemes = [getattr(object_schemes, name + "_scheme") for name in self.list_object_type]
            for scheme in schemes:
                comment += f"- {scheme['type']} : {scheme['info']} \n"
            comment += "\n-----------------------------"

            # archetype
            comment += f"COLIBRI archetype (where object properties are factorized) : \n"
            schemes = [getattr(archetype_schemes, name + "_types_scheme") for name in self.list_archetype_type]
            for scheme in schemes:
                comment += f"- {scheme['type']} : {scheme['info']} \n"
            comment += "\n-----------------------------"

            # nodes
            comment += f"COLIBRI nodes (volumes/spaces, linears or points that connect objects) : \n"
            schemes = [getattr(node_schemes, name + "_scheme") for name in self.list_node_type]
            for scheme in schemes:
                comment += f"- {scheme['type']} : {scheme['info']} \n"
            comment += "\n-----------------------------"
            comment += "\nTo learn more about each object parameter : Use describe('type_name' = object name) \n"
            comment += "To learn more about a specific parameter of a given object : Use describe('type_name' = object name,'parameter_name' = name of the parameter) \n" \
                           "To learn more about the function you can use to create the Colibri dataset, use .doc()"

            print(comment)

        else:
            if object_type is not None:
                if object_type == "archetype":
                    types_to_try = [Archetype]
                elif object_type == "object" and type_name == "boundary":
                    types_to_try = [Boundary]
                elif object_type == "object":
                    types_to_try = [Object]
                elif object_type == "node":
                    types_to_try = [Node]
                else:
                    raise ValueError(f"{object_type} is not a valid COLIBRI type of element. Please choose among the following list : 'archetype', 'object', 'node'")
            else:
                types_to_try = [Archetype, Object, Node]

            for Type in types_to_try:
                try:
                    return Type(type_name, logs = False).describe(parameter_name)
                except Exception:
                    try:
                        return Type(logs=False).describe(parameter_name)
                    except Exception:
                        pass

            # If all tentatives have failed
            raise ValueError(f"{type_name} or {parameter_name} doesn't exist in current COLIBRI dataset")

    def doc(self):
        '''Complete doc of DataSet class'''
        for name, func in inspect.getmembers(self, inspect.ismethod):
            print(f"{name} : {func.__doc__}")

if __name__ == '__main__':

    from pkg_resources import resource_filename
    import json
    geojson_path = resource_filename('datamodel', 'examples/house_1.json')

    with open(geojson_path, encoding='utf-8') as json_file:
        geojson = json.load(json_file)

    model = DataSet(geojson = geojson)


