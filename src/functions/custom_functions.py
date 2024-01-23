from model.tile import Tile

import colorsys
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
    circles = cv.HoughCircles(image, cv.HOUGH_GRADIENT, dp=1, minDist=100, param1=50, param2=10, minRadius=50, maxRadius=58)
    return np.uint16(np.around(circles))[0,:]

def get_circles_color(image, circles, np_fun):
    '''
    Retrieves the average color of the circles in an image in HSV format.
    '''
    circles_array = []
    r,g,b = cv.split(image)
    for i in circles:
        mask = np.full((image.shape[0], image.shape[1]),0,dtype=np.uint8)
        cv.circle(mask, (i[0], i[1]), i[2], (255, 255, 255), -1)

        r_circle_masked = cv.bitwise_and(r, r, mask = mask)
        g_circle_masked = cv.bitwise_and(g, g, mask = mask)
        b_circle_masked = cv.bitwise_and(b, b, mask = mask)

        r_pos_circle = r_circle_masked[r_circle_masked!=0]
        g_pos_circle = g_circle_masked[g_circle_masked!=0]
        b_pos_circle = b_circle_masked[b_circle_masked!=0]

        r_circle_average = np_fun(r_pos_circle)
        g_circle_average = np_fun(g_pos_circle)
        b_circle_average = np_fun(b_pos_circle)

        circles_array.append(Tile(i, tuple([r_circle_average / 255, g_circle_average / 255, b_circle_average / 255])))
    return circles_array

def get_average_circles(image, circles):
    return get_circles_color(image, circles, np.mean)

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
    
    
def get_tiles(image: np.ndarray) -> list[Tile]:
    '''
    Retrieves the tiles from an image.
    '''
    # half_image = cv.resize(image, (image.shape[1]*1.5, image.shape[0]*1.5))
    preprocessed_image = preprocess_image(image)
    circles = get_circles(preprocessed_image)
    average_circles = get_average_circles(image, circles)
    return sort_circles(average_circles)

def tiles_to_dataframe(tiles):
    '''
    Converts a list of tiles to a dataframe
    '''
    data = [[tile.color[0], tile.color[1], tile.color[2], tile.dimensions[0], tile.dimensions[1], tile.dimensions[2], tile.tile_type, tile.img_id] for tile in tiles]
    return pd.DataFrame(data, columns=["red", "green", "blue", "position_x", "position_y", "radius", "tile_type", "img_id"])

