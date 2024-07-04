class Boundary():

    def __init__(self, type, type_id, label, side_1, side_2, azimuth, tilt, area, origin, segments):
        self.type = type
        self.type_id = type_id
        self.label = label
        self.side_1 = side_1
        self.side_2 = side_2
        self.azimuth = azimuth
        self.tilt = tilt
        self.area = area
        self.origin = origin
        self.segments = segments

        # topology
        self.space = None

