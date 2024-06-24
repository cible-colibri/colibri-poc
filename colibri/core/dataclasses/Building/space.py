class Space():

    def __init__(self, label="", volume=0, reference_area=0, altitude=0, use="living_room", air_permeability = 1.3):
        self.label = label
        self.volume = volume
        self.reference_area = reference_area
        self.altitude = altitude
        self.use = use
        self.air_permeability = air_permeability

        # simulation variables (computed at each timestep)
        self.Tint = 20


