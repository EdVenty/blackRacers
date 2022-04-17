# pyinstaller --onefile --noconsole start_robot.py
__author__ = 'Yuri Glamazdin <yglamazdin@gmail.com>'
__version__ = '1.6'

import json
import os
import socket as sc
import threading
import time
import tkinter.filedialog as tkFileDialog
import tkinter as tk
import cv2
import numpy as np
import zmq
import zlib
import base64
import InetConnection as InetConnection
# Create a UDP socket
import select

from ctypes import *
from ctypes.util import find_library
import platform
import numpy as np
import math
import warnings
import os
import pickle, base64

flag_udp_comand = False
flag_udp_event = False
flag_udp_turbo_show_window = False
flag_udp_show_window = False

show_system_message = False
fps_fix_timer = 0.04


video_show = 0
video_show2 = 3
video_show2_global = 0
video_show2_global = 0
video_show_work = False
flag_start_script = None
timer_wait_start = 10
lock_time = 10+60 * 30

# default libTurboJPEG library path
DEFAULT_LIB_PATHS = {
    'Darwin': ['/usr/local/opt/jpeg-turbo/lib/libturbojpeg.dylib'],
    'Linux': [
        '/usr/lib/x86_64-linux-gnu/libturbojpeg.so.0',
        '/opt/libjpeg-turbo/lib64/libturbojpeg.so'
    ],
    # 'Windows': ['C:/libjpeg-turbo-gcc64/bin/libturbojpeg.dll']
    'Windows': ['libturbojpeg.dll']
}

# error codes
# see details in https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/turbojpeg.h
TJERR_WARNING = 0
TJERR_FATAL = 1

# color spaces
# see details in https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/turbojpeg.h
TJCS_RGB = 0
TJCS_YCbCr = 1
TJCS_GRAY = 2
TJCS_CMYK = 3
TJCS_YCCK = 4

# pixel formats
# see details in https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/turbojpeg.h
TJPF_RGB = 0
TJPF_BGR = 1
TJPF_RGBX = 2
TJPF_BGRX = 3
TJPF_XBGR = 4
TJPF_XRGB = 5
TJPF_GRAY = 6
TJPF_RGBA = 7
TJPF_BGRA = 8
TJPF_ABGR = 9
TJPF_ARGB = 10
TJPF_CMYK = 11

# chrominance subsampling options
# see details in https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/turbojpeg.h
TJSAMP_444 = 0
TJSAMP_422 = 1
TJSAMP_420 = 2
TJSAMP_GRAY = 3
TJSAMP_440 = 4
TJSAMP_411 = 5

# miscellaneous flags
# see details in https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/turbojpeg.h
# note: TJFLAG_NOREALLOC cannot be supported due to reallocation is needed by PyTurboJPEG.
TJFLAG_BOTTOMUP = 2
TJFLAG_FASTUPSAMPLE = 256
TJFLAG_FASTDCT = 2048
TJFLAG_ACCURATEDCT = 4096
TJFLAG_STOPONWARNING = 8192
TJFLAG_PROGRESSIVE = 16384


class TurboJPEG(object):
    """A Python wrapper of libjpeg-turbo for decoding and encoding JPEG image."""

    def __init__(self, lib_path=None):
        turbo_jpeg = cdll.LoadLibrary(
            self.__find_turbojpeg() if lib_path is None else lib_path)
        self.__init_decompress = turbo_jpeg.tjInitDecompress
        self.__init_decompress.restype = c_void_p
        self.__init_compress = turbo_jpeg.tjInitCompress
        self.__init_compress.restype = c_void_p
        self.__destroy = turbo_jpeg.tjDestroy
        self.__destroy.argtypes = [c_void_p]
        self.__destroy.restype = c_int
        self.__decompress_header = turbo_jpeg.tjDecompressHeader3
        self.__decompress_header.argtypes = [
            c_void_p, POINTER(c_ubyte), c_ulong, POINTER(c_int),
            POINTER(c_int), POINTER(c_int), POINTER(c_int)]
        self.__decompress_header.restype = c_int
        self.__decompress = turbo_jpeg.tjDecompress2
        self.__decompress.argtypes = [
            c_void_p, POINTER(c_ubyte), c_ulong, POINTER(c_ubyte),
            c_int, c_int, c_int, c_int, c_int]
        self.__decompress.restype = c_int
        self.__compress = turbo_jpeg.tjCompress2
        self.__compress.argtypes = [
            c_void_p, POINTER(c_ubyte), c_int, c_int, c_int, c_int,
            POINTER(c_void_p), POINTER(c_ulong), c_int, c_int, c_int]
        self.__compress.restype = c_int
        self.__free = turbo_jpeg.tjFree
        self.__free.argtypes = [c_void_p]
        self.__free.restype = None
        self.__get_error_str = turbo_jpeg.tjGetErrorStr
        self.__get_error_str.restype = c_char_p
        # tjGetErrorStr2 is only available in newer libjpeg-turbo
        self.__get_error_str2 = getattr(turbo_jpeg, 'tjGetErrorStr2', None)
        if self.__get_error_str2 is not None:
            self.__get_error_str2.argtypes = [c_void_p]
            self.__get_error_str2.restype = c_char_p
        # tjGetErrorCode is only available in newer libjpeg-turbo
        self.__get_error_code = getattr(turbo_jpeg, 'tjGetErrorCode', None)
        if self.__get_error_code is not None:
            self.__get_error_code.argtypes = [c_void_p]
            self.__get_error_code.restype = c_int
        self.__scaling_factors = []

        class ScalingFactor(Structure):
            _fields_ = ('num', c_int), ('denom', c_int)

        get_scaling_factors = turbo_jpeg.tjGetScalingFactors
        get_scaling_factors.argtypes = [POINTER(c_int)]
        get_scaling_factors.restype = POINTER(ScalingFactor)
        num_scaling_factors = c_int()
        scaling_factors = get_scaling_factors(byref(num_scaling_factors))
        for i in range(num_scaling_factors.value):
            self.__scaling_factors.append(
                (scaling_factors[i].num, scaling_factors[i].denom))

    def decode_header(self, jpeg_buf):
        """decodes JPEG header and returns image properties as a tuple.
           e.g. (width, height, jpeg_subsample, jpeg_colorspace)
        """
        handle = self.__init_decompress()
        try:
            width = c_int()
            height = c_int()
            jpeg_subsample = c_int()
            jpeg_colorspace = c_int()
            jpeg_array = np.frombuffer(jpeg_buf, dtype=np.uint8)
            src_addr = self.__getaddr(jpeg_array)
            status = self.__decompress_header(
                handle, src_addr, jpeg_array.size, byref(width), byref(height),
                byref(jpeg_subsample), byref(jpeg_colorspace))
            if status != 0:
                self.__report_error(handle)
            return (width.value, height.value, jpeg_subsample.value, jpeg_colorspace.value)
        finally:
            self.__destroy(handle)

    def decode(self, jpeg_buf, pixel_format=TJPF_BGR, scaling_factor=None, flags=0):
        """decodes JPEG memory buffer to numpy array."""
        handle = self.__init_decompress()
        try:
            if scaling_factor is not None and \
                    scaling_factor not in self.__scaling_factors:
                raise ValueError('supported scaling factors are ' +
                                 str(self.__scaling_factors))
            pixel_size = [3, 3, 4, 4, 4, 4, 1, 4, 4, 4, 4, 4]
            width = c_int()
            height = c_int()
            jpeg_subsample = c_int()
            jpeg_colorspace = c_int()
            jpeg_array = np.frombuffer(jpeg_buf, dtype=np.uint8)
            src_addr = self.__getaddr(jpeg_array)
            status = self.__decompress_header(
                handle, src_addr, jpeg_array.size, byref(width), byref(height),
                byref(jpeg_subsample), byref(jpeg_colorspace))
            if status != 0:
                self.__report_error(handle)
            scaled_width = width.value
            scaled_height = height.value
            if scaling_factor is not None:
                def get_scaled_value(dim, num, denom):
                    return (dim * num + denom - 1) // denom

                scaled_width = get_scaled_value(
                    scaled_width, scaling_factor[0], scaling_factor[1])
                scaled_height = get_scaled_value(
                    scaled_height, scaling_factor[0], scaling_factor[1])
            img_array = np.empty(
                [scaled_height, scaled_width, pixel_size[pixel_format]],
                dtype=np.uint8)
            dest_addr = self.__getaddr(img_array)
            status = self.__decompress(
                handle, src_addr, jpeg_array.size, dest_addr, scaled_width,
                0, scaled_height, pixel_format, flags)
            if status != 0:
                self.__report_error(handle)
            return img_array
        finally:
            self.__destroy(handle)

    def encode(self, img_array, quality=85, pixel_format=TJPF_BGR, jpeg_subsample=TJSAMP_422, flags=0):
        """encodes numpy array to JPEG memory buffer."""
        handle = self.__init_compress()
        try:
            jpeg_buf = c_void_p()
            jpeg_size = c_ulong()
            height, width, _ = img_array.shape
            src_addr = self.__getaddr(img_array)
            status = self.__compress(
                handle, src_addr, width, img_array.strides[0], height, pixel_format,
                byref(jpeg_buf), byref(jpeg_size), jpeg_subsample, quality, flags)
            if status != 0:
                self.__report_error(handle)
            dest_buf = create_string_buffer(jpeg_size.value)
            memmove(dest_buf, jpeg_buf.value, jpeg_size.value)
            self.__free(jpeg_buf)
            return dest_buf.raw
        finally:
            self.__destroy(handle)

    def __report_error(self, handle):
        """reports error while error occurred"""
        if self.__get_error_code is not None:
            # using new error handling logic if possible
            if self.__get_error_code(handle) == TJERR_WARNING:
                warnings.warn(self.__get_error_string(handle))
                return
        # fatal error occurred
        raise IOError(self.__get_error_string(handle))

    def __get_error_string(self, handle):
        """returns error string"""
        if self.__get_error_str2 is not None:
            # using new interface if possible
            return self.__get_error_str2(handle).decode()
        # fallback to old interface
        return self.__get_error_str().decode()

    def __find_turbojpeg(self):
        """returns default turbojpeg library path if possible"""
        lib_path = find_library('turbojpeg')
        if lib_path is not None:
            return lib_path
        for lib_path in DEFAULT_LIB_PATHS[platform.system()]:
            if os.path.exists(lib_path):
                return lib_path
        if platform.system() == 'Linux' and 'LD_LIBRARY_PATH' in os.environ:
            ld_library_path = os.environ['LD_LIBRARY_PATH']
            for path in ld_library_path.split(':'):
                lib_path = os.path.join(path, 'libturbojpeg.so.0')
                if os.path.exists(lib_path):
                    return lib_path
        raise RuntimeError(
            'Unable to locate turbojpeg library automatically. '
            'You may specify the turbojpeg library path manually.\n'
            'e.g. jpeg = TurboJPEG(lib_path)')

    def __getaddr(self, nda):
        """returns the memory address for a given ndarray"""
        return cast(nda.__array_interface__['data'][0], POINTER(c_ubyte))


# sock.setblocking(1)
server_address_udp_turbo = ('192.168.4.1', 5001)
server_address_udp_event = ('192.168.4.1', 5003)
server_address_udp_command = ('192.168.4.1', 4999)
frame_udp_turbo = np.zeros((480, 640, 3), np.uint8)
fps_udp_turbo = 0
time_frame = 0


def udp_work_turbo():
    global flag_udp_turbo_show_window, server_address_udp, frame_udp_turbo, fps_udp_turbo, time_frame, fps_fix_timer
    sock = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
    sock.setblocking(0)
    name_window = "Udp TURBO image"
    fps_count = 0
    fps_timer = time.time()
    timer_r = time.time()
    try:
        jpeg = TurboJPEG()
    except:
        pass

    while (True):

        if flag_udp_turbo_show_window:

            try:
                if time.time() - timer_r > fps_fix_timer:
                    timer_r = time.time()

                    sent = sock.sendto("g".encode('utf-8'), server_address_udp_turbo)

                    ready = select.select([sock], [], [], 0.05)
                    if ready[0]:
                        # data = sock.recvmsg()
                        data = sock.recv(65507)
                        array = np.frombuffer(data, dtype=np.dtype('uint8'))
                        img = jpeg.decode(array)

                        frame_udp_turbo = img
                        time_frame = time.time()
                        fps_count += 1

                else:
                    time.sleep(0.001)
            except:
                time.sleep(0.1)
                pass
            if time.time() - fps_timer > 1:
                fps_timer = time.time()
                fps_udp_turbo = fps_count
                # print(fps)
                fps_count = 0


        else:
            cv2.destroyWindow(name_window)
            time.sleep(0.1)


my_thread_udp_turbo = threading.Thread(target=udp_work_turbo)
my_thread_udp_turbo.daemon = True
my_thread_udp_turbo.start()

server_address_udp = ('192.168.4.1', 5000)

frame_udp = np.zeros((480, 640, 3), np.uint8)
fps_udp = 0


def udp_work():
    global flag_udp_show_window, server_address_udp, fps_udp, frame_udp, time_frame, fps_fix_timer
    sock = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
    sock.setblocking(0)
    name_window = "Udp image"
    fps_count = 0
    fps_timer = time.time()
    timer_r = time.time()

    while (True):
        if flag_udp_show_window:
            try:
                if time.time() - timer_r > fps_fix_timer:
                    timer_r = time.time()
                    sent = sock.sendto("g".encode('utf-8'), server_address_udp)
                    ready = select.select([sock], [], [], 0.05)
                    # print(ready)
                    if ready[0]:

                        # data = sock.recv(65507)
                        # array = np.frombuffer(data, dtype=np.dtype('uint8'))
                        # img = cv2.imdecode(array, 1)
                        # frame_udp = img
                        # time_frame = time.time()
                        # fps_count += 1

                        t = time.time()
                        good = False
                        while 1:
                            good = False
                            try:
                                data = sock.recv(65507)
                                good = True
                                break
                            except:
                                time.sleep(0.001)
                                pass
                            if time.time() - t > 0.1:
                                break
                        if good:
                            array = np.frombuffer(data, dtype=np.dtype('uint8'))
                            img = cv2.imdecode(array, 1)
                            frame_udp = img
                            time_frame = time.time()
                            fps_count += 1
                else:
                    time.sleep(0.001)
            except:
                time.sleep(0.1)
                pass
            if time.time() - fps_timer > 1:
                fps_timer = time.time()
                fps_udp = fps_count
                # print(fps)
                fps_count = 0


        else:
            cv2.destroyWindow(name_window)
            time.sleep(0.1)


my_thread_udp = threading.Thread(target=udp_work)
my_thread_udp.daemon = True
my_thread_udp.start()
list_udp_send = []


def udp_event():
    global flag_udp_event, server_address_udp_event, list_udp_send
    sock = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
    sock.setblocking(0)
    fps_count = 0
    fps_timer = time.time()
    timer_r = time.time()

    while (True):
        if flag_udp_event:
            try:
                if len(list_udp_send) > 0:
                    # print(len(list_udp_send))
                    for mess in list_udp_send:
                        # print("send udp", str(mess))
                        sent = sock.sendto(str(mess).encode('utf-8'), server_address_udp_event)
                        list_udp_send.remove(mess)
                        # ready = select.select([sock], [], [], 0.05)
                        # print(ready)
                        # if ready[0]:
                        #     data = sock.recv(65507)
                        #     if len(data) == 4:
                        #         # This is a message error sent back by the server
                        #         if (data == "FAIL"):
                        #             continue
                        #     fps_count += 1
                else:
                    time.sleep(0.001)
            except:
                time.sleep(0.1)
                pass
            if time.time() - fps_timer > 1:
                fps_timer = time.time()
                fps_udp = fps_count
                # print(fps)
                fps_count = 0


        else:
            time.sleep(0.1)


my_thread_udp_event = threading.Thread(target=udp_event)
my_thread_udp_event.daemon = True
my_thread_udp_event.start()

udp_commanda = []

message_s_udp = ""


def udp_command():
    global flag_udp_comand, server_address_udp_command, udp_commanda, message_s_udp
    global video_show2_global, started_flag, video_show2
    sock = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
    sock.setblocking(0)
    fps_count = 0
    fps_timer = time.time()
    timer_r = time.time()

    while (True):
        if flag_udp_comand:
            try:
                if len(udp_commanda) > 0:
                    for udp_c in udp_commanda:
                        # print("send udp, ", udp_c, server_address_udp_command)
                        sent = sock.sendto(udp_c, server_address_udp_command)
                        # if udp_c == b't':
                        ready = select.select([sock], [], [], 0.05)
                        if ready[0]:
                            data = sock.recv(65507)
                            message_s_udp += data.decode('utf-8')

                        udp_commanda.remove(udp_c)
                else:
                    time.sleep(0.001)
            except:
                time.sleep(0.1)
                pass
        else:
            time.sleep(0.1)


my_thread_udp_event = threading.Thread(target=udp_command)
my_thread_udp_event.daemon = True
my_thread_udp_event.start()

# os.system('pip install pypiwin32')
FLAG_PYPIWIN32 = True

MOUSE_FLAG = False

JOYSTIK_FLAG = False
if JOYSTIK_FLAG:
    import pygame

    pygame.init()
    pygame.joystick.init()

# FRAME = np.ndarray(shape=(240, 320, 3), dtype=np.uint8)
FRAME = 0
DATASET = False

if DATASET:
    import pickle

ic = InetConnection.InetConnect(sc.gethostname(), "client")
# ic.take_list()


Reset = "\x1b[0m"
Bright = "\x1b[1m"
Dim = "\x1b[2m"
Underscore = "\x1b[4m"
Blink = "\x1b[5m"
Reverse = "\x1b[7m"
Hidden = "\x1b[8m"

FgBlack = "\x1b[30m"
FgRed = "\x1b[31m"
FgGreen = "\x1b[32m"
FgYellow = "\x1b[33m"
FgBlue = "\x1b[34m"
FgMagenta = "\x1b[35m"
FgCyan = "\x1b[36m"
FgWhite = "\x1b[37m"

BgBlack = "\x1b[40m"
BgRed = "\x1b[41m"
BgGreen = "\x1b[42m"
BgYellow = "\x1b[43m"
BgBlue = "\x1b[44m"
BgMagenta = "\x1b[45m"
BgCyan = "\x1b[46m"
BgWhite = "\x1b[47m"

flag_inet_work = False

port = "5557"

list_combobox = []
robot_adres = "-1"
robot_adres_inet = "-1"

# vd = vsc.VideoClient().inst()
# socket.connect ("tcp://192.168.88.19:%s" % port)


# pass_hash="d5a"
pass_hash = ""
lock_pass = None

try:
    file = open('lock.txt', "r")
    lock_pass = file.readline()
except:
    pass

try:
    file = open("password", "r")
    pass_hash = file.readline()
except:
    pass
# print("pass hash (",pass_hash,")")

selected_file = ""
selected_file_no_dir = ""
started_flag = 0
recive_flag = 0
key_started = -1
key_pressed = 0
mouse_x = -1
mouse_y = -1
fps_show = 1
fps = 0
socket_2_connected = False
joy_data = []

joy_x = 0
joy_y = 0
key_pressed_dataset = 0
flag_sended_file = False
resize_windows = False

last_joy_activ = time.time()


def camera_work():
    global root, video_show2, socket2, video_show2_global, image, started_flag, flag_inet_work, socket_2_connected, DATASET, FRAME, resize_windows, frame_turbo, time_frame
    global flag_start_script, timer_wait_start, fps_fix_timer
    ic_v = InetConnection.InetConnect(sc.gethostname() + "_v", "client")
    ic_v.connect()
    image = np.zeros((480, 640, 3), np.uint8)
    time_frame = time.time()
    frames = 0
    frames_time = time.time()
    context = zmq.Context()
    flag_destroy = False
    timer_clip_fps = time.time()

    while 1:
        # try:
        # print("s",started_flag)
        # print("video status", video_show2_global, video_show2)

        if video_show2_global == 1:
            flag_destroy = True
            if video_show2 == 1:  # and started_flag == 1:
                # print("vid1", flag_inet_work)
                if time.time() - timer_clip_fps > fps_fix_timer:
                    timer_clip_fps = time.time()
                    if flag_inet_work == True:
                        if (flag_udp_show_window == False and flag_udp_turbo_show_window == False):

                            ic_v.send_and_wait_answer(robot_adres_inet, "p|" + pass_hash)
                            # print("p")
                            while 1:

                                try:
                                    j_mesg, jpg_bytes = ic_v.take_answer_bytes()
                                    if len(jpg_bytes) > 1:

                                        A = np.frombuffer(jpg_bytes, dtype=j_mesg['dtype'])
                                        # arrayname = md['arrayname']sccv2.waitKey(1)

                                        # image = A.reshape(j_mesg['shape'])
                                        # print(len(A))
                                        image = A.reshape(j_mesg['shape'])
                                        image = cv2.imdecode(image, 1)
                                        time_frame = time.time()
                                        frames += 1
                                    else:
                                        break

                                except:
                                    pass


                    else:
                        if flag_udp_show_window != True and flag_udp_turbo_show_window != True:
                            try:
                                socket2.send_string("1", zmq.NOBLOCK)  # zmq.NOBLOCK
                            except:
                                # print("error0")
                                pass
                            md = ""
                            t = time.time()
                            # ee=0

                            while 1:

                                try:
                                    md = socket2.recv_json(zmq.NOBLOCK)
                                except zmq.ZMQError as e:
                                    # time.sleep(0.001)
                                    # print("error1",ee)
                                    # ee+=1
                                    pass
                                if md != "":
                                    break
                                if time.time() - t > 1:
                                    # print("break video")
                                    break

                            if md != "" and video_show2 == 1:
                                msg = 0
                                t = time.time()
                                while 1:
                                    try:
                                        msg = socket2.recv(zmq.NOBLOCK)
                                    except:
                                        pass
                                        # print("error2")
                                    if msg != 0:
                                        break
                                    if time.time() - t > 1:
                                        # print("break video")
                                        break

                                try:

                                    A = np.frombuffer(msg, dtype=md['dtype'])
                                    # arrayname = md['arrayname']sccv2.waitKey(1)
                                    image = A.reshape(md['shape'])
                                    image = cv2.imdecode(image, 1)
                                    time_frame = time.time()
                                    # print("frame", md['shape'])
                                    # cv2.imshow("Robot frame", image)
                                    # cv2.waitKey(1)
                                    frames += 1
                                    # if DATASET:
                                    #     FRAME = image.copy()


                                except:
                                    pass

                # отрисовываем картинку
                if flag_udp_show_window != True or flag_udp_turbo_show_window != True:
                    if time.time() - time_frame > 2:
                        if image is None:
                            image = np.ones((480, 640, 3), dtype=np.uint8)
                        cv2.putText(image, "video lost", (10, int(image.shape[0] - 10)), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                    1,
                                    (255, 255, 255))
                        for i in range(int(time.time() - time_frame)):
                            cv2.putText(image, ".", (140 + (i * 10), int(image.shape[0] - 10)),
                                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                                        (255, 255, 255))

                        # автореконнект видео
                        if time.time() - time_frame > 5:
                            # print("reconnect video")
                            if flag_inet_work == True:
                                # ic_v.disconnect()
                                # print("disconnect")
                                pass
                            else:
                                if socket_2_connected:
                                    socket2.close()

                            time_frame = time.time()
                            video_show2 = 0
                            continue

                if frames_time < time.time():
                    fps = frames
                    # print("fps:",fps)
                    frames_time = int(time.time()) + 1
                    # print(frames_time)
                    frames = 0
                if flag_udp_show_window:
                    image = frame_udp
                    # time_frame = time.time()

                if flag_udp_turbo_show_window:
                    image = frame_udp_turbo
                    # time_frame = time.time()
                if image is None: continue
                # FRAME = image.copy()
                if resize_windows:
                    image = cv2.resize(image, (640, 480))

                if fps_show == 1:
                    text_fps = "fps:"
                    if flag_udp_show_window:
                        fps = fps_udp
                        text_fps = "fpsu:"

                    if flag_udp_turbo_show_window:
                        fps = fps_udp_turbo
                        text_fps = "fpsut:"

                    cv2.putText(image, text_fps + str(fps), (int(image.shape[1] - 110), int(image.shape[0] - 10)),
                                cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                                (255, 255, 255))

                if flag_start_script is not None:
                    try:
                        image = np.zeros((480, 640, 3), np.uint8)
                        if flag_start_script is not None:
                            cv2.putText(image, "Connect to robot... " + str(
                                round(timer_wait_start - abs(time.time() - flag_start_script), 2)), (50, 240),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
                        if time.time() - flag_start_script > 0:
                            flag_start_script = None
                    except:
                        pass
                cv2.imshow("Robot frame", image)
                # cv2.moveWindow("Robot frame", 300, 300)

                # искуственно понижаем фпс
                if flag_udp_turbo_show_window != True or flag_udp_show_window != True:
                    time.sleep(0.001)
                cv2.waitKey(1)
                continue

            if video_show2 == 0:

                if flag_inet_work == True:
                    # print("conect to sknet")
                    video_show2 = 1
                    ic_v.connect()

                    continue
                else:
                    # print("Connecting to soft...", robot_adres)
                    cv2.destroyAllWindows()
                    # for i in range(1, 5):
                    #     cv2.waitKey(1)
                    #
                    socket2 = context.socket(zmq.REQ)
                    # socket2.setTcpNoDelay(True)
                    print("start")
                    # socket2.setsockopt(zmq.SNDTIMEO, 500)
                    # socket2.setsockopt(zmq.RCVTIMEO, 500)

                    socket2.connect("tcp://" + robot_adres + ":5555")
                    socket_2_connected = True
                    # print("connect ok")
                    # context = zmq.Context()
                    # socket2 = context.socket(zmq.REQ)
                    # socket2.setsockopt(zmq.LINGER, 0)
                    # socket2.connect("tcp://" + robot_adres + ":5555")
                    # socket2.send_string("1")  # send can block on other socket types, so keep track
                    # # use poll for timeouts:
                    # poller = zmq.Poller()
                    # poller.register(socket, zmq.POLLIN)
                    # if poller.poll(1 * 1000):  # 10s timeout in milliseconds
                    #     #msg = socket2.recv_json()
                    #     pass
                    # else:
                    #     print("Timeout processing auth request")

                    # these are not necessary, but still good practice:
                    pass

                image = np.zeros((480, 640, 3), np.uint8)
                cv2.putText(image, "Connect to robot...", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))

                time_frame = time.time()
                video_show2 = 1
                cv2.namedWindow("Robot frame")

                cv2.startWindowThread()

                # print("connected")

                continue
            if video_show2 == -1:
                # print("vid-1")
                # print("close socket2")

                cv2.destroyAllWindows()
                for i in range(1, 5):
                    cv2.waitKey(1)

                if flag_inet_work == True:
                    video_show2 = 3
                    continue

                if socket_2_connected:
                    socket2.close()
                    socket_2_connected = False

                time.sleep(0.1)
                video_show2 = 3
                # ic_v.disconnect()
                time.sleep(0.05)
                # print("video_show2", video_show2 )
                continue
            if video_show2 == 3:
                # print("vid3")
                # cv2.imshow("Robot frame", image)
                # cv2.destroyWindow("Robot frame")
                cv2.destroyAllWindows()
                for i in range(1, 5):
                    cv2.waitKey(1)

                time.sleep(0.05)
                continue
                # print("vid??", video_show2, "started_flag==", started_flag)

        else:

            if flag_destroy:
                cv2.destroyAllWindows()
                flag_destroy = False
            cv2.waitKey(1)
            video_show2 = 3
            time.sleep(0.1)
            # except:
            #     print("error video")
            #     pass


my_thread = threading.Thread(target=camera_work)
my_thread.daemon = True
my_thread.start()

ic = InetConnection.InetConnect(sc.gethostname() + "_r", "client")
ic.connect()


def status_lock(s):
    global lock_pass
    s = s.split("|")[1:]
    # print(s)
    if len(s) < 2: return
    if s[1] == "True":
        lock_pass = s[2]

        sec = float(s[2]) - time.time()
        if sec < 60:
            sec = str(int(sec)) + " sec"
        else:
            sec = str(int(sec // 60)) + " min"
        fg = 'green'
        color_log = FgGreen
        print(color_log + "The robot was successfully captured for " + sec)
        printt("The robot was successfully captured for " + sec, fg)
        file = open('lock.txt', 'w')
        file.write(lock_pass)
        file.close()
    else:
        sec = float(s[2])
        if sec < 60:
            sec = str(int(sec)) + " sec"
        else:
            sec = str(int(sec // 60)) + " min"

        fg = 'red'
        color_log = FgRed
        print(color_log + "Fail lock robot! need wait " + sec)
        printt("Fail lock robot! need wait " + sec, fg)
        lock_pass = None


def robot_recive_work():
    global video_show2, recive_flag, started_flag, flag_inet_work, ic, selected_file_no_dir, selected_file, robot_adres, flag_sended_file, flag_udp_comand, message_s_udp
    global udp_commanda, flag_start_script, show_system_message, lock_pass, flag_udp_show_window, flag_udp_turbo_show_window
    color_log = FgBlack
    # ic = InetConnection.InetConnect(sc.gethostname() + "_r", "client")
    # ic.connect()
    time_recive = time.time()
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    # socket.setsockopt(zmq.SNDTIMEO, 500)
    # socket.setsockopt(zmq.RCVTIMEO, 500)
    count_stoped = 0
    while 1:
        # try:
        # if recive_flag != 0:
        # print("recive_flag", recive_flag)
        time.sleep(0.1)
        if recive_flag == 1:
            # print("recive_flag",recive_flag)
            message_s = ""
            if flag_inet_work == True:
                message_s = ic.send_and_wait_answer(robot_adres_inet, "d|" + pass_hash)

                time_recive = time.time()
                pass

            else:

                if flag_udp_comand == False:
                    t = time.time()
                    while 1:
                        f = 0
                        try:
                            socket.send_string("data", zmq.NOBLOCK)  # zmq.NOBLOCK
                            f = 1
                        except zmq.ZMQError as e:
                            if e.errno == zmq.ETERM:
                                # print("error", e)
                                pass
                        if f == 1:
                            break
                        if time.time() - t > 1:
                            break
                    message_s = ""
                    t = time.time()
                    while 1:
                        f = 0
                        try:
                            message_s = socket.recv_string(zmq.NOBLOCK)
                            time_recive = time.time()
                            f = 1
                        except zmq.ZMQError as e:
                            if e.errno == zmq.ETERM:
                                pass
                                # print("error", e)
                        if message_s != "" or f == 1:
                            break

                        if time.time() - t > 1:
                            break
                else:
                    # elif flag_udp_comand:
                    # print("take console")
                    udp_commanda.append(b"t")
                    time.sleep(1)
                    message_s = message_s_udp
                    message_s_udp = ""
                    time_recive = time.time()
                    pass
            # print(message_s.encode('utf-8'))
            # message_s=message_s.replace("/n", "")

            if message_s == None:
                time.sleep(0.01)
                continue

            message_ss = message_s.split('\r\n')
            # print(len(message_ss),message_s )
            for message_s in message_ss:

                if time.time() - time_recive > 10:
                    print("lost connect ..")
                    printt("lost connect ..")
                    if flag_inet_work == True:
                        # ic.disconnect()
                        ic.connect()
                    else:
                        if flag_udp_comand == False:
                            time_recive = time.time()
                            socket.close()
                            context = zmq.Context()
                            socket = context.socket(zmq.REQ)

                            socket.connect("tcp://" + robot_adres + ":%s" % port)
                            socket.send_string("take|" + robot_adres)
                            otvet = socket.recv_string()
                            print("Connected to robot: " + BgGreen + otvet + Reset)
                            printt("Connected to robot: " + otvet, fg='white', bg='green')
                            recive_flag = 6
                            t = time.time()
                            while recive_flag == 6:
                                if time.time() - t > 5:
                                    break
                                time.sleep(0.01)

                            recive_flag = 1
                        print("reconected")
                        printt("reconected")
                        if started_flag:
                            recive_flag = 1
                        else:
                            recive_flag = 0

                # if message_s.find("stoping") >= 0:
                #     recive_flag=-1

                if message_s.find("|STOPED") >= 0:
                    count_stoped += 1
                    if (count_stoped > 2 and started_flag == 1):
                        count_stoped = 0
                        # recive_flag = 0
                        message_ss.remove(message_s)
                        # printt(message_s, fg='red')
                        printt("STOPED", fg='red')
                        mes = message_s.replace("|STOPED", FgRed + "STOPED" + Reset)
                        print(color_log + mes.rstrip())

                        color_log = FgBlack

                        video_show2 = -1
                        time.sleep(0.01)

                        started_flag = 0
                        time.sleep(0.01)
                        continue

                if message_s != "" and len(message_s) > 0 and message_s[0] != "|":
                    # обрезаем конец сообщения, спец символ
                    flag_start_script = None
                    fg = 'black'
                    if message_s.find("Traceback") >= 0 or message_s.find("Error:") >= 0 or message_s.find(
                            "Exception in") >= 0:
                        color_log = FgRed
                        video_show2 = -1
                        fg = 'red'

                    print(color_log + message_s.rstrip())
                    printt(message_s.rstrip(), fg)
                else:
                    if message_s != "":
                        if show_system_message:
                            print("sys:", message_s.rstrip())
                        if message_s.find("|run|") > -1:
                            s = message_s.split("|")
                            fg = 'blue'
                            print(color_log + "File start on robot: " + s[2].rstrip())
                            printt("File start on robot: " + s[2].rstrip(), fg)
                        if message_s.find("|fail_run|") > -1:
                            s = message_s.split("|")
                            fg = 'red'
                            print(FgRed + "Fail run file! Robot locked: " + s[2].rstrip())
                            printt("Fail run file! Robot locked: " + s[2].rstrip(), fg)

                        if message_s.find("|start_api") > -1:
                            # print("--------------------------------")
                            flag_start_script = None
                            color_log = FgBlack
                        if message_s.find("|ip|") > -1:
                            # print("--------------------------------")
                            flag_start_script = None
                            color_log = FgBlack
                            take_ip_from_robot(timer=0.1, message_s_ip=message_s)
                        if message_s.find("|lock|") > -1:
                            status_lock(message_s)

                        if message_s.find("|fail_stop|robot_locked|") != -1:
                            print(FgRed + "Fail stop! robot locked!")
                            printt("Fail stop! robot locked! need wait", "red")
                            lock_pass=None
                        if message_s.find("|error|") != -1:
                            print(FgRed + "Critical SkyNet error!!!" + message_s)
                            printt("Critical SkyNet error!!!" + message_s, "red")
                        if message_s.find("|error_udp_frame|") != -1:
                            s = message_s.split("|")
                            # print(s)
                            if flag_udp_show_window or flag_udp_turbo_show_window:
                                print(FgRed + "UDP error:" + str(s[2]))
                                printt("UDP error:" + str(s[2]), "red")
                            flag_udp_show_window=False
                            flag_udp_turbo_show_window=False

                        if message_s.find("|drop") != -1:
                            s = message_s.split("|")
                            if s[2] == "True":
                                fg = 'blue'
                                print(color_log + "robot unlocked: " + s[2].rstrip())
                                printt("robot unlocked: " + s[2].rstrip(), fg)
                            else:
                                print(FgRed + "Fail robot unlocked! need wait")
                                fg = 'red'
                                printt("Fail robot unlocked! need wait", fg)
                            lock_pass = None

                time.sleep(0.001)

        if recive_flag == -1:
            # print("reciv-1")
            color_log = FgBlack
            ret = ""

            if flag_inet_work == True:
                ret = ic.send_and_wait_answer(robot_adres_inet, "stop|" + str(lock_pass) + "|" + pass_hash)
                # ic.send_and_wait_answer(robot_adres_inet, "stopvideo|" + pass_hash)
                pass
            else:
                try:
                    socket.send_string("stop|" + str(lock_pass) + "|" + str(pass_hash))
                    ret = socket.recv_string()
                    color_log = FgRed
                    fg = "red"

                    if ret.find("|fail_stop|robot_locked|") != -1:
                        print(FgRed + "Fail stop! robot locked!")
                        printt("Fail stop! robot locked! need wait", fg)
                    if ret.find("|STOPED") != -1:
                        print(color_log + "STOPED")
                        printt("STOPED", fg)
                        started_flag = 0

                except:
                    pass
            # if started_flag == 1:
            #     print(ret.replace("STOPED", FgRed + "STOPED" + Reset))
            # recive_flag = 0
            recive_flag = 1
            time.sleep(0.01)
        if recive_flag == 2:
            # print("lock robot recive_flag", recive_flag)
            color_log = FgBlack
            ret = ""

            if flag_inet_work == True:
                ret = ic.send_and_wait_answer(robot_adres_inet,
                                              "lock|" + str(lock_pass) + "|" + str(lock_time) + "|" + pass_hash)
                time.sleep(0.5)
                # ic.send_and_wait_answer(robot_adres_inet, "stopvideo|" + pass_hash)
                pass
            else:
                try:
                    socket.send_string("lock|" + str(lock_pass) + "|" + str(lock_time) + "|" + pass_hash)
                    ret = socket.recv_string()
                except:
                    pass
            # time.sleep(0.01)
            # print("answer lock", ret)
            status_lock(ret)
            recive_flag = 1

        if recive_flag == 4:
            # print("lock robot recive_flag", recive_flag)
            color_log = FgBlack
            ret = ""

            if flag_inet_work == True:
                ret = ic.send_and_wait_answer(robot_adres_inet,
                                              "drop|" + str(lock_pass) + "|" + str(lock_time) + "|" + pass_hash)
                time.sleep(0.5)
                # ic.send_and_wait_answer(robot_adres_inet, "stopvideo|" + pass_hash)
                pass
            else:
                try:
                    socket.send_string("drop|" + str(lock_pass) + "|" + str(lock_time) + "|" + pass_hash)

                    ret = socket.recv_string()
                    print(FgRed + ret)
                    fg = 'red'
                    printt(ret, fg)

                except:
                    pass
            # time.sleep(0.01)
            # print("answer lock", ret)
            # status_lock(ret)
            recive_flag = 1

        if recive_flag == 3:
            count_stoped = 0
            # color_log = FgBlack
            fg = "blue"

            print(FgBlue + "open " + selected_file)

            with open(selected_file, 'rb') as myfile:
                fdata = myfile.read()

            data = {"filename": selected_file_no_dir, "data": fdata}
            b = zlib.compress(pickle.dumps(data), 9)
            data_to_send = base64.b64encode(b).decode("utf-8")
            if flag_inet_work:
                t1 = time.time()
                ic.clear()
                ic.send_and_wait_answer(robot_adres_inet,
                                        "run|" + data_to_send + "|" + str(lock_pass) + "|" + pass_hash)

                print("Sending file time:" + str(round(time.time() - t1, 3)) + " sec")
                printt("Sending file time:" + str(round(time.time() - t1, 3)) + " sec")

            else:

                if flag_udp_comand == False:
                    try:
                        # socket.send_string("start|" + selected_file_no_dir)
                        # res = socket.recv_string()
                        socket.connect("tcp://" + robot_adres + ":%s" % port)
                        socket.send_string("run|" + str(data_to_send) + "|" + str(lock_pass))
                        # t=time.time()
                        # otvet=""
                        # while 1:
                        #     f = 0
                        #     try:
                        #         otvet = socket.recv_string(zmq.NOBLOCK)
                        #         time_recive = time.time()
                        #         f = 1
                        #     except zmq.ZMQError as e:
                        #         if e.errno == zmq.ETERM:
                        #             pass
                        #             # print("error", e)
                        #     if message_s != "" or f == 1:
                        #         break
                        #
                        #     if time.time() - t > 5:
                        #
                        #         break

                        otvet = socket.recv_string()
                        if otvet == "":
                            print(BgRed + "Fail send file to robot" + Reset)
                        else:
                            if otvet.find("fail_run") != -1:
                                print("answer from robot: " + FgRed + otvet + Reset)
                                fg = 'red'
                                printt("answer from robot: " + otvet.rstrip(), fg)

                            else:
                                print("answer from robot: " + BgGreen + otvet + Reset)
                                fg = 'blue'
                                printt("answer from robot: " + otvet.rstrip(), fg)

                    except:

                        print(FgRed + "Start fail... try again" + Reset)

                else:
                    b = zlib.compress(pickle.dumps(data_to_send), 9)
                    udp_commanda.append(b"r" + b)
                    message_s_udp = ""
                    message_s = ""

                    time.sleep(0.5)
            started_flag = 1
            recive_flag = 1
            flag_sended_file = True

        if recive_flag == 6:
            # коннект

            ip_adress = sc.gethostbyname(sc.gethostname())

            # s = socket.recv_string(zmq.NOBLOCK)

            otvet = ""
            if flag_udp_comand == False:
                try:
                    socket.connect("tcp://" + robot_adres + ":%s" % port)
                    socket.send_string("take|" + ip_adress)
                    otvet = socket.recv_string()
                    print("Connected to robot: " + BgGreen + otvet + Reset)
                    printt("Connected to robot: " + otvet, fg='white', bg='green')
                except Exception as e:
                    printt("Error connect to robot", e)
                    pass
            else:
                printt("Taking UDP robot: " + robot_adres, fg='white', bg='green')

            pass
            recive_flag = 0

        time.sleep(0.05)
        # root.after(10, robot_recive_work)
    # except:
    #     #print("except reciver")
    #     pass


#
my_thread_print = threading.Thread(target=robot_recive_work)
my_thread_print.daemon = True
my_thread_print.start()


def Raw(ev):
    global recive_flag, root, video_show, robot_adres, started_flag, selected_file_no_dir, selected_file, video_show2, video_show2_global
    # video_show2 = 1
    recive_flag = 0
    if robot_adres == "-1":
        print(FgRed + "select robot")
        printt("select robot", fg='red')

        return
    # if selected_file_no_dir == "":
    #     print("select file!")
    #     return

    # if started_flag == 1:
    #     Stop(ev)
    video_show2_global = 1
    video_show2 = 0

    selected_file_no_dir = "/raw.py"
    # dir = os.path.abspath(os.curdir).replace("starter", '')
    dir = os.path.abspath(os.curdir)
    selected_file = dir.replace("\\", "/") + selected_file_no_dir
    root.title(selected_file)

    Start(ev)

    # socket.send_string("start|" + selected_file_no_dir)
    # res = socket.recv_string()

    started_flag = 1

    recive_flag = 1

    print(BgGreen + "RAW ON" + Reset)


def Video2(ev):
    global root, video_show2, robot_adres, socket2, video_show2_global, video_show_work
    if robot_adres == "-1":
        print(FgRed + "select robot")
        printt("select robot", fg='red')
        return

    if video_show2_global == 0:
        video_show2_global = 1
        video_show2 = 0

        print(FgYellow + "Video ON")
        # root.after(100, ShowVideo2)
    else:
        video_show2_global = 0
        video_show2 = 0
        # print(video_show_work)
        # while video_show_work == True:
        #     print("wait...")
        #     pass

        print(FgYellow + "Video2 OFF")
        # cv2.destroyAllWindows()
        # socket2.close()


def Quit(ev):
    global root
    root.destroy()


def send_selected_file(show_text=False):
    global selected_file, robot_adres, selected_file_no_dir, socket, recive_flag, flag_inet_work, flag_sended_file

    flag_sended_file = False
    # print("sending...", video_show2, recive_flag)
    # отсылка через интернет

    if flag_inet_work:
        # print("send_selected_file1")
        time.sleep(0.1)
        recive_flag = 4
        while flag_sended_file == False:
            time.sleep(0.01)
        # print("send_selected_file ok")
    else:
        pass
        # отсылка по локалке
        # time.sleep(0.1)
        # recive_flag = 4
        # # print("send log: recive flag = ", recive_flag)
        # # посылаем заголовок
        # while recive_flag == 4:
        #     # print("send log: recive flag = ", recive_flag)
        #     time.sleep(0.01)
        #     pass
        #
        # # посылаем сам файл
        # # print("send log: recive flag = ", recive_flag)
        # recive_flag = 5
        # while recive_flag == 5:
        #     # print("send log: recive flag = ", recive_flag)
        #     time.sleep(0.01)
        #     pass
        # посылаем сам файл
        # print("send log: recive flag = ", recive_flag)
        # recive_flag = 7
        # while recive_flag == 7:
        #     # print("send log: recive flag = ", recive_flag)
        #     time.sleep(0.01)
        #     pass

    started_flag = 0
    time.sleep(0.1)
    # cv2.destroyAllWindows()

    if show_text:
        print(FgBlue + "sended ", selected_file_no_dir)
        printt("sended " + selected_file_no_dir, fg='blue')


def Start(ev):
    global root, robot_adres, video_show2, video_show2_global, started_flag, recive_flag, socket, flag_inet_work
    global frame_udp, frame_udp_turbo, flag_start_script, frame, timer_wait_start
    # video_show2 = 1
    t = time.time()
    if robot_adres == "-1":
        print(FgRed + "select robot")
        printt("select robot", fg='red')
        return

    if selected_file_no_dir == "":
        print(FgRed + "select file!" + Reset)
        printt("select file", fg='red')
        return

    flag_start_script = time.time() + timer_wait_start

    Stop(ev, False)

    # send_selected_file()

    recive_flag = 3

    while recive_flag == 3:
        time.sleep(0.001)
        pass

    # else:
    #     # time.sleep(3)
    #     print("Send UDP file", selected_file_no_dir)
    #     with open(selected_file, 'rb') as myfile:
    #         data = myfile.read()
    #     b = zlib.compress(pickle.dumps([selected_file_no_dir,data]), 9)
    #     udp_commanda.append(b"f" + b)
    #     flag_sended_file = True
    #     # udp_commanda.append(b"r" + base64.b64encode(b))

    # print(FgBlue + "starting..." + FgBlue + selected_file_no_dir)
    # printt("starting..." + selected_file_no_dir, fg='blue')
    # time.sleep(2.5)

    # if flag_udp_comand:
    f = np.ones((480, 640, 3), dtype=np.uint8)
    f = cv2.putText(f, str(f"File sent to robot in {round(time.time() - t, 2)} sec"),
                    (f.shape[1] // 10, f.shape[0] // 2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (255, 255, 255), 2)
    f = cv2.putText(f, str(f"Waiting for the start of the robot"),
                    (f.shape[1] // 10, f.shape[0] // 2 + 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (255, 255, 255), 2)
    frame_udp = f
    frame_udp_turbo = f
    # frame = f

    if video_show2_global == 1:
        # print("restart video")
        video_show2 = 0

    started_flag = 1
    recive_flag = 1


def Stop(ev, send_stop=True):
    global root, video_show2, video_show2_global, started_flag, recive_flag, robot_adres, socket2, udp_commanda
    global timer_wait_start

    if robot_adres == "-1":
        print(FgRed + "select robot")
        printt("select robot", fg="red")
        return
    flag_start_script = time.time() + timer_wait_start

    # recive_flag = 0

    if video_show2 != 3:
        video_show2 = -1

    if send_stop:
        if flag_udp_comand:
            print("Stop UDP")
            udp_commanda.append(b"s")
            # return

        if flag_inet_work:
            recive_flag == -1
            time.sleep(0.1)

    count = 0
    while video_show2 != 3:

        if count > 20:
            # print(BgRed + "break Video Stop" + Reset)
            break
        count += 1
        # print("wait stoped video", video_show2)
        time.sleep(0.05)

    if send_stop:
        if flag_udp_comand == False:
            recive_flag = -1
            count = 0
            t = time.time()
            while recive_flag != 1:
                if time.time() - t > 10:
                    print(BgRed + "break Stop" + Reset)
                    break
                count += 1
                time.sleep(0.05)

    # started_flag = 0
    time.sleep(0.1)
    cv2.destroyAllWindows()


def LoadFile(ev):
    global selected_file, robot_adres, selected_file_no_dir

    if robot_adres == "-1":
        print(FgRed + "select robot!")
        printt("select robot!", fg='red')
        return
    #
    # my_thread_stop = threading.Thread(target=Stop, args=[(ev,)])
    # my_thread_stop.daemon = True
    # my_thread_stop.start()
    Stop(ev, False)

    # fn = tkFileDialog.Open(root, filetypes=[('*.py files', '.py')]).show()
    fn = tkFileDialog.askopenfilename(filetypes=[('*.py files', '.py'), ('*.* files', '*.*')])
    if fn == '':
        return
    # print("load2")

    selected_file = fn
    # print(selected_file)
    s = fn.split("/")
    selected_file_no_dir = s[len(s) - 1]
    # print(s[len(s) - 1])

    # print(selected_file)
    root.title(selected_file)

    Start(ev)
    # send_selected_file(True)

    # textbox.delete('1.0', 'end')
    # textbox.insert('1.0', open(fn, 'rt').read())


# def OptionMenu_SelectionEvent(event):  # I'm not sure on the arguments here, it works though
#     ## do something
#     global robot_adres, socket, recive_flag
#     print(FgBlue,event)
#
#     if event == "none" or robot_adres != "-1":
#         print("return")
#         return
#
#     if event[0] == "scan":
#         ScanRobots(event)
#         return
#     robot_adres = event[1]
#     # socket = context.socket(zmq.REP)
#     socket = context.socket(zmq.REQ)
#     socket.connect("tcp://" + robot_adres + ":%s" % port)
#
#     ip_adress = sc.gethostbyname(sc.gethostname())
#
#     # s = socket.recv_string(zmq.NOBLOCK)
#
#     print("Taking robot..", robot_adres)
#     socket.send_string("take|" + ip_adress)
#     print("Connected to robot: "+BgGreen+socket.recv_string()+Reset)
#     # recive_flag = 1
#
#     connect_keyboard(robot_adres)
#     flag_inet_work = False
#     pass
def take_ip_from_robot(timer=2, message_s_ip=""):
    global robot_adres, server_address_udp, server_address_udp, server_address_udp_turbo, flag_inet_work, server_address_udp_event, server_address_udp_command
    if flag_inet_work == False:
        return
    if message_s_ip == "":
        t = time.time()
        while len(message_s_ip) < 1:
            if time.time() - t > timer:
                break
            message_s_ip = ic.send_and_wait_answer(robot_adres_inet, "ip|" + pass_hash)
            time.sleep(0.1)

    # print(message_s_ip)
    if message_s_ip.find("|ip|") > -1:
        message_s_ip = message_s_ip.split('|')[2]
        robot_adres = message_s_ip[2:-4].split(' ')[0]
        server_address_udp = (robot_adres, 5001)
        server_address_udp_turbo = (robot_adres, 5002)
        server_address_udp_event = (robot_adres, 5003)
        server_address_udp_command = (robot_adres, 4999)
        # print(f"IP adress mashine: {server_address_udp[0]}")


def OptionMenu_SelectionEvent(event):  # I'm not sure on the arguments here, it works though
    ## do something
    global robot_adres, socket, recive_flag, flag_inet_work, robot_adres_inet, started_flag, pass_hash, server_address_udp, server_address_udp_turbo, server_address_udp_event
    global flag_udp_comand, server_address_udp_command
    # print(pass_hash)
    print(FgBlue, event)

    # if event == "none" or robot_adres != "-1":
    #     print("return")
    #     return

    if event[0] == "scan":
        # ScanRobots(event)
        return

    if event[0] == "scan_inet":
        ip_adress_s = sc.gethostbyname(sc.gethostname())
        list_combobox.clear()
        print(ip_adress_s)
        print("connect to server...")
        printt("connect to server...")
        time.sleep(0.01)
        ic.connect()
        print("take list")
        printt("take list")
        list = ic.take_list()
        # print(list)
        # print(ic.take_list())
        # list_combobox_inet = []
        # list_combobox_inet.append(["scan_inet", " "])
        time.sleep(0.01)
        for r in list:
            print(r)
            printt(str(r[1]))
            if r[2] == "robot":
                list_combobox.append(r)
        if len(list) == 0:
            print("no robots in server list")
            printt("no robots in server list")

        list_combobox.append(["scan_inet", " "])
        dropVar = tk.StringVar()
        dropVar.set(list_combobox_inet[0])

        combobox_inet = tk.OptionMenu(panelFrame, dropVar, *(list_combobox), command=OptionMenu_SelectionEvent)
        combobox_inet.place(x=260, y=10, width=150, height=40)  # Позиционируем Combobox на форме
        # print("end take")
        return

    if event[3] == "l":
        robot_adres = event[1]
        robot_adres_inet = event[0]

        # print(robot_adres)
        server_address_udp = (robot_adres, 5001)
        server_address_udp_turbo = (robot_adres, 5002)
        server_address_udp_event = (robot_adres, 5003)
        server_address_udp_command = (robot_adres, 4999)

        flag_udp_event = True
        flag_udp_show_window = True

        # print(server_address_udp)
        # socket = context.socket(zmq.REP)
        # flag_udp_comand = False

        recive_flag = 6
        t = time.time()
        while recive_flag == 6:
            if time.time() - t > 5:
                break
            time.sleep(0.01)

        recive_flag = 1
        flag_inet_work = False

    if event[3] == "i":

        robot_adres_inet = event[0]
        robot_adres = event[0]
        # print(robot_adres_inet)
        # printt(robot_adres_inet)
        flag_udp_comand = False
        flag_inet_work = True
        ic.clear()
        for i in range(5):
            message_s = ic.send_and_wait_answer(robot_adres_inet, "d")
            time.sleep(0.001)
        print("Connected to robot: " + BgGreen + event[1] + Reset)
        printt("Connected to robot: " + event[1], bg='green', fg='white')
        ic.clear()

        # print("SEND IP REQ")
        # message_s_ip = ""
        server_address_udp = ('', 5001)
        server_address_udp_turbo = ('', 5002)
        server_address_udp_event = ('', 5003)
        server_address_udp_command = ('', 4999)

        take_ip_from_robot()
        # t = time.time()
        #
        # while len(message_s_ip) < 1:
        #     if time.time() - t > 2:
        #         break
        #     message_s_ip = ic.send_and_wait_answer(robot_adres_inet, "ip|" + pass_hash)
        #     time.sleep(0.1)
        #
        #
        #
        # robot_adres = message_s_ip[2:-4].split(' ')[0]
        # server_address_udp = (robot_adres, 5001)
        # server_address_udp_turbo = (robot_adres, 5002)
        # print(server_address_udp)

        ic.clear()

        # print(str(message_s_ip)[2:-3])

        recive_flag = 1
        started_flag = 1
        pass
    connect_keyboard(robot_adres)
    pass


def mouse_move():
    global mouse_x, mouse_y
    import mouse

    try:
        import win32gui
    except:
        os.system('pip install pypiwin32')

    x1 = 0
    y1 = 0
    while 1:
        # x, y = mouse.get_position()
        try:
            flags, hcursor, z = win32gui.GetCursorInfo()
            x = z[0]
            y = z[1]
            # print(x,y)

            if x1 != x or y1 != y:
                # send_event(data)
                x1 = x
                y1 = y
                mouse_x = x
                mouse_y = y
                # print("mouse", x,y)
        except:
            pass
        time.sleep(0.05)


if MOUSE_FLAG:
    my_thread_mouse = threading.Thread(target=mouse_move)
    my_thread_mouse.daemon = True
    my_thread_mouse.start()


def joy_move():
    global joy_x, joy_y, joy_data, last_joy_activ
    x = 1
    y = 1
    joy_data_old = []

    while 1:
        pygame.event.get()
        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()
        # print("count", joystick_count)
        if joystick_count > 0:

            joystick = pygame.joystick.Joystick(0)
            joystick.init()

            # 0 газ
            # joy_x1 = joystick.get_axis(2)
            # joy_y1 = joystick.get_axis(1)

            joy_data_temp = []
            # print(joystick.get_numbuttons())

            for i in range(0, joystick.get_numaxes()):
                joy_data_temp.append(int(np.interp(joystick.get_axis(i), [-1, 1], [1000, 2000])))
            for i in range(0, joystick.get_numbuttons()):
                joy_data_temp.append(joystick.get_button(i))

            if len(joy_data_old) == 0:
                joy_data_old = joy_data_temp
            # print(joy_data_temp)

            # в течении n секунд выдаем люую активность, потом только по изменению
            if time.time() < last_joy_activ + 1:
                joy_data = joy_data_temp.copy()
                # print(joy_data)
            else:
                if joy_data_old != joy_data_temp:
                    joy_data = joy_data_temp.copy()
                    last_joy_activ = time.time()

                joy_data_old = joy_data_temp

            # joy_data = joy_data_temp.copy()
            # print(joystick.get_axis(3))

            # if x != joy_x1 or y != joy_y1:
            #     # send_event(data)
            #     x = joy_x1
            #     y = joy_y1
            #     joy_x = np.interp(joy_x1, [-1, 1], [-255, 255])
            #     joy_y = np.interp(joy_y1, [-1, 1], [-255, 255])
            #     #print((joy_x, joy_y))
            #     continue

        time.sleep(0.05)
        # return joystick.get_axis(0), joystick.get_axis(1)


if JOYSTIK_FLAG:
    my_thread_joy = threading.Thread(target=joy_move)
    my_thread_joy.daemon = True
    my_thread_joy.start()


def make_dataset():
    global FRAME, key_pressed_dataset
    count = 2000
    X = np.ndarray(shape=(count, 120, 160, 3), dtype=np.uint8)
    Y = np.ndarray(shape=(count, 1), dtype=np.float32)
    Z = np.ndarray(shape=(count, 1), dtype=np.float32)
    count_frames = 0
    while 1:
        # if type(FRAME)=="<class 'int'>":
        if type(FRAME) is int:
            # print (str(type(FRAME)))
            pass
        else:

            j_x = joy_x
            j_y = joy_y

            if key_pressed_dataset != 0:
                print(key_pressed_dataset)

                cv2.imshow("dataset_key", FRAME)
                cv2.waitKey(1)

                # frame = cv2.cvtColor(FRAME, cv2.COLOR_BGR2RGB)
                frame = FRAME.copy()
                X[count_frames] = cv2.resize(frame, (160, 120), interpolation=cv2.INTER_CUBIC)
                t = 0.5
                if key_pressed_dataset == 39:
                    t = 0
                if key_pressed_dataset == 37:
                    t = 1

                Y[count_frames] = t
                Z[count_frames] = key_pressed_dataset

                print(j_x, j_y)

                count_frames += 1
                print(count_frames)

                if count_frames >= count:
                    with open("train.pkl", "wb") as f:
                        pickle.dump([X, Y, Z], f)
                    print("save dataset")
                    return
                key_pressed_dataset = 0

            if abs(j_x) > 1 and abs(j_y) > 1:

                cv2.imshow("dataset", FRAME)
                cv2.waitKey(1)

                frame = cv2.cvtColor(FRAME, cv2.COLOR_BGR2RGB)
                X[count_frames] = cv2.resize(frame, (160, 120), interpolation=cv2.INTER_CUBIC)
                Y[count_frames] = j_y
                Z[count_frames] = j_x

                print(j_x, j_y)

                count_frames += 1
                print(count_frames)

                if count_frames >= count:
                    with open("train.pkl", "wb") as f:
                        pickle.dump([X, Y, Z], f)
                    print("save dataset")
                    return

        time.sleep(0.1)
        # return joystick.get_axis(0), joystick.get_axis(1)


#
if DATASET:
    my_thread_dataset = threading.Thread(target=make_dataset)
    my_thread_dataset.daemon = True
    my_thread_dataset.start()


def send_event():
    global socket3, started_flag, ic_key, recive_flag, key_started, key_pressed, mouse_x, mouse_y, joy_x, joy_y, joy_data, list_udp_send
    context3 = zmq.Context()
    socket3 = context3.socket(zmq.REQ)
    ic_key = InetConnection.InetConnect(sc.gethostname() + "_key", "client")
    while 1:
        if key_started == -1:
            time.sleep(0.1)
            continue

        if key_started == 0:
            if flag_inet_work:
                ic_key.connect()
                # print("start key client")
            else:
                socket3.connect("tcp://" + robot_adres + ":5559")
            key_started = 1
            break

    try:
        import win32api
    except:
        print("need install win32api: pip install pypiwin32 ")
        os.system('pip install pypiwin32')

    timer_send = time.time()
    while 1:
        if time.time() - timer_send < 0.005:
            time.sleep(0.001)
            continue
        timer_send = time.time()

        try:
            for i in range(1, 256):
                k = win32api.GetAsyncKeyState(i)
                if k:
                    key_pressed = i
        except:
            pass

        data_all = []

        if key_pressed != 0:
            # data = key_pressed
            data_all.append(key_pressed)
            key_pressed = 0
        # else:
        if mouse_x != -1 and mouse_y != -1:
            # print("send mouse", mouse_x, mouse_y)
            # data = "m," + str(mouse_x) + "," + str(mouse_y)
            data_all.append("m," + str(mouse_x) + "," + str(mouse_y))
            mouse_x = -1
            mouse_y = -1

        # print(joy_data)
        if len(joy_data) > 0:
            # if joy_x != j_x or joy_y != j_y:
            ds = "j,"
            for i in joy_data:
                ds += str(i) + ","
            data_all.append(ds[:-1])
            # print("joy", data)
            joy_data = []
            # data = "j," + str(round(joy_x, 2)) + "," + str(round(joy_y, 2))
            # #print(joy_x, joy_y)
            # j_x = joy_x
            # j_y = joy_y

        # if data!="":
        #     print(data, recive_flag)
        # print("---", time.time()-ttt)
        # if data != "" and recive_flag == 1:
        # if data != "":
        if flag_udp_event == False:
            for data in data_all:
                # print("Send DATA", data)
                if flag_inet_work == True:
                    # print("send",str(data)+"|"+pass_hash )
                    ic_key.send_key(robot_adres_inet, str(data) + "|" + pass_hash)

                else:

                    if recive_flag == 1:
                        # socket3.send_string(str(data))
                        try:
                            socket3.send_string(str(data), zmq.NOBLOCK)  # zmq.NOBLOCK
                        except:
                            pass

                        message = ""
                        count = 0
                        while 1:
                            count += 1
                            try:
                                # print("s1")
                                # socket2.send_string("p", zmq.NOBLOCK)
                                message = socket3.recv_string(zmq.NOBLOCK)
                                # print("....ok")
                            except zmq.ZMQError as e:
                                pass
                            # print(message)
                            if message == "|":
                                break
                            time.sleep(0.01)
                            if count > 100:
                                # print(BgRed + "reconnect key" + Reset)
                                # print("reconnect key" + Reset)
                                socket3.close()
                                # context3 = zmq.Context()
                                socket3 = context3.socket(zmq.REQ)
                                socket3.connect("tcp://" + robot_adres + ":5559")
                                break
        else:
            # print("send udp ",data)
            list_udp_send.extend(data_all)
        # print("---", time.time()-ttt)
        # time.sleep(0.01)


my_thread_key = threading.Thread(target=send_event)
my_thread_key.daemon = True
my_thread_key.start()


def connect_keyboard(robot_adres):
    global flag_inet_work, key_started
    key_started = 0
    pass


def keydown(e):
    global started_flag, recive_flag, key_pressed, fps_show, key_pressed_dataset, FRAME, resize_windows, flag_udp_show_window, flag_udp_turbo_show_window, flag_udp_event, server_address_udp_command
    global flag_udp_comand, socket, robot_adres, port, recive_flag
    key_pressed = e.keycode
    key_pressed_dataset = e.keycode
    if key_pressed == 113:
        # print("F2 make screen")
        # cv2.imwrite("screen.jpg", FRAME)
        if fps_show == 1:
            fps_show = 0
        else:
            fps_show = 1
    if key_pressed == 114:
        if resize_windows:
            resize_windows = False
            print("F3 resize windows OFF")
        else:
            resize_windows = True
            print("F3 resize windows ON")
        # cv2.imwrite("screen.jpg", FRAME)

    if key_pressed == 112:
        # print("lock robot")
        recive_flag = 2
    if key_pressed == 121:
        # print("drop robot")
        recive_flag = 4

    if key_pressed == 115:
        popup_bonus()
    if key_pressed == 116:

        flag_udp_turbo_show_window = False
        flag_udp_show_window = not flag_udp_show_window

        if flag_udp_show_window:
            print(FgYellow + "Video UDP ON")
            if server_address_udp[0] == "":
                take_ip_from_robot(10)
        else:
            print(FgYellow + "Video UDP OFF")
    if key_pressed == 117:

        flag_udp_show_window = False
        flag_udp_turbo_show_window = not flag_udp_turbo_show_window

        if flag_udp_turbo_show_window:
            print(FgYellow + "Video UDP TURBO ON")
            if server_address_udp_event[0] == "":
                take_ip_from_robot(10)

        else:
            print(FgYellow + "Video UDP TURBO OFF")

    if key_pressed == 119:
        flag_udp_event = not flag_udp_event
        # print(FgYellow + "F8 ")
        if flag_udp_event:
            print(FgYellow + "Send event UDP ON")
            if server_address_udp_event[0] == "":
                take_ip_from_robot(10)

        else:
            print(FgYellow + "Send event UDP OFF")
    if key_pressed == 120:
        flag_udp_comand = not flag_udp_comand
        # print(FgYellow + "F8 ")
        if flag_udp_comand:
            print(FgYellow + "Send command UDP ON")
            if server_address_udp_command[0] == "":
                take_ip_from_robot(10)

        else:
            print(FgYellow + "Send comamand UDP OFF")
            try:
                socket.close()
            except:
                pass
            context = zmq.Context()
            socket = context.socket(zmq.REQ)

            if robot_adres != '-1':
                socket.connect("tcp://" + robot_adres + ":%s" % port)
                socket.send_string("take|" + robot_adres)
                otvet = socket.recv_string()
                print("Connected to robot: " + BgGreen + otvet + Reset)
                printt("Connected to robot: " + otvet, fg='white', bg='green')

    # print(key_pressed)

root = tk.Tk()
root.title('RoboStarter')
root.geometry('420x300+900+10')  # ширина=500, высота=400, x=300, y=200
root.resizable(True, True)  # размер окна может быть изменён только по горизонтали

root.bind("<KeyPress>", keydown)

panelFrame = tk.Frame(root, height=55, bg='gray')
textFrame = tk.Frame(root, height=200, width=500)

panelFrame.pack(side='top', fill='x')
textFrame.pack(side='bottom', fill='both', expand=1)

# tex.pack(side=tk.RIGHT)
textbox = tk.Text(textFrame, font='Arial 10', wrap='word')

scrollbar = tk.Scrollbar(textFrame)

scrollbar['command'] = textbox.yview
textbox['yscrollcommand'] = scrollbar.set

textbox.pack(side='left', fill='both', expand=1)
scrollbar.pack(side='right', fill='y')

loadBtn = tk.Button(panelFrame, text='Load\nStart')
# saveBtn = Button(panelFrame, text='Scan')
startBtn = tk.Button(panelFrame, text='Start')
stopBtn = tk.Button(panelFrame, text='Stop')
videoBtn = tk.Button(panelFrame, text='Raw')
videoBtn2 = tk.Button(panelFrame, text='Video')
# testBtn = Button(panelFrame, text='test')


loadBtn.bind("<Button-1>", LoadFile)
# saveBtn.bind("<Button-1>", ScanRobots)
startBtn.bind("<Button-1>", Start)
stopBtn.bind("<Button-1>", Stop)
videoBtn.bind("<Button-1>", Raw)
videoBtn2.bind("<Button-1>", Video2)
# testBtn.bind("<Button-1>", test)

loadBtn.place(x=10, y=10, width=40, height=40)
# saveBtn.place(x=10, y=10, width=40, height=40)
startBtn.place(x=60, y=10, width=40, height=40)
stopBtn.place(x=110, y=10, width=40, height=40)
videoBtn.place(x=160, y=10, width=40, height=40)
videoBtn2.place(x=210, y=10, width=40, height=40)


def ppp():
    global textbox, started_flag, root, list_to_print
    while 1:
        time.sleep(0.1)
        text = ""
        fg = 'black'
        bg = 'white'
        flag = False
        for z in list_to_print:
            text1, fg, bg = z
            text += text1 + "\n"
            list_to_print.remove(z)
            flag = True

        if flag:

            textbox.configure(state='normal')
            data = textbox.get('1.0', 'end-1c')

            data = data.split('\n')

            text_list = text.split("\n")

            # print()
            count = len(data)

            if count > 100:
                textbox.delete('1.0', '50.0')
                data = textbox.get('1.0', 'end-1c')

                data = data.split('\n')

                text_list = text.split("\n")

            # print()
            count = len(data)

            textbox.insert('end', str(text))
            textbox.see('end')  # Scroll if necessary
            # print(str(count) + ".0", str(count) + ".20")
            textbox.tag_add(str(count), str(count) + ".0", str(count) + str(len(text_list)) + ".200")
            # textbox.tag_add("start", "1.8", "1.13")
            # textbox.tag_config("here", background="yellow", foreground="blue")
            textbox.tag_config(str(count), foreground=fg, background=bg)
            #
            if started_flag:
                textbox.configure(state='disabled')


my_thread_work_tkinter = threading.Thread(target=ppp)
my_thread_work_tkinter.daemon = True
my_thread_work_tkinter.start()

list_to_print = []
def printt(text, fg='black', bg='white'):
    global list_to_print
    list_to_print.append([text, fg, bg])


# def kill_cv():
#     global started_flag
#     if started_flag==False:
#         cv2.destroyAllWindows()
#     time.sleep(1)
#
#
# my_thread = threading.Thread(target=kill_cv)
# my_thread.daemon = True
# my_thread.start()

print("Start robot API")

printt("Start robot API", fg='green')


def popup_bonus():
    global pass_hash
    print(pass_hash)
    win = tk.Toplevel()
    win.wm_title("Window")
    password = ''

    pwdbox = tk.Entry(win, show='*')

    # def onpwdentry(evt):
    #     password = pwdbox.get()
    #     print(password)
    #
    #     win.destroy()
    #     return password

    def onokclick(evt):
        global pass_hash
        password = pwdbox.get()
        # print(password)
        import hashlib
        pass_hash = hashlib.sha224(password.encode('utf-8')).hexdigest()[:3]
        # print(pass_hash)
        print("change password")
        file = open('password', 'w+')
        file.write(pass_hash)
        file.close()
        win.destroy()
        return pass_hash

    tk.Label(win, text='Password').pack(side='top')

    pwdbox.pack(side='top')
    pwdbox.bind('<Return>', onokclick)
    # tk.Button(win, command=onokclick, text='OK').pack(side='top')


# popup_bonus()

def ask_quit():
    global lock_pass, recive_flag
    root.destroy()
    cv2.destroyAllWindows()
    if lock_pass is not None:
        recive_flag = 4
        t = time.time()
        while recive_flag != 1:
            if time.time() - t < 5:
                break
            time.sleep(0.01)
    time.sleep(3)



# testBtn.place(x=10, y=60, width=40, height=40)
# root.after(10, robot_recive_work)
#
list_combobox = []

list_combobox_inet = []
dropVar = tk.StringVar()
dropVar.set("Connect to robot")
dropVar_inet = tk.StringVar()
dropVar_inet.set("Connect to robot")

list_combobox.append(["8", "192.168.10.1", "robot", "l"])
list_combobox.append(["alex", "to2", "robot", "l"])
list_combobox.append(["slava", "korshun4568", "robot", "l"])
list_combobox.append(["local", "raspberrypi", "robot", "l"])
list_combobox.append(["rover", "192.168.1.6", "robot", "l"])


list_combobox.append(["scan_inet", " "])
list_combobox_inet.append(["scan_inet", " "])

combobox = tk.OptionMenu(panelFrame, dropVar, *(list_combobox), command=OptionMenu_SelectionEvent)
combobox.place(x=260, y=10, width=150, height=40)  # Позиционируем Combobox на форме

# combobox_inet = OptionMenu(panelFrame, dropVar_inet, *(list_combobox_inet), command=OptionMenu_SelectionEvent_inet)
# combobox_inet.place(x=260, y=60, width=150, height=40)  # Позиционируем Combobox на форме



root.protocol("WM_DELETE_WINDOW", ask_quit)
root.mainloop()
