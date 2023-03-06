import random

import pyrealsense2 as rs
import numpy as np
import cv2 as cv


font = cv.FONT_HERSHEY_SIMPLEX

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

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
print("Depth Scale is: " , depth_scale)

# We will be removing the background of objects more than
#  clipping_distance_in_meters meters away
clipping_distance_in_meters = 1 #2 meter
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
    if not color_init:
        continue

    frame1 = np.asanyarray(color_init.get_data())
    frame2 = cv.resize(frame1, dsize=(480, 360), interpolation=cv.INTER_AREA)

    # opencv tracker
    tracker = cv.TrackerKCF_create()
    # select custom bbox that opencv will track
    bbox = cv.selectROI(frame2, False)
    ok = tracker.init(frame2, bbox)
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

        # Remove background - Set pixels further than clipping_distance to grey
        '''grey_color = 153
        depth_image_3d = np.dstack(
            (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)'''

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv.applyColorMap(cv.convertScaleAbs(depth_image, alpha=0.03), cv.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # make images smaller so whole mapper fits on screen
        resized_color = cv.resize(color_image, dsize=(480, 360), interpolation=cv.INTER_AREA)
        resized_depth = cv.resize(depth_colormap, dsize=(480, 360), interpolation=cv.INTER_AREA)

        # for fps
        timer = cv.getTickCount()

        # Update tracker
        ok, bbox = tracker.update(resized_color)

        # Calculate Frames per second (FPS)
        fps = cv.getTickFrequency() / (cv.getTickCount() - timer);

        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv.rectangle(resized_color, p1, p2, (255, 0, 0), 2, 1)
        else:
            # Tracking failure
            cv.putText(resized_color, "Tracking failure detected", (100, 80), font, 0.75,
                       (0, 0, 255), 2)
        # Display tracker type on frame
        cv.putText(resized_color, "KCF Tracker", (100, 20), font, 0.75, (50, 170, 50), 2);
        cv.putText(resized_color, "FPS : " + str(int(fps)), (100, 50), font, 0.75, (50, 170, 50), 2);

        # build big frame with map on bottom
        images = np.hstack((resized_color, resized_depth))
        map = np.copy(images)
        map.fill(0)

        # calculate depth
        avg = 0
        width = resized_depth.shape
        points = []
        try:
            for i in range(300):
                points.append((random.randint(bbox[0], bbox[0] + bbox[2] - 1), random.randint(bbox[1], bbox[1] + bbox[3] - 1)))
            for point in points:
                avg += resized_depth[point[1]][point[0]][0]
            avg /= float(len(points))
            print(avg)
        except ValueError:
            pass

        # standardize depth

        # shade in object being tracked
        map_shape = np.shape(map)

        for i in range(40):
            map[50][int(map_shape[1] / 2) + (1 + i)] = [255, 0 ,0]
            map[50][int(map_shape[1] / 2) + (2 + i)] = [255, 0 ,0]

        cv.circle(map, (int(map_shape[1] / 2),(int(avg) - 100) * 2), 5, (0,0,255), 3)


        images = np.vstack((images, map))

        # Show images
        cv.namedWindow('RealSense', cv.WINDOW_AUTOSIZE)
        cv.imshow('RealSense', images)
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break


finally:

    # Stop streaming
    pipeline.stop()

cv.destroyAllWindows()
