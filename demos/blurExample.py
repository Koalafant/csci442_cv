import cv2 as cv

src = cv.imread("japaneseflowers.jpg", 1)
if src is None:
    print("missing image")
else:
    cv.imshow("windowM", src)
    #gray = cv.cvtColor(src, cv.COLOR_RGB2GRAY)
    dst = cv.blur(src, (5,5))
    can = cv.Canny(dst, 10,40)
    cv.imshow("windowMy", can)
                
                
                
