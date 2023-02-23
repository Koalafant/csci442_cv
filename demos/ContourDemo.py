import cv2 as cv


src = cv.imread("japaneseflowers.jpg", 1)
if src is None:
    print("missing image")
else:
    gray= cv.cvtColor(src,cv.COLOR_BGR2GRAY) 
    ret, thresh = cv.threshold(gray,127,255,0) 
	#calculate the contours from binary image
    contours, hierarchy = cv.findContours(thresh,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE) 
    with_contours = cv.drawContours(src,contours,-1,(255,0,0),3) 
    
    cv.imshow("Contours", src)
    cv.imshow("gray", gray )
    cv.waitKey(0)
                
                
