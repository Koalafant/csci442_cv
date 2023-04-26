import random
import maestro
import math
import pyrealsense2 as rs
import numpy as np
import cv2 as cv
import time
import sys

"""State defined Tango controller. .run() will find a goal, 
navigate around obstacles and eventually return via successive state calls."""


class Robo:
    def __init__(self, set_depth_scale=1):
        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.controller = maestro.Controller()
        self.robo_move('stop')

        # Get device product line for setting a supporting resolution
        self.pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        self.pipeline_profile = self.config.resolve(self.pipeline_wrapper)
        self.device = self.pipeline_profile.get_device()
        self.device_product_line = str(self.device.get_info(rs.camera_info.product_line))

        # camera setup
        found_rgb = False
        for s in self.device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            exit(0)

        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        if self.device_product_line == 'L500':
            self.config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
        else:
            self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start streaming
        self.profile = self.pipeline.start(self.config)

        # Getting the depth sensor's depth scale (see rs-align example for explanation)
        depth_sensor = self.profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        print("Depth Scale is: ", depth_scale)

        align_to = rs.stream.color
        self.align = rs.align(align_to)

        # We will be removing the background of objects more than
        #  clipping_distance_in_meters meters away
        self.clipping_distance_in_meters = set_depth_scale  # 2 meter
        self.clipping_distance = self.clipping_distance_in_meters / depth_scale

    def robo_move(self, dir='stop', speed=6000):
        if dir == "stop":
            self.controller.setTarget(1, 6000)
            time.sleep(0.01)
            self.controller.setTarget(2, 6000)
            time.sleep(0.01)
        elif dir == "left":
            self.controller.setTarget(1, 6000)
            time.sleep(0.01)
            self.controller.setTarget(2, speed + 900)
            time.sleep(0.1)
        elif dir == "right":
            self.controller.setTarget(1, 6000)
            time.sleep(0.01)
            self.controller.setTarget(2, speed - 900)
            time.sleep(0.1)
        elif dir == "forward":
            self.controller.setTarget(2, 6000)
            time.sleep(0.01)
            self.controller.setTarget(1, speed - 700)
            time.sleep(0.1)
        else:
            raise SystemError("valid robo_move commands are: 'stop' 'left' 'right' or 'forward'.")

    def grab_frame(self):
        while True:
            # Wait for a coherent pair of frames: depth and color
            frames = self.pipeline.wait_for_frames()

            aligned_frames = self.align.process(frames)

            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            #depth_colormap_image = cv.applyColorMap(cv.convertScaleAbs(depth_image, alpha=0.03), cv.COLORMAP_JET)
            color_image = np.asanyarray(color_frame.get_data())
            return color_image, depth_image

    def check_end(self):
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            print("Stopping")
            self.robo_move('stop')
            return True
        return False

    def first_frame(self):
        # Set up initial bounding box for tracking
        while True:
            # grab one frame
            frames = self.pipeline.wait_for_frames()
            color_init = frames.get_color_frame()
            if not color_init:
                continue

            frame1 = np.asanyarray(color_init.get_data())


            # opencv tracker
            self.tracker = cv.TrackerKCF_create()
            # select custom bbox that opencv will track
            bbox = [200, 200, 300, 300]  # cv.selectROI(frame2, False)
            ok = self.tracker.init(frame1, bbox)
            break

        self.current_cog = [300, 300]
        self.x = 0
        self.repeat = False
    def locate(self, iteration):
        if iteration == 1:
            while True:
                color_frame, depth_frame = self.grab_frame()

                # remove depth background
                depth_image_3d = np.dstack((depth_frame , depth_frame , depth_frame ))  # depth image is 1 channel, color is 3 channels
                depth_frame = np.where((depth_image_3d > self.clipping_distance) | (depth_image_3d <= 0), 255 ,color_frame)

                color_check_frame = cv.blur(depth_frame, (60, 60))
                color_check_frame = cv.cvtColor(color_check_frame, cv.COLOR_BGR2HSV)
                #color_check_frame = cv.threshold(color_check_frame, 100, 255, cv.THRESH_BINARY)[1]

                # check for red
                mask1 = cv.inRange(color_check_frame, (0, 50, 20), (15, 255, 255))
                mask2 = cv.inRange(color_check_frame, (170, 50, 20), (180, 255, 255))

                ## Merge the mask and crop the red regions
                mask = cv.bitwise_or(mask1, mask2)
                cropped = cv.bitwise_and(color_check_frame, color_check_frame, mask=mask)
                h, s , v1 = cv.split(cropped)
                v1 = cv.threshold(v1, 1, 255, cv.THRESH_BINARY)[1]
                count, counts = np.unique(v1, return_counts=True)
                try:
                    if dict(zip(count, counts))[255] > 750:
                        if self.repeat:
                            print('RED FOUND')
                            self.repeat = False
                        else:
                            print('RED FOUND!')
                            self.repeat = True
                except KeyError:
                    pass

                self.robo_move('left')
                cv.imshow('1', color_check_frame)
                cv.imshow('2', v1)

                if self.check_end():
                    break

    def turn_around(self):
        for i in range(10):
            self.robo_move('left')

    def avoid_rocks(self):
        pass

    def find_person(self):
        pass

    def touch_goal(self):
        pass

    def run(self):
        self.first_frame()
        self.locate(1)
        self.turn_around()
        self.avoid_rocks()
        self.find_person()
        self.locate(2)
        self.avoid_rocks()
        self.touch_goal()
        #self.testing()

    def testing(self):
        try:
            while True:

                color_image, depth_colormap_image = self.grab_frame()



                img = cv.cvtColor(color_image, cv.COLOR_BGR2GRAY)
                img = cv.blur(img, (100, 100))
                img = cv.threshold(img, 130, 255, cv.THRESH_BINARY)
                img = img[1]
                mg = cv.blur(img, (30, 30))
                img = cv.threshold(img, 100, 255, cv.THRESH_BINARY)
                img = img[1]
                '''img = cv.equalizeHist(img[1])
                img = cv.blur(img, (9,9))
                img_x = cv.Sobel(img, 2, 1, 0);
                img_y = cv.Sobel(img, 2, 0, 1);
                abs_grad_x = cv.convertScaleAbs(img_x);
                abs_grad_y = cv.convertScaleAbs(img_y);
                img = cv.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0);
        
                img = cv.threshold(img, 40, 255, cv.THRESH_BINARY)
                img = cv.blur(img[1], (9, 9))
                img = cv.threshold(img, 100, 255, cv.THRESH_BINARY)
                img = img[1]'''

                height, width, = img.shape
                x_vals, y_vals = np.where(img == 255)
                pixels = len(x_vals)

                # if cog is off-screen, stop moving and wait
                try:
                    cog = [int(float(sum(y_vals)) / len(y_vals)), int(float(sum(x_vals)) / len(x_vals))]
                except ZeroDivisionError:
                    cog = self.current_cog
                    self.robo_move('stop')
                    time.sleep(0.01)

                if pixels < 500:
                    self.robo_move('stop')
                    cog = [200, 150]

                # reduce cog jittering
                if cog[0] - self.current_cog[0] > 40:
                    cog[0] = self.current_cog[0] + 40
                elif cog[0] - self.current_cog[0] < -40:
                    cog[0] = self.current_cog[0] - 40
                if cog[1] - self.current_cog[1] > 40:
                    cog[1] = self.current_cog[1] + 40
                elif cog[1] - self.current_cog[1] < -40:
                    cog[1] = self.current_cog[1] - 40
                self.current_cog = cog

                cv.circle(img, cog, 20, 150, 20)
                '''if x < 3:
                    x+=1
                    continue
                else:
                    x=0'''
                # print(cog[1],height)
                # cog is too far left
                '''if cog[0] > width * 0.75:
                    print('turning right!')
                    controller.setTarget(1, 6000)
                    time.sleep(0.01)
                    controller.setTarget(2, 5100)
                    time.sleep(0.6)
        
                # cog is too far right
                elif cog[0] < width * 0.25:
                    print('turning left!')
                    controller.setTarget(1, 6000)
                    time.sleep(0.01)
                    controller.setTarget(2, 6900)
                    time.sleep(0.6)
        
                # cog is too far up (move forward)
                elif cog[1] < height * 0.85:
                    print('VROOOOM')
                    controller.setTarget(2, 6000)
                    time.sleep(0.01)
                    controller.setTarget(1, 5300)
                    time.sleep(0.7)
        
                # lost cog (stop)
                elif cog[1] > height * 0.66:
                    print('Help me! STOP!')
                    controller.setTarget(1, 6000)
                    time.sleep(0.01)
                    controller.setTarget(2, 6000)
                    time.sleep(0.01)
                else:
                    print('STOP!')
                    controller.setTarget(1, 6000)
                    time.sleep(0.01)
                    controller.setTarget(2, 6000)
                    time.sleep(0.01)
        '''
                cv.imshow('Depth', depth_colormap_image)
                cv.imshow('RealSense', img)
                self.robo_move('stop')

                if self.check_end():
                    break



        finally:

            # Stop streaming
            self.pipeline.stop()
            self.robo_move('stop')

        cv.destroyAllWindows()


robo = Robo(0.75)
robo.run()