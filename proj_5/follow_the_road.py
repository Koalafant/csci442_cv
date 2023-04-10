import random
# -- import maestro
import math
import pyrealsense2 as rs
import numpy as np
import cv2 as cv
import time
import sys

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# -- controller = maestro.Controller()
# -- controller.setTarget(1, 6000)
# -- time.sleep(0.1)
# -- controller.setTarget(1, 6000)

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

# camera setup
found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: ", depth_scale)

align_to = rs.stream.color
align = rs.align(align_to)

current_cog = [0,0]

try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()

        aligned_frames = align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        resized_color = cv.resize(color_image, dsize=(480, 360), interpolation=cv.INTER_AREA)
        resized_depth = cv.resize(depth_image, dsize=(480, 360), interpolation=cv.INTER_AREA)

        img = cv.cvtColor(resized_color, cv.COLOR_BGR2GRAY)
        img = cv.blur(img, (9,9))
        img = cv.threshold(img, 100, 255, cv.THRESH_BINARY)

        img = cv.equalizeHist(img[1])
        img = cv.blur(img, (9,9))
        img_x = cv.Sobel(img, 2, 1, 0);
        img_y = cv.Sobel(img, 2, 0, 1);
        abs_grad_x = cv.convertScaleAbs(img_x);
        abs_grad_y = cv.convertScaleAbs(img_y);
        img = cv.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0);
        img = cv.threshold(img, 40, 255, cv.THRESH_BINARY)
        img = cv.blur(img[1], (9, 9))
        img = cv.threshold(img, 100, 255, cv.THRESH_BINARY)
        img = img[1]

        height, width, = img.shape
        x_vals, y_vals = np.where(img == 255)
        try:
            cog = [int(float(sum(y_vals)) / len(y_vals)), int(float(sum(x_vals)) / len(x_vals))]
        except ZeroDivisionError:
            cog = current_cog

        if cog[0] - current_cog[0] > 40:
            cog[0] = current_cog[0] + 40
        elif cog[0] - current_cog[0] < -40:
            cog[0] = current_cog[0] - 40
        if cog[1] - current_cog[1] > 40:
            cog[1] = current_cog[1] + 40
        elif cog[1] - current_cog[1] < -40:
            cog[1] = current_cog[1] - 40
        current_cog = cog
        cv.circle(img, cog, 20, (255, 0, 0), 20)

        # cog is too far left
        if cog[0] > width * 0.66:
            print('turning right!')

            time.sleep(0.01)

        # cog is too far right
        elif cog[0] < width * 0.33:
            print('turning left!')
            time.sleep(0.01)

        # cog is too far up (move forward)
        elif cog[1] < height * 0.5:
            print('VROOOOM')
            time.sleep(0.01)

        # lost cog (stop)
        elif cog[1] > height * 0.5:
            print('Help me! STOP!')
            time.sleep(0.01)

        else:
            print('STOP!')
            time.sleep(0.01)


        cv.namedWindow('RealSense', cv.WINDOW_AUTOSIZE)
        cv.imshow('RealSense', img)

        k = cv.waitKey(5) & 0xFF
        if k == 27:
            print("Stopping")
            # -- controller.setTarget(1,6000)
            break


finally:

    # Stop streaming
    pipeline.stop()
    # -- controller.setTarget(1, 6000)

cv.destroyAllWindows()
