class Block:
    def __init__(self, x, y, z, id):
        self.x = x
        self.y = y
        self.z = z
        self.id = id

    def info(self):
        print(f"Block: ({self.x}, {self.y}, {self.z}) - ID: {self.id}")