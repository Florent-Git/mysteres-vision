# Create an immutable class whose name is Tile and whose constructor 
# takes three arguments: dimensions, color, and index.
# The dimensions argument should be a tuple of three integers representing the 
# x position, the y position and the radius of the tile.
class Tile:
    def __init__(self, dimensions, color):
        self.dimensions = dimensions
        self.color = color
        self.index = None
        self.tile_id = None
        self.img_id = None
    
    def with_index(self, index):
        self.index = index
        return self
    
    def with_tile_id(self, tile_id):
        self.tile_id = tile_id
        return self
    
    def with_img_id(self, img_id):
        self.img_id = img_id
        return self
    
    def get_tile_id(self):
        return self.tile_id
    
    def __str__(self) -> str:
        return f"Tile: {{{self.dimensions}, {self.color}, {self.index}, {self.tile_id}, {self.img_id}}}"
