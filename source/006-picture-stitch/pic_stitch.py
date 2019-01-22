#

#py -3 -m pip install opencv-python==3.4.2.16
#py -3 -m pip install opencv-contrib-python==3.4.2.16
import numpy as np
import cv2
from matplotlib import pyplot as plt

if __name__ == '__main__':
    images = []

    images.append(cv2.imread('test1.jpg', cv2.IMREAD_COLOR))
    images.append(cv2.imread('test2.jpg', cv2.IMREAD_COLOR))
    images.append(cv2.imread('test3.jpg', cv2.IMREAD_COLOR))
    
    stitcher = cv2.createStitcher(True)
    stitched = stitcher.stitch(images)
    cv2.imwrite('res.jpg', stitched[1])
    plt.imshow(cv2.cvtColor(stitched[1],cv2.COLOR_BGR2RGB)),plt.show()
    