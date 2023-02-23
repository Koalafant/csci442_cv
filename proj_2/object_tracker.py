import cv2 as cv
import numpy as np

global width
global hsv

min_hsv = [0, 0, 0]
max_hsv = [255, 255, 255]


def mouse_click(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        print(hsv[x][y][0], hsv[x][y][1], hsv[x][y][2])


def min_h(val):
    min_hsv[0] = val


def max_h(val):
    max_hsv[0] = val


def min_s(val):
    min_hsv[1] = val


def max_s(val):
    max_hsv[1] = val


def min_v(val):
    min_hsv[2] = val


def max_v(val):
    max_hsv[2] = val


trackbars = False

cap = cv.VideoCapture(0)
# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

while True:
    global width
    # 1. capture video
    ret, frame = cap.read()
    width = frame.shape
    original = frame # cv.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv.INTER_AREA)
    shape = frame.shape

    # 2. Display live video
    cv.imshow('Original', original)

    # 3. BGR to HSV
    hsv = cv.cvtColor(original, cv.COLOR_BGR2HSV)

    # 4. Display HSV video
    cv.imshow('HSV', hsv)
    cv.namedWindow("HSV")

    # 5. MouseCallback on HSV
    cv.setMouseCallback('HSV', mouse_click)

    # 6. create 6 scalers and 2 trackbars
    if not trackbars:
        cv.createTrackbar("Min H", "HSV", 0, 255, min_h)
        cv.createTrackbar("Max H", "HSV", 0, 255, max_h)
        cv.createTrackbar("Min_S", "HSV", 0, 255, min_s)
        cv.createTrackbar("Max_S", "HSV", 0, 255, max_s)
        cv.createTrackbar("Min_V", "HSV", 0, 255, min_v)
        cv.createTrackbar("Max_v", "HSV", 0, 255, max_v)
        trackbars = True

    # 7. inRange to binary
    threshhold = cv.inRange(hsv, tuple(min_hsv), tuple(max_hsv))
    # cv.imshow('Threshhold', threshhold)

    # 8. Dilate and erode grayscale
    kernel = np.ones((5, 5), np.uint8)
    noise_removal = cv.erode(threshhold, kernel, iterations=1)
    noise_removal = cv.dilate(noise_removal, kernel, iterations=1)
    # 9. Display binary
    cv.imshow('Binary', noise_removal)


    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break
cv.destroyAllWindows()
