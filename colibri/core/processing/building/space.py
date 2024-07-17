class Space():

    def __init__(self, label="", volume=0, reference_area=0, altitude=0, use="living_room", air_permeability = 1.3):
        self.label = label
        self.volume = volume
        self.reference_area = reference_area
        self.altitude = altitude
        self.use = use
        self.air_permeability = air_permeability
        self.height = 3 # TODO : hook up to data model


        # computed values
        self.envelope_area = 0.0
        self.envelope_list = {}
        self.previousTcons = 19.0
        self.qOccGains = 0  # TODO : hook up to data model
        self.tempAnnualNeeds = 0.0

        # simulation variables (computed at each timestep)
        self.Tint = 20.0
        self.set_point_heating = 0.0
        self.set_point_cooling = 0.0
        self.Qneeds = 0.0

        # topology
        self.emitters = []
        self.boundaries = []

