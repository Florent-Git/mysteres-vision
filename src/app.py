from flask import Flask, jsonify, request
from functions.custom_functions import get_tiles, tiles_to_dataframe
from model.tile_types import TileType
from model.tile_decision_tree import get_decision_tree

import numpy as np
import cv2 as cv

app = Flask(__name__)
decision_tree = get_decision_tree()

@app.route('/')
def home():
    '''
    Returns a form to upload an image and a submit button to send the image to the server at /get_tiles
    and display the response
    '''
    return '''
    <form method="POST" action="/get_image_tiles" enctype="multipart/form-data">
        <input type="file" name="image">
        <input type="submit">
    </form>
    '''

@app.route('/get_image_tiles', methods=['POST'])
def get_image_tiles():
    img = np.fromfile(request.files["image"].stream)
    img = cv.imdecode(img, cv.IMREAD_COLOR)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    try:
        tiles = get_tiles(img)
        tiles_df = tiles_to_dataframe(tiles)
        tiles_X = tiles_df[['hue', 'saturation', 'value']]
        
        tiles_Y = decision_tree.predict(tiles_X)
        print(tiles_Y)
        for (tile, prediction) in zip(tiles, tiles_Y):
            print("tile: ", tile, "prediction: ", prediction)
            tile.set_tile_type(TileType(prediction))
            
        return jsonify([tile.to_dict() for tile in tiles]), 200
    except Exception as e:
        print(e)
        return "image does not contain tiles", 400


if __name__ == '__main__':
    app.run()
