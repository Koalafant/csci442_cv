import cv2 as cv

src = cv.imread("japaneseflowers.jpg", 1)
#src = cv.imread("me.jpg", 1)
if src is None:
    print("missing image")
else:
    cv.imshow("windowM", src)
    gray = cv.cvtColor(src, cv.COLOR_RGB2GRAY)
    ret,thresh = cv.threshold(gray, 75, 255, 0)
    
    cv.imshow("windowMy", thresh)
    cv.waitKey(0)
                
                
                
