from model.tile_types import TileType

# Create an immutable class whose name is Tile and whose constructor 
# takes three arguments: dimensions, color, and index.
# The dimensions argument should be a tuple of three integers representing the 
# x position, the y position and the radius of the tile.
class Tile:
    def __init__(self, dimensions, color):
        self.position_x = dimensions[0]
        self.position_y = dimensions[1]
        self.radius = dimensions[2]
        
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]
        
        self.flipped = False
        
        self.index = None
        self.tile_type = None
        self.img_id = None
        
    
    def to_dict(self):
        return {
            "position_x": int(self.position_x),
            "position_y": int(self.position_y),
            "radius": int(self.radius),
            "red": int(self.red),
            "blue": int(self.blue),
            "green": int(self.green),
            "index": int(self.index),
            "tile_type": str(self.tile_type.name)
        }
    
    
    @property
    def dimensions(self):
        return (self.position_x, self.position_y, self.radius)
    
    @property
    def color(self):
        return (self.red, self.green, self.blue)
    
    def set_index(self, index):
        self.index = index
        return self
    
    def set_tile_type(self, tile_type):
        self.tile_type = tile_type
        return self
    
    def set_img_id(self, img_id):
        self.img_id = img_id
        return self
    
    def set_flipped(self, flipped):
        self.flipped = flipped
        return self
    
    def get_tile_type(self):
        return self.tile_type
    
    def __str__(self) -> str:
        return f"Tile: {{{self.dimensions}, {self.color}, {self.index}, {self.tile_type}, {self.img_id}}}"
    
    @staticmethod
    def from_dict(tile_dict):
        return Tile((tile_dict["position_x"], tile_dict["position_y"], tile_dict["radius"]), (tile_dict["red"], tile_dict["green"], tile_dict["blue"])).set_index(tile_dict["index"]).set_tile_type(TileType[tile_dict["tile_type"]]).set_img_id(tile_dict["img_id"]).set_flipped(tile_dict["flipped"])
    
