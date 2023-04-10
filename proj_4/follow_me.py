import random
import maestro

import pyrealsense2 as rs
import numpy as np
import cv2 as cv
import time
import sys

font = cv.FONT_HERSHEY_SIMPLEX

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

ooga = maestro.Controller()
ooga.setTarget(1, 6000)
time.sleep(0.1)
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
    print("The demo requires Depth camera with Color sensor")
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

# We will be removing the background of objects more than
#  clipping_distance_in_meters meters away
clipping_distance_in_meters = 1  # 2 meter
clipping_distance = clipping_distance_in_meters / depth_scale

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
align_to = rs.stream.color
align = rs.align(align_to)

# Set up initial bounding box for tracking
while True:
    # grab one frame
    frame = pipeline.wait_for_frames()
    color_init = frame.get_color_frame()
    depth_init = frame.get_depth_frame()
    if not color_init and depth_init:
        continue

    frame1 = np.asanyarray(color_init.get_data())
    depth1 = np.asanyarray(depth_init.get_data())

    resized_color_init = cv.resize(frame1, dsize=(480, 360), interpolation=cv.INTER_AREA)
    resized_depth_init = cv.resize(depth1, dsize=(480, 360), interpolation=cv.INTER_AREA)

    # opencv tracker
    tracker = cv.TrackerKCF_create()
    # select custom bbox that opencv will track
    bbox = cv.selectROI(resized_color_init, False)
    ok = tracker.init(resized_color_init, bbox)



    #ok, bbox = tracker.update(resized_color_init)

    points_init = []
    avg = 0
    try:
        for i in range(300):
            points_init.append(
                (random.randint(bbox[0], bbox[0] + bbox[2] - 1), random.randint(bbox[1], bbox[1] + bbox[3] - 1)))
        for point in points_init:

            avg += resized_depth_init[point[1]][point[0]]
        avg /= float(len(points_init))
        poo = avg
        poo /= 1000
    except ValueError:
        pass
    break

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



        # for fps
        timer = cv.getTickCount()

        # Update tracker
        ok, bbox = tracker.update(resized_color)

        # Calculate Frames per second (FPS)

        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv.rectangle(resized_color, p1, p2, (255, 0, 0), 2, 1)
        else:
            pass
            ooga.setTarget(1, 6000)
        # build big frame with map on bottom

        # calculate depth
        avg = 0
        points = []
        try:
            for i in range(300):
                points.append(
                    (random.randint(bbox[0], bbox[0] + bbox[2] - 1), random.randint(bbox[1], bbox[1] + bbox[3] - 1)))
            for point in points:
                avg += resized_depth[point[1]][point[0]]
            avg /= float(len(points))
            avg *= depth_scale
            updatedAvg = avg * 28000
            if poo - 0.2 > avg:
                ooga.setTarget(1, 6600)
                print("moving backwards")
                time.sleep(0.1)
            elif poo + 0.4 < avg:
                ooga.setTarget(1, 5400)
                time.sleep(0.1)
                print('moving forwards')
            else:
                ooga.setTarget(1, 6000)
                time.sleep(0.1)
            if avg == 0:
                ooga.setTarge(1, 6000)
                time.sleep(0.1)
        except ValueError:
            pass
        print(f'Target: {poo} -> real: {avg}')
        print(poo)
        # Show images
        cv.namedWindow('RealSense', cv.WINDOW_AUTOSIZE)
        # cv.imshow('RealSense', images)
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            print("Stopping")
            ooga.setTarget(1,6000)
            break


finally:

    # Stop streaming
    pipeline.stop()
    ooga.setTarget(1, 6000)

cv.destroyAllWindows()
