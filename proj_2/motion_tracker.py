import cv2 as cv
import random
import numpy as np

global width
global hsv

cap = cv.VideoCapture(0)
# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# 1. cap an image
ret, frame = cap.read()
dim = frame.shape
# 2. create blank images
gray = 100 * np.zeros((dim[0], dim[1]), dtype=np.uint8)
color = 100 * np.zeros((dim[0], dim[1], 3), dtype=np.uint8)
image1 = frame.astype(float)
abs_diff = frame.copy()

# 3. while loop
while True:
    # 4. grab new image and brighten
    ret, frame = cap.read()
    orig = frame.copy()
    dim = frame.shape

    # 4. brighten image
    cv.normalize(frame, frame, alpha=50, beta=1.5 * 255, norm_type=cv.NORM_MINMAX)

    # 5. Blur
    frame = cv.blur(frame, (5, 5))

    # 6. accumulateWeighted
    cv.accumulateWeighted(frame, image1, alpha=0.1)

    # 7. convertScaleAbs
    color = cv.convertScaleAbs(image1)

    # 8. absDiff
    color = cv.absdiff(frame, np.array(image1, dtype='uint8'))

    # 9. convert to Gray
    gray = cv.cvtColor(color, cv.COLOR_BGR2GRAY)
    cv.imshow('Gray', gray)

    # 10. Threshold grayscale (LOW)
    ret, gray = cv.threshold(gray, 50, 255, cv.THRESH_BINARY)

    # 11. Blur again
    gray = cv.blur(gray, (5, 5))

    # 12. Threshold again (HIGH)
    ret, gray = cv.threshold(gray, 210, 255, cv.THRESH_BINARY)
    cv.imshow('Threshold', gray)

    # 13, 14, 15, Contours and stuff...
    contours, hierarchy = cv.findContours(gray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    good_rect = []
    contours_poly = [None] * len(contours)
    boundRect = [None] * len(contours)

    # display contours
    contours_im = np.zeros((dim[0], dim[1]), dtype=np.uint8)
    contours_im.fill(255)
    cv.drawContours(contours_im, contours=contours, contourIdx=-1, color=(0, 0, 0), thickness=2)
    cv.imshow("Contours", contours_im)

    for i, c in enumerate(contours):
        contours_poly[i] = cv.approxPolyDP(c, 3, True)
        boundRect[i] = cv.boundingRect(contours_poly[i])
        if boundRect[i][2] > 50 or boundRect[i][3] > 50:
            good_rect.append(boundRect[i])

    new_bounds = good_rect

    # 16. Draw bounding boxes on original image
    for i in range(len(new_bounds)):
        color = (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
        cv.rectangle(orig, (int(new_bounds[i][0]), int(new_bounds[i][1])),
                     (int(new_bounds[i][0] + new_bounds[i][2]), int(new_bounds[i][1] + new_bounds[i][3])), color, 2)

    cv.imshow('Original', orig)

    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break


cv.destroyAllWindows()
