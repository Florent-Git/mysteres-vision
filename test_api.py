from flask import Flask
from flask import request, jsonify
from custom_functions import get_tiles as _get_tiles, tiles_to_dataframe

import numpy as np
import cv2 as cv
import pickle

app = Flask("MysteresAPI")

def get_model():
    '''
    Loads the model from the model directory
    '''
    with open('model/mysteres01.pkl', 'rb') as f:
        model = pickle.load(f)
    return model

model = get_model()

def import_image(stream):
    '''
    Imports an image from a stream
    '''
    nparr = np.fromstring(stream, np.uint8)
    img = cv.imdecode(nparr, cv.IMREAD_COLOR)
    return img

@app.route('/')
def home():
    '''
    Returns a form to upload an image and a submit button to send the image to the server at /get_tiles
    and display the response
    '''
    return '''
    <form method="POST" action="/get_tiles" enctype="multipart/form-data">
        <input type="file" name="image">
        <input type="submit">
    </form>
    '''

        
@app.route('/get_tiles', methods=['POST'])
def get_tiles():
    '''
    Retrieves an image from the post request and returns the type of tiles
    '''
    nparr = np.fromfile(request.files["image"].stream)
    image_cv = cv.imdecode(nparr, cv.IMREAD_COLOR)
    image_cv = cv.cvtColor(image_cv, cv.COLOR_BGR2RGB)
    
    tiles = _get_tiles(image_cv)
    tiles_df = tiles_to_dataframe(tiles)
    tiles_X = tiles_df[["hue", "saturation", "value"]]
    
    tiles_Y = model.predict(tiles_X)
    for (tile, prediction) in zip(tiles, tiles_Y):
        tile.with_tile_id(prediction)
    return jsonify(list(map(lambda x: x.tile_id, tiles)))
    

if __name__ == "__main__":
    app.run(debug=True)

