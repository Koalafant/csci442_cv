import cv2 as cv
import numpy as np

src = cv.imread("japaneseflowers.jpg", 1)

if src is None:
    print("missing image")
else:
    gray = cv.cvtColor(src, cv.COLOR_RGB2GRAY)
    final = cv.Canny(gray, 10,30)   
    cv.imshow("Original", src)
    #cv.createTrackbar("Canny threshold default", "Original", 1, 100, 0);
    cv.imshow("adaptive", final)            
                
                
