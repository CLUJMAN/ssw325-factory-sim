class MoveCommand:
    """One explicit instruction for the robotic arm, e.g. 'Move IdleRack -> C5'."""

    def __init__(self, device, source, destination, issued_at):
        self.device = device
        self.source = source              # any location with .name and .position
        self.destination = destination
        self.issued_at = issued_at
        self.started_at = None            # when the arm actually began this move
        self.completed_at = None

    def describe(self):
        return f"Move {self.source.name} -> {self.destination.name} (Device {self.device.device_id})"
