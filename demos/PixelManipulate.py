import cv2 as cv

src = cv.imread("japaneseflowers.jpg", 1)
if src is None:
    print("missing image")
else:
    cv.imshow("windowM", src)
    width = src.shape
    
    print(width)
    for row in range(width[0]):
        for col in range(width[1]):
                src[row][col][0]=0
    cv.imshow("windowMy", src)
    cv.waitKey(0)
                
                
                
