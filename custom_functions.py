from os import listdir
import numpy as np
import cv2 as cv

def reconstruct_image(base_image, mask, iterations=1, kernel=np.ones((3, 3))):
    i = 0
    reconstructed_image = base_image
    while i != iterations:
        lastReconstructedImage = cv.dilate(reconstructed_image, kernel)
        lastReconstructedImage = cv.bitwise_and(lastReconstructedImage, cv.bitwise_not(mask))
        reconstructed_image = lastReconstructedImage
        i += 1
    
    return reconstructed_image


def get_circles(image):
    grayed_image = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    blurred_image = cv.medianBlur(grayed_image, 5)
    _, threshold_image = cv.threshold(blurred_image, 70, 255, cv.THRESH_BINARY)
    closed_image = cv.morphologyEx(threshold_image, cv.MORPH_CLOSE, np.ones((31, 31)))
    image_circles = cv.HoughCircles(closed_image, cv.HOUGH_GRADIENT, dp=1, minDist=100, param1=50, param2=10, minRadius=73, maxRadius=78)
    return np.uint16(np.around(image_circles))[0,:]


def get_average_circles(image, circles):
    circles_dict = {}
    h,s,v = cv.split(cv.cvtColor(image, cv.COLOR_RGB2HSV))
    for i in circles:
        mask = np.full((image.shape[0], image.shape[1]),0,dtype=np.uint8)
        cv.circle(mask, (i[0], i[1]), i[2], (255, 255, 255), -1)
        circle_masked = cv.bitwise_and(h, h, mask = mask)
        posCircle = circle_masked[circle_masked!=0]
        circle_average = np.average(posCircle)
        circles_dict[circle_average] = i
    return circles_dict


if __name__ == "__main__":
    images = listdir("./images")

    for imagePath in images:
        image = cv.imread(f"./images/{imagePath}")
        circles = get_circles(image)
        img_black = np.zeros(image.shape)

        for i in circles[0,:]:
            # draw the outer circle
            cv.circle(img_black, (i[0], i[1]), i[2], (255, 255, 255), cv.FILLED, 2)
        
        cv.imwrite(f"./out/{imagePath}", img_black)
