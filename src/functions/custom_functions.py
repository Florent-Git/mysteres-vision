from model.tile import Tile

import pandas as pd
import numpy as np
import cv2 as cv

def reconstruct_image(base_image: np.array, mask: np.array, iterations=1, kernel=np.ones((3, 3))):
    '''
    Reconstructs an image based on the dilation of the base image and the mask.
    '''
    i = 0
    reconstructed_image = base_image
    while i != iterations:
        lastReconstructedImage = cv.dilate(reconstructed_image, kernel)
        lastReconstructedImage = cv.bitwise_and(lastReconstructedImage, cv.bitwise_not(mask))
        reconstructed_image = lastReconstructedImage
        i += 1
    return reconstructed_image


def preprocess_image(image: np.array) -> np.array:
    grayed_image = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    blurred_image = cv.medianBlur(grayed_image, 5)
    _, threshold_image = cv.threshold(blurred_image, 70, 255, cv.THRESH_BINARY)
    closed_image = cv.morphologyEx(threshold_image, cv.MORPH_CLOSE, np.ones((27, 27)))
    return closed_image


def get_circles(image: np.array) -> np.array:
    '''
    Retrieves the circles in an image.
    '''
    circles = cv.HoughCircles(image, cv.HOUGH_GRADIENT, dp=1, minDist=100, param1=50, param2=10, minRadius=73, maxRadius=78)
    return np.uint16(np.around(circles))[0,:]

def get_average_circles(image, circles):
    '''
    Retrieves the average color of the circles in an image in HSV format.
    '''
    circles_array = []
    h,s,v = cv.split(cv.cvtColor(image, cv.COLOR_RGB2HSV))
    for i in circles:
        mask = np.full((image.shape[0], image.shape[1]),0,dtype=np.uint8)
        print(i)
        cv.circle(mask, (i[0], i[1]), i[2], (255, 255, 255), -1)

        h_circle_masked = cv.bitwise_and(h, h, mask = mask)
        s_circle_masked = cv.bitwise_and(s, s, mask = mask)
        v_circle_masked = cv.bitwise_and(v, v, mask = mask)

        h_pos_circle = h_circle_masked[h_circle_masked!=0]
        s_pos_circle = s_circle_masked[s_circle_masked!=0]
        v_pos_circle = v_circle_masked[v_circle_masked!=0]

        h_circle_average = np.average(h_pos_circle)
        s_circle_average = np.average(s_pos_circle)
        v_circle_average = np.average(v_pos_circle)

        circles_array.append(Tile(i, tuple([h_circle_average, s_circle_average, v_circle_average])))
    return circles_array

def sort_circles(tiles: [Tile]):
    returned_array = []
    # Map the dimensions of the tiles to a numpy array
    circles = np.array([circle.dimensions for circle in tiles])
    x_sorted = circles[np.argsort(circles[:, 0]), :]
    left_most = x_sorted[:3, :]
    middle = x_sorted[3:6, :]
    right_most = x_sorted[6:, :]
    (tl, ml, bl) = left_most[np.argsort(left_most[:, 1]), :]
    (tm, mm, bm) = middle[np.argsort(middle[:, 1]), :]
    (tr, mr, br) = right_most[np.argsort(right_most[:, 1]), :]
    sorted_circles = [tl, tm, tr, ml, mm, mr, bl, bm, br]
    # Map each dimensions to a tuple
    sorted_circles = [tuple(circle) for circle in sorted_circles]
    # For each circle, find the corresponding tile, apply the index and return the list of tiles
    for tile in tiles:
        for circle in sorted_circles:
            if np.array_equal(tile.dimensions, circle):
                returned_array.append(tile.set_index(sorted_circles.index(circle)))
    
    # Sort returned_array by index
    returned_array = sorted(returned_array, key=lambda tile: tile.index)            
    return returned_array
    
    
def get_tiles(image: np.array) -> [Tile]:
    '''
    Retrieves the tiles from an image.
    '''
    half_image = cv.resize(image, (image.shape[1]//2, image.shape[0]//2))
    preprocessed_image = preprocess_image(half_image)
    circles = get_circles(preprocessed_image)
    average_circles = get_average_circles(half_image, circles)
    return sort_circles(average_circles)

def tiles_to_dataframe(tiles):
    '''
    Converts a list of tiles to a dataframe
    '''
    data = [[tile.color[0], tile.color[1], tile.color[2], tile.dimensions[0], tile.dimensions[1], tile.dimensions[2], tile.tile_type, tile.img_id] for tile in tiles]
    return pd.DataFrame(data, columns=["hue", "saturation", "value", "position_x", "position_y", "radius", "tile_type", "img_id"])

