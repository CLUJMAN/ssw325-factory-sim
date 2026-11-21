class DoneRack:
    """Unlimited buffer for devices that have finished testing."""

    def __init__(self, rack_id="DoneRack", position=(0, 0)):
        self.rack_id = rack_id
        self.name = rack_id
        self.position = position
        self.finished = []

    def put(self, d):
        self.finished.append(d)

    def get_finished(self):
        return self.finished
