from flask import Flask, jsonify, request, render_template
from functions.custom_functions import get_tiles, tiles_to_dataframe
from model.tile_types import TileType
from model.tile import Tile
from model.tile_decision_tree import get_decision_tree

import base64 as b64
import numpy as np
import cv2 as cv

app = Flask(__name__)
decision_tree = get_decision_tree()

def get_image() -> np.ndarray:
    '''
    Returns the image taken from a POST requests in the "image" json field as a base64 encoded string
    '''    
    img_json = request.json["image"]
    buff = b64.b64decode(img_json)
    nparr = np.frombuffer(buff, dtype=np.uint8)
    img = cv.imdecode(nparr, cv.IMREAD_COLOR)
    return cv.cvtColor(img, cv.COLOR_BGR2RGB)
    

@app.route('/')
def home():
    '''
    Returns a form to upload an image and a submit button to send the image to the server at /get_image_tiles
    and display the response
    '''
    # Returns a simple form to upload an image in a JSON "image" field and a submit button to send the image
    # to the server at /get_image_tiles and display the response
    return render_template("form.html")
    

@app.route('/get_image_tiles', methods=['POST'])
def get_image_tiles():
    img = get_image()
    try:
        tiles = get_tiles(img)
        tiles_df = tiles_to_dataframe(tiles)
        tiles_X = tiles_df[['red', 'green', 'blue']]
        
        tiles_Y = decision_tree.predict(tiles_X)
        for (tile, prediction) in zip(tiles, tiles_Y):
            prediction_index = np.argmax(prediction)
            tile.set_tile_type(TileType(prediction_index))
            
        return jsonify([tile.to_dict() for tile in tiles]), 200
    except Exception as e:
        print("Error:", e)
        return "image does not contain tiles", 400
    
@app.route('/poll_changes', methods=['POST'])
def poll_changes():
    '''
    Returns a JSON object containing the changes to the tiles since the last poll
    '''
    img = get_image()
    original_tiles = [Tile.from_dict(tile) for tile in request.json["tiles"]]
    
    new_tiles = get_tiles(img)
    
    original_tiles = sorted(original_tiles, key=lambda tile: tile["index"])
    new_tiles = sorted(new_tiles, key=lambda tile: tile.index)
    
    # Compare the new tiles to the old tiles by their index
    # If a tile has the same index, check if the tile color has changed by a certain threshold
    # If the tile color has changed, return the tile
    if len(original_tiles) != len(new_tiles):
        return "number of original tiles does not match the number of new tiles", 400
    
    changed_tiles = []
    for (original_tile, new_tile) in zip(original_tiles, new_tiles):
        if original_tile["index"] == new_tile.index:
            original_color = (original_tile["red"], original_tile["green"], original_tile["blue"])
            new_color = new_tile.color
            if np.linalg.norm(np.array(original_color) - np.array(new_color)) > 10:
                changed_tiles.append(new_tile)
                
    return jsonify([tile.to_dict() for tile in changed_tiles]), 200

if __name__ == '__main__':
    app.run()
