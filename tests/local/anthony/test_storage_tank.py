
def storage_tank():
    from core.project                                         import Project
    from models.utility.simple_weather                        import SimpleWeather
    from models.solar_thermal_collectors.flat_plate_collector import FlatPlateCollector

    project                              = Project()
    weather                              = SimpleWeather("weather_1")
    weather.number_of_time_steps_per_day = 1
    weather.ending_day                   = 168
    flat_plate_collector = FlatPlateCollector("flat_plate_collector_1")
    #project.link(weather, "outlet_flow_rate", flat_plate_collector, "inlet_flow_rate_1")
    weather.number_of_surfaces           = 1
    weather.surface_azimuth_angle_1      = 0
    weather.surface_tilt_angle_1         = 45
    project.add(weather)
    project.add(flat_plate_collector)
    project.add_plot("Weather", weather, "total_incident_solar_radiation_1")
    project.add_plot("Flat-plate collector", flat_plate_collector, "outlet_temperature")
    project.run()
    print("toto")

if __name__ == "__main__":
    storage_tank()


