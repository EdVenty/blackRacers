import RobotAPI as rapi
import time as t
import random
import RPi.GPIO as GPIO
import queue
import asyncio
from threading import Thread
import logging
from NNPAPI import *
import cv2
import numpy as np
import time
# from cv2 import aruco


GPIO.setwarnings(False)
# pins = PinConfig(
#     DigitalMotorsPlatformDevice(
#         DigitalMotorDevice(17, 4), 
#         DigitalMotorDevice(22, 27)
#     )
# )
pins.add_devices(
    PWMMotorPlatformDevice(
        PWMMotorDevice(
            2, 3, invert_pwm_duty_cicle=True
        ),
        PWMMotorDevice(
            17, 4, invert_pwm_duty_cicle=True
        )
    )
)
robot = NNPAPI(pins)
robot.start_control_thread()

ARUCO_DICT = {
	"DICT_4X4_50": cv2.aruco.DICT_4X4_50,
	"DICT_4X4_100": cv2.aruco.DICT_4X4_100,
	"DICT_4X4_250": cv2.aruco.DICT_4X4_250,
	"DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
	"DICT_5X5_50": cv2.aruco.DICT_5X5_50,
	"DICT_5X5_100": cv2.aruco.DICT_5X5_100,
	"DICT_5X5_250": cv2.aruco.DICT_5X5_250,
	"DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
	"DICT_6X6_50": cv2.aruco.DICT_6X6_50,
	"DICT_6X6_100": cv2.aruco.DICT_6X6_100,
	"DICT_6X6_250": cv2.aruco.DICT_6X6_250,
	"DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
	"DICT_7X7_50": cv2.aruco.DICT_7X7_50,
	"DICT_7X7_100": cv2.aruco.DICT_7X7_100,
	"DICT_7X7_250": cv2.aruco.DICT_7X7_250,
	"DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
	"DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
	"DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
	"DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
	"DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

# try:
#     robot.move(MotorMode.FORWARD, MotorMode.FORWARD, 1, wait_until_complete=True)
#     print("Finish!")
# finally:
#     GPIO.cleanup()
# robot.move(DigitalMotorMode.FORWARD, DigitalMotorMode.FORWARD, 10)

class PD(object):
    _kp = 0.0
    _kd = 0.0
    _prev_error = 0.0
    _timestamp = 0

    def __init__(self, pk: int = ..., dk: int = ...):
        if pk is not ...: self._kp = pk
        if dk is not ...: self._kd = dk

    def set_p_gain(self, value):
        self._kp = value

    def set_d_gain(self, value):
        self._kd = value

    def process(self, error):
        timestamp = int(round(time.time() * 1000))
        output = self._kp * error + self._kd / (timestamp - self._timestamp) * (error - self._prev_error)
        self._timestamp = timestamp
        self._prev_error = error
        return output

thresh1 = 0
thresh2 = 0
aruco_pd = PD(0.001, 0.00001)

def find_aruco(frame, draw_frame):
    arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT["DICT_4X4_50"])
    arucoParams = cv2.aruco.DetectorParameters_create()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict,
	parameters=arucoParams)
    data = []
    if len(corners) > 0:
        # print(corners)
        ids = ids.flatten()
        for (markerCorner, markerID) in zip(corners, ids):
            # print("[INFO] ArUco marker ID: {}".format(markerID))
            area = cv2.contourArea(markerCorner)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # draw the bounding box of the ArUCo detection
            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
            data.append((
                markerID,
                (topLeft, topRight, bottomRight, bottomLeft),
                (cX, cY),
                area
            ))
    return data
def find_aruco_in_movement(id: int, direction=0):
    while True:
        frame = robot.get_frame()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        for _id, coord, (cX, cY), area in find_aruco(frame, frame):
            # print(id)
            if _id == id:
                U = aruco_pd.process(640 // 2 - cX)
                # print(U)
                if U > 0:
                    robot.move(DigitalMotorMode.BACKWARD, DigitalMotorMode.FORWARD, U, wait_until_complete=True)
                else: 
                    robot.move(DigitalMotorMode.FORWARD, DigitalMotorMode.BACKWARD, U * -1, wait_until_complete=True)
                return
        robot.set_frame(frame)
        if direction == 0:
            robot.move(DigitalMotorMode.BACKWARD, DigitalMotorMode.FORWARD, 0.3, True)
        else:
            robot.move(DigitalMotorMode.FORWARD, DigitalMotorMode.BACKWARD, 0.3, True)
        time.sleep(0.1)
        if direction == 1:
            robot.move(DigitalMotorMode.BACKWARD, DigitalMotorMode.FORWARD, 0.1, True)
        else:
            robot.move(DigitalMotorMode.FORWARD, DigitalMotorMode.BACKWARD, 0.1, True)

def move_to_aruco(id: int, area_to=40000, direction=0):
    # timer = 0
    find_aruco_in_movement(id, direction)
    while True:
        frame = robot.get_frame()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        robot.move(DigitalMotorMode.FORWARD, DigitalMotorMode.FORWARD, 0.2, True)
        # if time.time() - timer > 3:
        #     find_aruco_in_movement(id, direction)
        #     timer = time.time()
        for _id, coord, (cX, cY), area in find_aruco(frame, frame):
            if _id == id:
                print(area)
                if area > area_to:
                    # print(area)
                    return 
                U = aruco_pd.process(640 // 2 - cX)
                # print(U)
                if U > 0:
                    robot.move(DigitalMotorMode.BACKWARD, DigitalMotorMode.FORWARD, U, wait_until_complete=True)
                else: 
                    robot.move(DigitalMotorMode.FORWARD, DigitalMotorMode.BACKWARD, U * -1, wait_until_complete=True)
        robot.set_frame(frame)
# find_aruco_in_movement(0, 0)
# print("Found 0")
# move_to_aruco(0)
# print("Parked 0")
# find_aruco_in_movement(1, 0)
# print("Found 1")
# move_to_aruco(1, 10000)
# print("Parked 1")
# find_aruco_in_movement(2, 1)
# print("Found 2")
# move_to_aruco(2, 20000)
# print("Parked 2")
# find_aruco_in_movement(3, 0)
# print("Found 3")
# move_to_aruco(3, 20000)
# print("Parked 3")
# find_aruco_in_movement(4, 1)
# print("Found 4")
# move_to_aruco(4, 20000)
# print("Parked 4")
# move_to_aruco(0)

# move_to_aruco(1, 40000)
# move_to_aruco(2, 40000, 0)
# move_to_aruco(3, 40000, 1)
# move_to_aruco(4, 40000, 0)
# move_to_aruco(5, 40000, 1)
# move_to_aruco(6, 30000, 1)

# move_to_aruco(8, 40000, 0)
# move_to_aruco(9, 20000, 0)
# move_to_aruco(10, 20000, 1)
# move_to_aruco(4, 40000, 0)
# move_to_aruco(7, 10000, 0)
# move_to_aruco(1, 40000, 0)

# move_to_aruco(7, 30000, 0)
# while True:
#     k = robot.get_key()
    # frame = cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2))
    # if k == 87:
    #     robot.move(DigitalMotorMode.FORWARD, DigitalMotorMode.FORWARD, 0.2, True)
    # elif k == 65:
    #     robot.move(DigitalMotorMode.BACKWARD, DigitalMotorMode.FORWARD, 0.2, True)
    # elif k == 83:
    #     robot.move(DigitalMotorMode.BACKWARD, DigitalMotorMode.BACKWARD, 0.2, True)
    # elif k == 68:
    #     robot.move(DigitalMotorMode.FORWARD, DigitalMotorMode.BACKWARD, 0.2, True)
    # elif k == 219:
    #     thresh1 -= 1
    # elif k == 221:
    #     thresh1 += 1
    # elif k == 37:
    #     thresh2 -= 1
    # elif k == 39:
    #     thresh2 += 1

    # cv2.aruc
    # else:
    #     if k != -1: print(k)
    # sigma=0.1
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # kernel_size = 5
    # gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)
    # v = np.median(gray)
    # lower = int(max(0, (1.0 - sigma) * v))
    # upper = int(min(255, (1.0 + sigma) * v))
    # # thresh = cv2.adaptiveThreshold(gray, 255,
	# #     cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 10)
    # # out = cv2.merge(frame, gray)
    # c = cv2.Canny(gray, lower, upper)

    # rho = 1  # distance resolution in pixels of the Hough grid
    # theta = np.pi / 180  # angular resolution in radians of the Hough grid
    # threshold = 15  # minimum number of votes (intersections in Hough grid cell)
    # min_line_length = 50  # minimum number of pixels making up a line
    # max_line_gap = 20  # maximum gap in pixels between connectable line segments

    # lines = cv2.HoughLinesP(c, rho, theta, threshold, np.array([]),
    #                 min_line_length, max_line_gap)

    # for line in lines:
    #     for x1,y1,x2,y2 in line:
    #         cv2.line(frame, (x1,y1),(x2,y2),(255,0,0),5)
    
        # # flatten the ArUco IDs list
        # ids = ids.flatten()
        # # loop over the detected ArUCo corners
        # for (markerCorner, markerID) in zip(corners, ids):
        #     # extract the marker corners (which are always returned in
        #     # top-left, top-right, bottom-right, and bottom-left order)
        #     corners = markerCorner.reshape((4, 2))
        #     (topLeft, topRight, bottomRight, bottomLeft) = corners
        #     # convert each of the (x, y)-coordinate pairs to integers
        #     topRight = (int(topRight[0]), int(topRight[1]))
        #     bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
        #     bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
        #     topLeft = (int(topLeft[0]), int(topLeft[1]))

        #     # draw the bounding box of the ArUCo detection
        #     cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
        #     cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
        #     cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
        #     cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
        #     # compute and draw the center (x, y)-coordinates of the ArUco
        #     # marker
        #     cX = int((topLeft[0] + bottomRight[0]) / 2.0)
        #     cY = int((topLeft[1] + bottomRight[1]) / 2.0)
        #     cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
        #     # draw the ArUco marker ID on the image
        #     cv2.putText(frame, str(markerID),
        #         (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
        #         0.5, (0, 255, 0), 2)
        #     print("[INFO] ArUco marker ID: {}".format(markerID))
        #     # show the output image
        #     cv2.imshow("Image", frame)
        #     cv2.waitKey(0)

    
    # robot.move(DigitalMotorMode.FORWARD, DigitalMotorMode.FORWARD, 2, True)
    # robot.move(DigitalMotorMode.BACKWARD, DigitalMotorMode.FORWARD, 0.35, True)

#     frame = robot.get_frame()
#     k = robot.get_key()
# #     # if k == 87:
# #     #     robot.led(0)
# #     #     robot.move(1, 1, 1000)
# #     #     robot.led(1)
#     robot.set_frame(frame)
    
#     # time.sleep(0.1)
#     # robot.led(1)
#     # time.sleep(1)
#     # robot.led(0)
#     # time.sleep(1)