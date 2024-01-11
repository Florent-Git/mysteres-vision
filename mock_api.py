from flask import Flask
from flask import jsonify

from tuiles import TILE_LABELS

import random

app = Flask("MysteresAPI")
        
@app.route('/get_tiles', methods=['POST'])
def get_tiles():
    '''
    Retrieves an image from the post request and returns the type of tiles
    '''
    # Get 9 random distinct tiles from TILE_LABELS
    tiles = random.sample(TILE_LABELS, 9)
    return jsonify(list(map(lambda x: x.tile_id, tiles)))
    

if __name__ == "__main__":
    app.run(debug=True, host='YOUR_IP_ADDRESS')

