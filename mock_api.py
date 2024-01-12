from flask import Flask
from flask import jsonify

from tuiles import TILE_LABELS
from src.model.tile import Tile

import random

# Use SocketIO to create a state where the client continuously sends an image as an event
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('check_image')
def check_image(data):
    # Return an array of Tile objects
    tiles = []
    for i in range(0, 16):
        tiles.append(Tile((random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)), TILE_LABELS[random.randint(0, 3)]).set_index(i).set_tile_type(i).set_img_id(i))
    emit('image_checked', {'tiles': [tile.__dict__ for tile in tiles]})
    
    
if __name__ == '__main__':
    socketio.run(app, debug=True)
