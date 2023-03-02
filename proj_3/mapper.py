import pyrealsense2 as rs
import numpy as np
import cv2 as cv

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

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
pipeline.start(config)
while True:

    frame = pipeline.wait_for_frames()
    color_init = frame.get_color_frame()
    if not color_init:
        continue
    frame1 = np.asanyarray(color_init.get_data())
    frame2 = cv.resize(frame1, dsize=(480, 360), interpolation=cv.INTER_AREA)

    tracker = cv.TrackerKCF_create()
    bbox = cv.selectROI(frame2, False)
    ok = tracker.init(frame2, bbox)
    break


try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv.applyColorMap(cv.convertScaleAbs(depth_image, alpha=0.03), cv.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape
        # If depth and color resolutions are different, resize color image to match depth image for display
        '''if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv.resize(color_image, dsize=(depth_colormap_dim[1] / 50, depth_colormap_dim[0] / 50), interpolation=cv.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))'''
        resized_color = cv.resize(color_image, dsize=(480, 360), interpolation=cv.INTER_AREA)
        resized_depth = cv.resize(depth_colormap, dsize=(480, 360), interpolation=cv.INTER_AREA)

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
            cv.putText(resized_color, "Tracking failure detected", (100, 80), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        # Display tracker type on frame
        cv.putText(resized_color, 'KCF' + " Tracker", (100, 20), cv.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);

        # Display FPS on frame
        cv.putText(resized_color, "FPS : " + str(int(fps)), (100, 50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);



        images = np.hstack((resized_color, resized_depth))
        map = np.copy(images)
        map.fill(0)
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