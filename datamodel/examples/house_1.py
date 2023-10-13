from datamodel.utils import dataset_classes as sc
from unittest.mock import patch
import json

#create house_1 COLIBRI DataSet
house_1 = sc.DataSet()

with patch('builtins.input', return_value='default to all'): #we apply default value for any parameter not fixed when DataSet "ask" question to user for missing data

    #region CREATE ARCHETYPES
    ##Layers
    # To know all properties use sc.Scheme("layer").describe() or sc.Scheme("layer").describe("SPECIFIC PARAMETER NAME")
    house_1.add_archetype("layer", archetype_id = "beton_1", label = "béton 20cm", thickness = 0.2) #default thermal value are already set to concrete values
    house_1.add_archetype("layer", archetype_id = "isolant_1", label = "isolant 15cm pour mur verticaux", thickness = 0.15,
                          thermal_conductivity = 0.035, specific_heat= 1.030, density = 25, material_type = "insulation", constitutive_material_type = "rock wood")
    house_1.add_archetype("layer", archetype_id="isolant_toiture", label="isolant 10cm pour toiture", thickness=0.1,
                          thermal_conductivity=0.035, specific_heat=1.030, density=25, material_type="insulation", constitutive_material_type="rock wood")
    house_1.add_archetype("layer", archetype_id="isolant_plancher", label="isolant 5cm pour plancher", thickness=0.05,
                          thermal_conductivity=0.035, specific_heat=1.030, density=25, material_type="insulation", constitutive_material_type="rock wood")
    house_1.add_archetype("layer", archetype_id="vide_10", label="vide 10cm", thickness=0.1,
                          thermal_conductivity=0.025, specific_heat=1, density=1.293, material_type="insulation", constitutive_material_type="air")
    house_1.add_archetype("layer", archetype_id="ba_13", label="BA13", thickness=0.013,
                          thermal_conductivity=0.25, specific_heat=1, density=850, material_type="plaster",
                          constitutive_material_type="plaster")

    ##boundary type (walls, roof, floor...)
    house_1.add_archetype("boundary", archetype_id="mur_exterieur_1", label="Mur exterieur",
                              layers=[{"type": "layer", "type_id": "isolant_1"}, {"type": "layer", "type_id": "beton_1"}])

    house_1.add_archetype("boundary", archetype_id="toiture_1", label="Plancher haut",
                              layers=[{"type": "layer", "type_id": "beton_1"}, {"type": "layer", "type_id": "isolant_toiture"}])

    house_1.add_archetype("boundary", archetype_id="plancher_1", label="Plancher bas",
                              layers=[{"type": "layer", "type_id": "isolant_plancher"}, {"type": "layer", "type_id": "beton_1"}])

    house_1.add_archetype("boundary", archetype_id="cloison_1", label="Cloison BA13",
                              layers=[{"type": "layer", "type_id": "ba_13"},
                                      {"type": "layer", "type_id": "vide_10"},
                                      {"type": "layer", "type_id": "ba_13"}])

    ##window type #TODO : the scheme is currently empty from physics properties. Just need to complete it in archetype_schemes and it will be applied here.
    house_1.add_archetype("window", archetype_id="typical_window", label = "fenetre 1 vantail")

    ##door type #TODO : the scheme is currently empty from physics properties. Just need to complete it in archetype_schemes and it will be applied here.
    house_1.add_archetype("door", archetype_id="typical_door", label="porte classique")

    #endregion

    #region CREATE SPACES
    house_1.add_node("space","living_room_1",label = "salon", reference_area = 20.9, volume = 20.9*2.5, altitude = 0, use = "living room")
    house_1.add_node("space", "kitchen_1", label="cuisine", reference_area=9.52, volume=9.52*2.5, altitude=0, use="kitchen")

    #endregion

    #region CREATE BOUNDARIES
    #NOTE : "Important : coordinates needs to be set in CLOCKWISE order regarding side_1 of the boundary" (explain also in documentation with for example : house_1.Scheme("boundary").describe("segments"))

    ##mur_salon_sud_1
    segments_mur_salon_sud, area_mur_salon_sud = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 2.5], [6, 2.5], [6, 0]],
        ["s_mur_salon_sud_et_mur_salon_ouest", "s_mur_salon_sud_plafond", "s_mur_salon_sud_et_mur_cuisine_sud",
         "s_mur_salon_sud_plancher"])
    house_1.add_boundary(boundary_id="mur_salon_sud_1", archetype_id="mur_exterieur_1",
                         boundary_inputs={"label": "Mur salon sud", "azimuth": 180, "side_1": "exterior",
                                          "side_2": "living_room_1", "tilt": 90, "segments": segments_mur_salon_sud,
                                          "area": area_mur_salon_sud, "3d_origin" : (0,0,0)})

    ##mur_salon_ouest_1
    segments_mur_salon_ouest, area_mur_salon_ouest = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 2.5], [4, 2.5], [4, 0]],
        ["s_mur_salon_ouest_et_mur_salon_nord", "s_mur_salon_ouest_plafond", "s_mur_salon_ouest_et_mur_salon_sud",
         "s_mur_salon_ouest_plancher"])
    house_1.add_boundary(boundary_id="mur_salon_ouest_1", archetype_id="mur_exterieur_1",
                         boundary_inputs={"label": "Mur salon ouest", "azimuth": 270, "side_1": "exterior",
                                          "side_2": "living_room_1", "tilt": 90, "segments": segments_mur_salon_ouest,
                                          "area": area_mur_salon_ouest, "3d_origin" : (0,4,0)})

    ##mur_salon_nord_1
    segments_mur_salon_nord, area_mur_salon_nord = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 2.5], [6, 2.5], [6, 0]],
        ["s_mur_salon_nord_et_mur_salon_est", "s_mur_salon_nord_plafond", "s_mur_salon_nord_et_mur_salon_ouest",
         "s_mur_salon_nord_plancher"])
    house_1.add_boundary(boundary_id="mur_salon_nord_1", archetype_id="mur_exterieur_1",
                         boundary_inputs={"label": "Mur salon nord", "azimuth": 0, "side_1": "exterior",
                                          "side_2": "living_room_1", "tilt": 90, "segments": segments_mur_salon_nord,
                                          "area": area_mur_salon_nord, "3d_origin" : (6,4,0)})

    ##mur_salon_est_1
    segments_mur_salon_est, area_mur_salon_est = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 2.5], [2, 2.5], [2, 0]],
        ["s_mur_salon_est_et_mur_salon_cuisine", "s_mur_salon_est_plafond", "s_mur_salon_est_et_mur_salon_nord",
         "s_mur_salon_est_plancher"])
    house_1.add_boundary(boundary_id="mur_salon_est_1", archetype_id="mur_exterieur_1",
                         boundary_inputs={"label": "Mur salon nord", "azimuth": 90, "side_1": "exterior",
                                          "side_2": "living_room_1", "tilt": 90, "segments": segments_mur_salon_est,
                                          "area": area_mur_salon_est, "3d_origin": (6, 2, 0)})

    ##mur_salon_cuisine
    segments_mur_salon_cuisine, area_mur_salon_cuisine = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 2.5], [2, 2.5], [2, 0]],
        ["s_mur_salon_cuisine_et_mur_salon_sud", "s_mur_salon_cuisine_plafond", "s_mur_salon_cuisine_et_mur_salon_est",
         "s_mur_salon_cuisine_plancher"])
    house_1.add_boundary(boundary_id="mur_salon_cuisine", archetype_id="cloison_1",
                         boundary_inputs={"label": "Mur salon nord", "azimuth": 90, "side_1": "kitchen_1",
                                          "side_2": "living_room_1", "tilt": 90, "segments": segments_mur_salon_cuisine,
                                          "area": area_mur_salon_cuisine, "3d_origin": (6, 0, 0)})

    ##mur_cuisine_nord_1
    segments_mur_cuisine_nord, area_mur_cuisine_nord = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 2.5], [6, 2.5], [6, 0]],
        ["s_mur_cuisine_nord_et_mur_cuisine_est", "s_mur_cuisine_nord_plafond", "s_mur_cuisine_nord_et_mur_salon_est",
         "s_mur_cuisine_nord_plancher"])
    house_1.add_boundary(boundary_id="mur_cuisine_nord_1", archetype_id="mur_exterieur_1",
                         boundary_inputs={"label": "Mur salon nord", "azimuth": 0, "side_1": "exterior",
                                          "side_2": "kitchen_1", "tilt": 90, "segments": segments_mur_cuisine_nord,
                                          "area": area_mur_cuisine_nord, "3d_origin": (12, 2, 0)})

    ##mur_cuisine_est_1
    segments_mur_cuisine_est, area_mur_cuisine_est = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 2.5], [2, 2.5], [2, 0]],
        ["s_mur_cuisine_est_et_mur_cuisine_sud", "s_mur_cuisine_est_plafond", "s_mur_cuisine_est_et_mur_cuisine_nord",
         "s_mur_cuisine_est_plancher"])
    house_1.add_boundary(boundary_id="mur_cuisine_est_1", archetype_id="mur_exterieur_1",
                         boundary_inputs={"label": "Mur salon nord", "azimuth": 90, "side_1": "exterior",
                                          "side_2": "kitchen_1", "tilt": 90, "segments": segments_mur_cuisine_est,
                                          "area": area_mur_cuisine_est, "3d_origin": (12, 0, 0)})

    ##mur_cuisine_sud_1
    segments_mur_cuisine_sud, area_mur_cuisine_sud = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 2.5], [6, 2.5], [6, 0]],
        ["s_mur_cuisine_sud_et_mur_salon_sud", "s_mur_cuisine_sud_plafond", "s_mur_cuisine_sud_et_mur_cuisine_est",
         "s_mur_cuisine_sud_plancher"])
    house_1.add_boundary(boundary_id="mur_cuisine_sud_1", archetype_id="mur_exterieur_1",
                         boundary_inputs={"label": "Mur salon nord", "azimuth": 180, "side_1": "exterior",
                                          "side_2": "kitchen_1", "tilt": 90, "segments": segments_mur_cuisine_sud,
                                          "area": area_mur_cuisine_sud, "3d_origin": (6, 0, 0)})

    ##plancher haut salon
    segments_plafond_salon, area_plafond_salon = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 4], [6, 4], [6, 2], [6, 0]],
        ["s_plafond_mur_salon_ouest", "s_plafond_mur_salon_nord", "s_plafond_mur_salon_est", "s_plafond_salon_mur_cuisine", "s_plafond_mur_salon_sud"])
    house_1.add_boundary(boundary_id="plafond_salon", archetype_id="toiture_1",
                         boundary_inputs={"label": "Plafond salon", "azimuth": 0, "side_1": "exterior",
                                          "side_2": "living_room_1", "tilt": 0, "segments": segments_plafond_salon,
                                          "area": area_plafond_salon, "3d_origin": (0, 0, 2.5)})

    ##plancher bas salon
    segments_plancher_salon, area_plancher_salon = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 4], [6, 4], [6, 2], [6, 0]],
        ["s_plancher_mur_salon_ouest", "s_plancher_mur_salon_nord", "s_plancher_mur_salon_est",
         "s_plancher_mur_salon_cuisine", "s_plancher_mur_salon_sud"])
    house_1.add_boundary(boundary_id="plancher_salon", archetype_id="plancher_1",
                         boundary_inputs={"label": "Plancher salon", "azimuth": 0, "side_1": "living_room_1",
                                          "side_2": "ground", "tilt": 180, "segments": segments_plancher_salon,
                                          "area": area_plancher_salon, "3d_origin": (0, 0, 0)})

    ##plancher haut cuisine
    segments_plafond_cuisine, area_plafond_cuisine = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 2], [6, 2], [6, 0]],
        ["s_plafond_cuisine_mur_salon_cuisine", "s_plafond_mur_cuisine_nord", "s_plafond_mur_cuisine_est",
         "s_plafond_mur_cuisine_sud"])
    house_1.add_boundary(boundary_id="plafond_cuisine", archetype_id="toiture_1",
                         boundary_inputs={"label": "Plafond cuisine", "azimuth": 0, "side_1": "exterior",
                                          "side_2": "kitchen_1", "tilt": 0, "segments": segments_plafond_cuisine,
                                          "area": area_plafond_cuisine, "3d_origin": (0, 6, 2.5)})

    ##plancher haut cuisine
    segments_plancher_cuisine, area_plancher_cuisine = house_1.create_segment_and_area_from_coordinates(
        [[0, 0], [0, 2], [6, 2], [6, 0]],
        ["s_plancher_mur_salon_cuisine", "s_plancher_mur_cuisine_nord", "s_plancher_mur_cuisine_est",
         "s_plancher_mur_cuisine_sud"])
    house_1.add_boundary(boundary_id="plancher_cuisine", archetype_id="plancher_1",
                         boundary_inputs={"label": "Plafond cuisine", "azimuth": 0, "side_1": "kitchen_1",
                                          "side_2": "ground", "tilt": 0, "segments": segments_plancher_cuisine,
                                          "area": area_plancher_cuisine, "3d_origin": (0, 6, 2.5)})

    #endregion

    #region ADD OBJECT TO BOUNDARIES
    ##windows
    house_1.add_object_to_boundary(boundary_id="mur_salon_ouest_1", type_name="window", object_archetype_id="typical_window",
                                   id = "win_2", x_relative_position= 1, y_relative_position = 1, on_side= "side_1_to_side_2")
    house_1.add_object_to_boundary(boundary_id="mur_salon_ouest_1", type_name="window",
                                  object_archetype_id="typical_window",
                                  id="win_1", x_relative_position=3, y_relative_position=1, on_side="side_1_to_side_2")

    house_1.add_object_to_boundary(boundary_id="mur_cuisine_nord_1", type_name="window",
                                   object_archetype_id="typical_window",
                                   id="win_3", x_relative_position=4, y_relative_position=1, on_side="side_2_to_side_1") #Notes : you see on the plan that windows are incorporated differently than for win_1 and win_2, therefore on_side = "side_2_to_side_1"
    house_1.add_object_to_boundary(boundary_id="mur_cuisine_est_1", type_name="window",
                                   object_archetype_id="typical_window",
                                   id="win_4", x_relative_position=0.7, y_relative_position=1, on_side="side_2_to_side_1")

    #doors
    house_1.add_object_to_boundary(boundary_id="mur_salon_cuisine", type_name="door",
                                   object_archetype_id="typical_door",
                                   id="win_4", x_relative_position=0.6, y_relative_position=0,
                                   on_side="side_1_to_side_2")

    #endregion

    #region CONNECT BOUNDARIES AND CREATE ASSOCIATED NODES

    ##between walls : vertical linear junction
    house_1.link_boundaries(boundary_list = ["mur_salon_sud_1","mur_salon_ouest_1"],
                            segment_list_id=["s_mur_salon_sud_et_mur_salon_ouest", "s_mur_salon_ouest_et_mur_salon_sud"],
                            id = "j_mur_salon_sud_et_mur_salon_ouest")
    house_1.link_boundaries(boundary_list=["mur_salon_ouest_1", "mur_salon_nord_1"],
                            segment_list_id=["s_mur_salon_ouest_et_mur_salon_nord", "s_mur_salon_nord_et_mur_salon_ouest"],
                            id = "j_mur_salon_ouest_et_mur_salon_nord")
    house_1.link_boundaries(boundary_list=["mur_salon_nord_1", "mur_salon_est_1"],
                            segment_list_id=["s_mur_salon_nord_et_mur_salon_est", "s_mur_salon_est_et_mur_salon_nord"],
                            id = "j_mur_salon_nord_et_mur_salon_est")
    house_1.link_boundaries(boundary_list=["mur_salon_est_1","mur_cuisine_nord_1", "mur_salon_cuisine"],
                            segment_list_id=["s_mur_salon_est_et_mur_salon_cuisine", "s_mur_cuisine_nord_et_mur_salon_est", "s_mur_salon_cuisine_et_mur_salon_est"],
                            id = "j_mur_salon_est_et_mur_salon_cuisine")
    house_1.link_boundaries(boundary_list=["mur_cuisine_nord_1", "mur_cuisine_est_1"],
                            segment_list_id=["s_mur_cuisine_nord_et_mur_cuisine_est", "s_mur_cuisine_est_et_mur_cuisine_nord"],
                            id = "j_mur_cuisine_nord_et_mur_cuisine_est")
    house_1.link_boundaries(boundary_list=["mur_cuisine_est_1", "mur_cuisine_sud_1"],
                            segment_list_id=["s_mur_cuisine_est_et_mur_cuisine_sud","s_mur_cuisine_sud_et_mur_cuisine_est"],
                            id = "j_mur_cuisine_est_et_mur_cuisine_sud")
    house_1.link_boundaries(boundary_list=["mur_cuisine_sud_1", "mur_salon_sud_1", "mur_salon_cuisine"],
                            segment_list_id=["s_mur_cuisine_sud_et_mur_salon_sud","s_mur_salon_sud_et_mur_cuisine_sud", "s_mur_salon_cuisine_et_mur_salon_sud"],
                            id = "j_mur_cuisine_sud_et_mur_salon_sud")

    ##between wall and roof : horizontal linear junction
    
    house_1.link_boundaries(boundary_list=["plafond_salon", "mur_salon_ouest_1"],
                            segment_list_id=["s_plafond_mur_salon_ouest", "s_mur_salon_ouest_plafond"],
                            id="j_plafond_mur_salon_ouest")
    house_1.link_boundaries(boundary_list=["plafond_salon", "mur_salon_nord_1"],
                            segment_list_id=["s_plafond_mur_salon_nord", "s_mur_salon_nord_plafond"],
                            id="j_plafond_mur_salon_nord")
    house_1.link_boundaries(boundary_list=["plafond_salon", "mur_salon_est_1"],
                            segment_list_id=["s_plafond_mur_salon_est", "s_mur_salon_est_plafond"],
                            id="j_plafond_mur_salon_est")
    house_1.link_boundaries(boundary_list=["plafond_salon", "mur_salon_cuisine"],
                            segment_list_id=["s_plafond_salon_mur_cuisine", "s_mur_salon_cuisine_plafond"],
                            id="j_plafond_salon_mur_cuisine")


    house_1.link_boundaries(boundary_list=["plancher_salon", "mur_salon_ouest_1"],
                            segment_list_id=["s_plancher_mur_salon_ouest", "s_mur_salon_ouest_plancher"],
                            id="j_plancher_mur_salon_ouest")
    house_1.link_boundaries(boundary_list=["plancher_salon", "mur_salon_nord_1"],
                            segment_list_id=["s_plancher_mur_salon_nord", "s_mur_salon_nord_plancher"],
                            id="j_plancher_mur_salon_nord")
    house_1.link_boundaries(boundary_list=["plancher_salon", "mur_salon_est_1"],
                            segment_list_id=["s_plancher_mur_salon_est", "s_mur_salon_est_plancher"],
                            id="j_plancher_mur_salon_est")
    house_1.link_boundaries(boundary_list=["plancher_salon", "mur_salon_sud_1"],
                            segment_list_id=["s_plancher_mur_salon_sud", "s_mur_salon_sud_plancher"],
                            id="j_plancher_mur_salon_sud")

    house_1.link_boundaries(boundary_list=["plafond_salon", "plafond_cuisine", "mur_salon_cuisine"],
                            segment_list_id=["s_plafond_salon_mur_cuisine", "s_plafond_cuisine_mur_salon_cuisine", "s_mur_salon_cuisine_plafond"],
                            id="j_mur_salon_cuisine_plafond")

    house_1.link_boundaries(boundary_list=["plafond_cuisine", "mur_cuisine_nord_1"],
                            segment_list_id=["s_plafond_mur_cuisine_nord", "s_mur_cuisine_nord_plafond"],
                            id="j_plafond_mur_cuisine_nord")
    house_1.link_boundaries(boundary_list=["plafond_cuisine", "mur_cuisine_est_1"],
                            segment_list_id=["s_plafond_mur_cuisine_est", "s_mur_cuisine_est_plafond"],
                            id="j_plafond_mur_cuisine_est")
    house_1.link_boundaries(boundary_list=["plafond_cuisine", "mur_cuisine_sud_1"],
                            segment_list_id=["s_plafond_mur_cuisine_sud", "s_mur_cuisine_sud_plafond"],
                            id="j_plafond_mur_cuisine_sud")

    house_1.link_boundaries(boundary_list=["plancher_salon", "plancher_cuisine", "mur_salon_cuisine"],
                            segment_list_id=["s_plancher_mur_salon_cuisine", "s_plancher_cuisine_mur_salon_cuisine",
                                          "s_mur_salon_cuisine_plancher"],
                            id="j_mur_salon_cuisine_plancher")

    house_1.link_boundaries(boundary_list=["plancher_cuisine", "mur_cuisine_nord_1"],
                            segment_list_id=["s_plancher_mur_cuisine_nord", "s_mur_cuisine_nord_plancher"],
                            id="j_plancher_mur_cuisine_nord")
    house_1.link_boundaries(boundary_list=["plancher_cuisine", "mur_cuisine_est_1"],
                            segment_list_id=["s_plancher_mur_cuisine_est", "s_mur_cuisine_est_plancher"],
                            id="j_plancher_mur_cuisine_est")
    house_1.link_boundaries(boundary_list=["plancher_cuisine", "mur_cuisine_sud_1"],
                            segment_list_id=["s_plancher_mur_cuisine_sud", "s_mur_cuisine_sud_plancher"],
                            id="j_plancher_mur_cuisine_sud")

    #endregion

with open('house_1.json', 'w', encoding='utf8') as f:
    json.dump(house_1.generate_json(), f, ensure_ascii=False, indent=4)


