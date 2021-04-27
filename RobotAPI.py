__author__ = 'Yuri Glamazdin <yglamazdin@gmail.com>'
__version__ = '1.6'

# install turbo
# sudo apt-get install libturbojpeg-dev
import time
import zmq
import cv2
import threading
import atexit
import socket
import struct


# for TURBO
def cv2_decode_image_buffer(img_buffer):
    img_array = np.frombuffer(img_buffer, dtype=np.dtype('uint8'))
    # Decode a colored image
    return cv2.imdecode(img_array, flags=cv2.IMREAD_UNCHANGED)


def cv2_encode_image(cv2_img, jpeg_quality):
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
    result, buf = cv2.imencode('.jpg', cv2_img, encode_params)
    return buf.tobytes()


def turbo_decode_image_buffer(img_buffer, jpeg):
    return jpeg.decode(img_buffer)


def turbo_encode_image(cv2_img, jpeg, jpeg_quality):
    return jpeg.encode(cv2_img, quality=jpeg_quality)


from ctypes import *
from ctypes.util import find_library
import platform
import numpy as np
import math
import warnings
import os

# default libTurboJPEG library path
DEFAULT_LIB_PATHS = {
    'Darwin': ['/usr/local/opt/jpeg-turbo/lib/libturbojpeg.dylib'],
    'Linux': [
        '/usr/lib/x86_64-linux-gnu/libturbojpeg.so.0',
        '/opt/libjpeg-turbo/lib64/libturbojpeg.so'
    ],
    'Windows': ['C:/libjpeg-turbo-gcc64/bin/libturbojpeg.dll']
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


class Crc8DvbS2(object):
    """CRC-8/DVB-S2"""

    def __init__(self, initvalue=None):
        self._value = 0x00

    def process(self, data):
        crc = self._value
        for byte in data:
            crc = crc ^ byte
            for i in range(0, 8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0xD5
                else:
                    crc = (crc << 1)
            crc &= 0xFF
        self._value = crc
        return self

    def final(self):
        crc = self._value
        crc ^= 0x00
        return crc

    @classmethod
    def calc(cls, data, initvalue=None, **kwargs):
        inst = cls(initvalue, **kwargs)
        inst.process(data)
        return inst.final()


class RobotAPI:
    port = None
    server_flag = False
    last_key = -1
    last_frame = np.ones((480, 640, 3), dtype=np.uint8)
    quality = 50
    manual_regim = 0
    manual_video = 1
    manual_speed = 150
    manual_angle = 0
    frame = np.ones((480, 640, 3), dtype=np.uint8)
    __joy_data = []
    __mouse_data = []
    small_frame = 0
    motor_left = 0
    motor_rigth = 0
    flag_serial = False
    flag_pyboard = False
    __time_old_frame = time.time()
    time_frame = time.time() + 1000
    # time_frame =0
    __last_odometr = -1
    __last_write = 0
    __old_pos = []
    __flag_sending = False
    __cap = []
    __num_active_cam = 0
    __flag_bad_frame = False
    stop_frames = False
    __list_wait = []
    quality = 20

    def __init__(self, flag_video=True, flag_keyboard=True, flag_serial=True, flag_pyboard=False, udp_stream=True,
                 udp_turbo_stream=True, udp_event=True):
        # print("\x1b[42m" + "Start script" + "\x1b[0m")
        self.flag_serial = flag_serial
        self.flag_pyboard = flag_pyboard

        atexit.register(self.cleanup)
        atexit.register(self.cleanup)
        # print("open robot port")
        if flag_serial:
            import serial
            if socket.gethostname().find("ras") == 0:
                self.comp_name = "raspberry"
                if flag_pyboard:
                    # self.port = serial.Serial("/dev/ttyS0", baudrate=1000000)
                    # self.port = serial.Serial("/dev/ttyS0", baudrate=115200)
                    self.port = serial.Serial("/dev/ttyS0", baudrate=115200, stopbits=serial.STOPBITS_ONE)
                    # self.port = serial.Serial("/dev/ttyS0", baudrate=230400, stopbits=serial.STOPBITS_ONE)


                else:
                    self.port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=0.001)
                    # self.port = serial.Serial("/dev/ttyS0", baudrate=115200)

            else:
                self.comp_name = "orange"
                # self.port = serial.Serial("/dev/ttyS3", baudrate=115200, timeout=0.01)
                self.port = serial.Serial("COM16", baudrate=115200)
                time.sleep(1)

        # vsc.VideoClient.inst().subscribe("ipc")cap
        # vsc.VideoClient.inst().subscribe("tcp://127.0.0.1")
        # vsc.VideoClient.inst().subscribe("udp://127.0.0.1")

        # while True:
        #     frame = vsc.VideoClient.inst().get_frame()
        #     if frame.size != 4:
        #         break

        # r, self.frame = self.__cap[0].read()
        # self.frame = np.ndarray(shape=(120, 160, 3), dtype=np.uint8)
        # self.time_frame = time.time()
        self.flag_video = flag_video
        if self.flag_video == True:
            self.init_cam(0)
            self.set_camera(30, 640, 480)
            self.context = zmq.Context(1)
            self.socket = self.context.socket(zmq.REP)
            self.socket.setsockopt(zmq.SNDTIMEO, 3000)
            self.socket.setsockopt(zmq.RCVTIMEO, 3000)

            self.socket.bind("tcp://*:5555")
            cv2.putText(self.last_frame, str("Starting camera..."),
                        (self.last_frame.shape[1] // 8, self.last_frame.shape[0] // 2), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        2, (255, 255, 255), 2)
            cv2.putText(self.frame, str("Start..."), (self.last_frame.shape[1] // 3, self.last_frame.shape[0] // 2),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 2)
            # print("start video server")
            self.server_flag = True
            self.my_thread_video = threading.Thread(target=self.__send_frame)
            self.my_thread_video.daemon = True

            self.my_thread_video.start()

            self.manual_video = 1

        if flag_keyboard:
            self.context2 = zmq.Context(1)
            self.socket2 = self.context2.socket(zmq.REP)
            # self.socket2.setsockopt(zmq.SNDTIMEO, 3000)
            # self.socket2.setsockopt(zmq.RCVTIMEO, 3000)

            self.socket2.bind("tcp://*:5559")
            # print("start video server")
            self.server_keyboard = True
            self.my_thread = threading.Thread(target=self.__recive_key)
            self.my_thread.daemon = True
            self.my_thread.start()

        # серву выставляем в нуль

        if self.flag_serial:
            self.serv(0)
            # очищаем буфер кнопки( если была нажата, то сбрасываем)
            self.button()
            # выключаем все светодиоды
            self.color_off()

        if udp_stream:
            self.my_thread_udp = threading.Thread(target=self.__work_udp)
            self.my_thread_udp.daemon = True
            self.my_thread_udp.start()
        if udp_turbo_stream:
            self.my_thread_turbo_udp = threading.Thread(target=self.__work_turbo_udp)
            self.my_thread_turbo_udp.daemon = True
            self.my_thread_turbo_udp.start()

            # self.my_thread_turbo_udp1 = threading.Thread(target=self.__work_turbo_udp1)
            # self.my_thread_turbo_udp1.daemon = True
            # self.my_thread_turbo_udp1.start()

        if udp_event:
            self.my_thread_udp_event = threading.Thread(target=self.__work_udp_event)
            self.my_thread_udp_event.daemon = True
            self.my_thread_udp_event.start()
        self.my_thread_f = threading.Thread(target=self.__work_f)
        self.my_thread_f.daemon = True
        self.my_thread_f.start()
        print("|start_api")

    def init_cam(self, num=0):
        while len(self.__cap) <= num:
            self.__cap.append(None)
        if self.__cap[num] is None:
            self.__cap[num] = cv2.VideoCapture(num)

        self.__num_active_cam = num
        res = self.__cap[num].isOpened()

        if res == False or self.__flag_bad_frame == True:
            # self.wait(100)
            # print("release cam")
            self.__cap[num].release()
            self.__cap[num] = cv2.VideoCapture(num)
            # self.__cap[num] = None
        res = self.__cap[num].isOpened()
        if res:
            self.stop_frames = False
        return res

    def end_work(self):
        # self.cap.release()
        if self.flag_video:
            for i in self.__cap:
                if i is not None:
                    i.release()
        if self.flag_serial:
            self.color_off()
            self.serv(0)
        self.stop_frames = True
        self.wait(300)
        self.frame = np.array([[10, 10], [10, 10]], dtype=np.uint8)
        self.wait(1000)
        print("|STOPED API")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_work()

    def cleanup(self):
        self.end_work()

        # self.cap.release()

    def set_camera(self, fps=60, width=640, height=480, num=0):
        answer = self.init_cam(num)
        self.stop_frames = True
        self.wait(800)

        # if self.__cap[num] is None:

        # print("set camers", answer,self.__cap[num], fps, width, height, num)

        if answer and self.__cap[num] is not None:
            self.__cap[num].set(cv2.CAP_PROP_FPS, fps)
            self.__cap[num].set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.__cap[num].set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.wait(600)
        self.stop_frames = False
        return answer

    def set_camera_high_res(self):
        self.set_camera(30, 1024, 720)

    def set_camera_low_res(self):
        self.set_camera(60, 320, 240)

    def joy(self):
        j = self.__joy_data.copy()
        self.__joy_data = []
        return j

    def mouse(self):
        m = self.__mouse_data.copy()
        self.__mouse_data = []
        return m

    def __work_udp(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(0)
        # Bind the socket to the port
        host = ''
        port = 5001
        server_address = (host, port)

        # print('starting UDP stream up on %s port %s\n' % server_address)

        sock.bind(server_address)
        # clients ={}

        while 1:
            try:
                # print("start udp frame", time.time())
                data=b''
                # try:
                data, address = sock.recvfrom(1)
                # except:
                #     pass

                data = data.decode('utf-8')
                # print(address)
                if data == "g":

                    # t = time.time()

                    encode_param = [int(cv2.IMWRITE_JPEG_LUMA_QUALITY), self.quality]
                    result, buffer = cv2.imencode('.jpg', self.last_frame, encode_param)
                    # print(time.time() - t)

                    if len(buffer) > 65507:
                        print(
                            "The message is too large to be sent within a single UDP datagram. We do not handle splitting the message in multiple datagrams")
                        sock.sendto("FAIL".encode('utf-8'), address)
                        continue
                    sock.sendto(buffer, address)
            except Exception as e:
                # print("udp video error",e)
                time.sleep(0.01)
                pass

        pass

    # def __work_turbo_udp1(self):
    #     jpeg = TurboJPEG()
    #     jpeg_encode_func = lambda img, jpeg_quality=self.quality, jpeg=jpeg: turbo_encode_image(img, jpeg, jpeg_quality)
    #     timer = time.time()
    #     while 1:
    #         if timer <= self.time_frame:
    #             timer = time.time()
    #             self.buffer = jpeg_encode_func(self.last_frame)
    #             print(len(self.buffer))
    #     # pass

    def __work_turbo_udp(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Bind the socket to the port
            host = ''
            port = 5002
            server_address = (host, port)

            # print('starting UDP TURBO stream up on %s port %s\n' % server_address)

            sock.bind(server_address)

            # clients ={}
            try:
                jpeg = TurboJPEG()
            except:
                pass
            jpeg_encode_func = lambda img, jpeg_quality=self.quality, jpeg=jpeg: turbo_encode_image(img, jpeg,
                                                                                                    jpeg_quality)
            while 1:
                try:
                    # print("start TURBO frame", time.time())
                    data, address = sock.recvfrom(1)
                    data = data.decode('utf-8')

                    if data == "g":

                        buffer = jpeg_encode_func(self.last_frame)

                        if len(buffer) > 65507:
                            print(
                                "The message is too large to be sent within a single UDP TURBO datagram. We do not handle splitting the message in multiple datagrams")
                            sock.sendto("FAIL".encode('utf-8'), address)
                            continue
                        sock.sendto(buffer, address)
                except:
                    pass
        except:
            pass

    def __work_udp_event(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # sock.setblocking(0)
        host = ''
        port = 5003
        server_address = (host, port)
        sock.bind(server_address)

        while 1:
            # print("red udp")
            data=b''
            # try:
            data, address = sock.recvfrom(65507)
            # except:
            #     pass

            message = data.decode('utf-8')
            if len(message) > 0:
                #     print("take message", message)

                if message.find("m") > -1:
                    self.__mouse_data = message.split(",")[1:]
                    # print("take mouse", self.__mouse_data)

                elif message.find("j") > -1:
                    # message = message.split(",")
                    self.__joy_data = message.split(",")[1:]
                    # print("recive joy", self.joy_data)
                else:
                    self.last_key = int(message.lstrip())

        # pass

    def __recive_key(self):
        while True:
            try:
                message = ""
                try:
                    message = self.socket2.recv_string()
                except:
                    pass
                if len(message) > 0:
                    #     print("take message", message)

                    if message.find("m") > -1:
                        self.__mouse_data = message.split(",")[1:]
                        # print("take mouse", self.__mouse_data)

                    elif message.find("j") > -1:
                        # message = message.split(",")
                        self.__joy_data = message.split(",")[1:]
                        # print("recive joy", self.joy_data)
                    else:
                        self.last_key = int(message.lstrip())

                    try:
                        self.socket2.send_string("|")
                    except:
                        pass
                else:
                    time.sleep(0.001)
            except:
                time.sleep(0.001)

        print("RobotAPI key server down!")

    def __work_f(self):
        self.stop_frames = False
        while True:

            if self.stop_frames == False and self.flag_video:
                if len(self.__cap) > 0:
                    if self.__cap[self.__num_active_cam] is not None:
                        ret, frame = self.__cap[self.__num_active_cam].read()

                        if ret is not None:
                            self.frame = frame
                            self.time_frame = time.time()
                            self.__flag_bad_frame = False
                            # time.sleep(0.05)
                        else:
                            self.__flag_bad_frame = True
                            self.stop_frames = True
                            self.init_cam(self.__num_active_cam)
                    # if time.time() - self.time_frame>5:
                    #         self.__cap[self.__num_active_cam] = cv2.VideoCapture(self.__num_active_cam)
                    else:
                        time.sleep(0.001)
                else:
                    time.sleep(0.001)

            else:
                time.sleep(0.001)

    def get_key(self):
        l = self.last_key
        self.last_key = -1
        return l

    def num_activ_camera(self):
        return self.__num_active_cam

    def get_frame(self, wait_new_frame=False):
        if wait_new_frame:
            timer_max = time.time()
            while self.time_frame <= self.__time_old_frame:
                if time.time() - timer_max > 0.1:
                    break
                time.sleep(0.001)
            self.__time_old_frame = self.time_frame
        return self.frame

    def __send_frame(self):
        time1 = time.time()
        time2 = time.time()
        md = 0
        frame = 0

        while True:
            if self.last_frame is not None:
                if self.server_flag == True:  # and self.last_frame.shape[0] > 2:
                    message = ""
                    try:
                        message = self.socket.recv_string()
                    except:
                        pass

                    if message != "":
                        try:

                            if time1 < self.time_frame:
                                # print("make encode")
                                # encode_param = [int(cv2.IMWRITE_JPEG_LUMA_QUALITY), self.quality]
                                self.encode_param = [int(cv2.IMWRITE_JPEG_LUMA_QUALITY), self.quality]
                                result, frame = cv2.imencode('.jpg', self.last_frame, self.encode_param)
                                time1 = time.time()

                                md = dict(
                                    # arrayname="jpg",
                                    dtype=str(frame.dtype),
                                    shape=frame.shape,
                                )
                            self.socket.send_json(md, zmq.SNDMORE)
                            self.socket.send(frame, 0)


                        except:
                            pass
                    else:
                        time.sleep(0.001)
                else:
                    time.sleep(0.001)
            else:
                time.sleep(0.001)
        # while True:
        #     if self.last_frame is not None:
        #         if self.server_flag == True:# and self.last_frame.shape[0] > 2:
        #             if time2 <= self.time_frame:
        #                 # print("make encode")
        #                 # encode_param = [int(cv2.IMWRITE_JPEG_LUMA_QUALITY), self.quality]
        #                 self.encode_param = [int(cv2.IMWRITE_JPEG_LUMA_QUALITY), self.quality]
        #                 result, frame = cv2.imencode('.jpg', self.last_frame, self.encode_param)
        #                 time2 = time.time()
        #
        #                 md = dict(
        #                     # arrayname="jpg",
        #                     dtype=str(frame.dtype),
        #                     shape=frame.shape,
        #                 )
        #
        #             if time1 <= self.time_frame:
        #                 message = ""
        #                 time1 = time.time()
        #                 try:
        #                     message = self.socket.recv_string()
        #                 except:
        #                     pass
        #
        #                 if message != "":
        #                     try:
        #                         self.socket.send_json(md, zmq.SNDMORE)
        #                         self.socket.send(frame, 0)
        #                     except:
        #                         pass
        #                 else:
        #                     time.sleep(0.001)
        #         else:
        #             time.sleep(0.001)
        #     else:
        #         time.sleep(0.001)

    def set_frame(self, frame, quality=30):
        self.quality = quality
        self.last_frame = frame

    def wait(self, t):
        # print(t/1000)
        time.sleep(t / 1000)

    def __wait_my_query(self):
        id = time.time()
        self.__list_wait.append(id)
        while 1:
            if self.__list_wait[0] == id:
                return True
            time.sleep(0.001)

    def __exit_query(self):
        self.__list_wait.pop(0)

    def __send(self, message, wait_time=0.1, byte_flag=False, wait_answer=True):
        if self.flag_serial:
            # print("send",message)
            # timer_wait_send = time.time()
            # while self.__flag_sending == True:
            #     if time.time() - timer_wait_send > 0.5:
            #         break
            self.__wait_my_query()
            self.__flag_sending = True
            answer = ""

            # time.sleep(0.0001)
            # if wait_answer == True:
            #     self.port.flushInput()
            #     self.port.read(self.port.in_waiting)

            if byte_flag:
                self.port.write(message)
            else:
                self.port.write(message.encode("utf-8"))

            # while self.port.out_waiting>0:
            #          # print("self.port.out_waiting",self.port.out_waiting)
            #      pass

            if wait_answer == False:
                # self.wait(1)
                self.__flag_sending = False
                self.__exit_query()
                return
            # time.sleep(0.0001)
            # t = time.time()
            # while self.port.in_waiting == False:
            #     # if time.time()-t>1:
            #     #     print("RobotAPI: Error in_waiting (try change flag pyboard)")
            #     #     # t = time.time()
            #     #     break
            #     pass
            # print("read",self.port.in_waiting )
            # s = self.port.read(self.port.in_waiting)
            # count = 0
            # ttt = time.time()
            # beg = 0
            t = time.time()
            count_wait = 0
            while 1:
                if time.time() - t > wait_time:
                    break
                    # if len(answer)==0 or count_wait>0:
                    #     break
                    # count_wait+=1

                # if self.port.in_waiting == False:
                #      continue
                s = self.port.read(self.port.in_waiting)
                try:
                    answer += str(s, "utf-8")
                    # print(str(s, "utf-8"))
                except:
                    pass
                # if len(answer)>0:

                count_b = 0
                for b in answer:
                    if b == '|':
                        if answer[0] == message[0]:
                            answer = answer[:count_b]
                            self.__flag_sending = False
                            self.__exit_query()
                            return answer
                        # print("bad func", message[0], answer)
                        answer = ""
                        break
                    count_b += 1
            # print("bad packet", answer)
            self.__exit_query()
            self.__flag_sending = False
            return None

    def rgb(self, r, g, b, num=-1):
        if self.flag_pyboard:
            return self.__send("C," + str(r) + "," + str(g) + "," + str(b) + "," + str(num) + "|", wait_answer=False)
        else:
            # return self.__send("RGB," + str(r) + "," + str(g) + "," + str(b) + "|")
            return self.__send("C," + str(r) + "," + str(g) + "," + str(b) + "|")

    def move(self, m1, m2, timer=10, wait=True):

        # if timer < 50:
        #     wait = True
        m1 = self.constrain(m1, -255, 255)
        m2 = self.constrain(m2, -255, 255)

        self.motor_left = m1
        self.motor_rigth = m2
        # f'http://{domain}/{lang}/{path}'

        if self.flag_pyboard:
            m = self.__send(''.join(["M,", str(int(m1)), ",", str(int(m2)), ",", str(timer), "|"]), wait_answer=False)
        else:
            # m = self.__send(''.join(["MOVE,", str(int(m1)), ",", str(int(m2)), ",", str(timer), "|"]))
            # print(''.join(["M,", str(int(m1)), ",", str(int(m2)), ",", str(timer), "|"]))
            m = self.__send(''.join(["M,", str(int(m1)), ",", str(int(m2)), ",", str(timer), "|"]))

        if wait:
            self.wait(timer)

        return m

    def move_fix_speed(self, m1, timer=10, p=1, i=0.001, d=0.1, wait=False):

        # дл роборэйсера
        # if timer < 50:
        #     wait = True
        m1 = self.constrain(m1, -255, 255)
        # m2 = self.constrain(m2, -255, 255)

        self.motor_left = m1
        # self.motor_rigth = m2
        # f'http://{domain}/{lang}/{path}'

        m = self.__send(
            ''.join(["F,", str(int(m1)), ",", str(0), ",", str(timer), ",", str(p), ",", str(i), ",", str(d), "|"]),
            wait_answer=False)
        # m = self.__send(''.join(["M,", str(int(m1)), ",", str(int(m2)), ",", str(timer), "|"]))
        # m = self.__send("MOVE," + str(int(m1)) + "," + str(int(m2)) + "," + str(timer) + "|")

        if wait:
            self.wait(timer)

        return m

    def _fromInt16(self, value):
        return struct.unpack("<BB", struct.pack("@h", value))

    def _fromInt32(self, value):
        return struct.unpack("<BBBB", struct.pack("@i", value))

    def fly(self, pitch=0, roll=0, throttle=0, yaw=0, aux1=0, aux2=0, aux3=0):

        # pitch = self.constrain(pitch, 1000, 2000)
        # roll = self.constrain(roll, 1000, 2000)
        # throttle = self.constrain(throttle, 1000, 2000)
        # yaw = self.constrain(yaw, 1000, 2000)
        packet = bytearray()
        # packet.append(ord('f'))
        r = self._fromInt16(int(pitch))
        packet.append(r[0])
        packet.append(r[1])
        r = self._fromInt16(int(roll))
        packet.append(r[0])
        packet.append(r[1])
        r = self._fromInt16(int(throttle))
        packet.append(r[0])
        packet.append(r[1])
        r = self._fromInt16(int(yaw))
        packet.append(r[0])
        packet.append(r[1])
        r = self._fromInt16(int(aux1))
        packet.append(r[0])
        packet.append(r[1])
        r = self._fromInt16(int(aux2))
        packet.append(r[0])
        packet.append(r[1])
        r = self._fromInt16(int(aux3))
        packet.append(r[0])
        packet.append(r[1])

        # c = crc8(packet)
        # h=  c.digest()
        h = Crc8DvbS2.calc(packet)
        # print(packet)
        # print(h, len(h))
        # packet.append(ord(h))
        packet.append(h)
        mess = "f"
        for b in packet:
            mess += str(ord(chr(b))) + ","
        mess += "|"
        # packet.append(ord('|'))
        # print(mess)

        m = self.__send(mess, wait_answer=False)
        #
        # m = self.__send(
        #     ''.join(["f,", str(pitch), ",", str(roll), ",", str(throttle), ",", str(yaw), "|"]))
        return m

    def get_drone_position(self):
        mess = "x|"
        s = self.__send(mess, wait_answer=True, wait_time=0.1)

        # x_robot, y_robot, z_robot, yaw_robot, rangefinder_robot=0,0,0,0,0

        d = []
        try:

            s = str(s).split(",")
            if s[0] != 'x':
                return d
            crc = s[-1]
            s = s[1:-1]
            packet = bytearray()
            for c in s:
                r = self._fromInt32(int(c))
                packet.append(r[0])
                packet.append(r[1])
                packet.append(r[2])
                packet.append(r[3])
                d.append(int(c))
            if len(packet) > 0:
                h = Crc8DvbS2.calc(packet)
                if h == int(crc):
                    self.__old_pos = d
        except Exception as e:
            pass
        return self.__old_pos

    def set_drone_position(self, x, y, z, heading=0, position_move_mode=2, heading_move_mode=2):

        # 1.Ничего
        # 2.Абсолютное значение(всм / градусах от точки старта)
        # 3.Относительно текущего положения коптера
        # 4.Относительно предыдущей позиции

        packet = bytearray()
        ch = []
        ch.append(int(x))
        ch.append(int(y))
        ch.append(int(z))
        ch.append(int(heading))
        ch.append(int(position_move_mode))
        ch.append(int(heading_move_mode))

        for c in ch:
            r = self._fromInt32(int(c))
            packet.append(r[0])
            packet.append(r[1])
            packet.append(r[2])
            packet.append(r[3])
        if len(packet) > 0:
            h = Crc8DvbS2.calc(packet)
            mess = 'X,' + str(ch[0]) + "," + str(ch[1]) + "," + str(ch[2]) + "," + str(
                ch[3]) + "," + str(ch[4]) + ',' + str(ch[5]) + ',' + str(h) + '|'
            # print("set", mess)
            return self.__send(mess, wait_answer=False, wait_time=0.1)
        pass

    def autolevel_inav(self):

        mess = "l,1,2,3,4,5,6,7,8,9,10|"
        s = self.__send(mess, wait_answer=False, wait_time=0.1)
        res = 0
        try:
            s = str(s).split(",")
            res = float(s[1])
        except:
            pass
        return res

    def get_attitude(self):
        mess = "a|"
        # packet.append(ord('|'))
        # print(mess)

        s = self.__send(mess, wait_time=0.1)
        roll, pitch, yaw = None, None, None
        # print("robot api get_attitude", s)
        try:
            s = str(s).split(",")
            if s[0] == 'a':
                roll = float(s[1]) / 10.
                pitch = float(s[2]) / 10.
                yaw = float(s[3])
        except:
            pass
        return [roll, pitch, yaw]

    def accel(self):
        if self.flag_pyboard:
            m = self.__send("A|")
        else:
            m = self.__send("ACCEL|")
        x = 0
        y = 0
        z = 0
        try:
            s = str(m).split(",")
            x = float(s[1])
            y = float(s[2])
            z = float(s[3])
        except:
            pass
        return [x, y, z]

    def tone(self, fr, timer, wait=False):
        if self.flag_pyboard:
            mes = self.__send("T," + str(fr) + "," + str(timer) + "|")
        else:
            mes = self.__send("T," + str(fr) + "," + str(timer) + "|")
        if wait:
            self.wait(timer)
        return mes

    def light(self, l, wait=False):
        if self.flag_pyboard:
            mes = self.__send("L," + str(l) + "|")
        else:
            mes = self.__send("L," + str(l) + "|")
        return mes

    def sirena(self, timer, tone=100, wait=False):
        if self.flag_pyboard:
            mes = self.__send("Q," + str(timer) + "," + str(tone) + "|")
        else:
            mes = self.__send("Q," + str(timer) + "," + str(tone) + "|")
        return mes

    def serv(self, angle, num=0, min=-60, max=60):
        if angle > max:
            angle = max
        if angle < min:
            angle = min
        if self.flag_pyboard:
            return self.__send("S," + str(num) + "," + str(round(angle, 1)) + "|", wait_answer=False)
        else:
            # return self.__send("SERV," + str(angle) + "|")
            return self.__send(''.join(["S,", str(int(num)), ",", str(int(angle)), "|"]))

    def dist(self):

        s = self.__send("D|")
        # print('disr', s)
        d = None
        try:
            s = s.split(",")
            if s[0] == "D":
                d = float(s[1])
        except:
            pass
        return d

    def rc(self):
        # print(s)
        d = []
        if self.flag_pyboard:
            s = self.__send("R|")
        else:
            s = self.__send("RC,|")
        # print(s)
        try:

            s = s.split(",")
            if s[0] != 'R':
                return d
            kol = int(s[1])
            s = s[2:]
            # print(len(s),kol)
            if len(s) != kol + 1:
                return d
            crc = s[-1]
            s = s[:-1]

            packet = bytearray()
            for c in s:
                r = self._fromInt16(int(c))
                packet.append(r[0])
                packet.append(r[1])
                d.append(int(c))
            if len(packet) > 0:
                h = Crc8DvbS2.calc(packet)
                if h != int(crc):
                    d = []

        except Exception as e:
            # print("rc eroor",e)
            return []

        return d

    def compas(self):
        d = [0, 0, 0, 0]
        try:
            s = self.__send("COMPAS,|")
            s = s.split(",")

            d = [float(s[1]), float(s[2]), float(s[3]), float(s[4])]
        except:
            pass
        return d

    def gps(self):
        d = [0, 0, 0, 0, 0, 0]
        try:
            s = self.__send("GPS,|")
            s = s.split(",")

            d = [float(s[1]), float(s[2]), float(s[3]), float(s[4]), float(s[5]), float(s[5])]
        except:
            pass
        return d

    def vcc(self):
        if self.flag_pyboard:
            s = self.__send("V|")
        else:
            # s = self.__send("VCC,|")
            s = self.__send("V|")
        v = -1
        try:
            s = s.split(",")
            v = float(s[1])
        except:
            pass
        return v

    def speed(self):
        if self.flag_pyboard:
            s = self.__send("P|")
        else:
            s = self.__send("SPEED,|")
        v = -1
        try:
            s = s.split(",")
            if s[0] == 'P':
                v = float(s[1])
        except:
            pass
        return v

    def odometr(self):
        if self.flag_pyboard:
            s = self.__send("O|")
        else:
            s = self.__send("O,|")
        # pos = s.find("VCC")
        # s = s[pos:]

        v = -1
        try:
            s = s.split(",")
            if s[0] == 'O':
                if s[1] == s[2]:
                    v = float(s[1])
        except:
            pass
        if self.__last_odometr < v:
            self.__last_odometr = v
        return self.__last_odometr
        # return v

    def ir(self):

        s = self.__send("i|")
        v = []

        try:
            s = s.split(",")
            if s[0] == 'i':
                for i in s[1:]:
                    v.append(float(i))
        except:
            pass
        return v
        # return v

    def hit(self):

        s = self.__send("H|")
        v = []
        try:
            s = s.split(",")
            if s[0] == 'H':
                for i in s[1:]:
                    v.append(float(i))
            return v
        except:
            pass
        return [-1, -1]
        # return v

    def laser_shoot(self, data):

        return self.__send("G," + str(data[0]) + "," + str(data[1]) + "|", wait_answer=False)

    def odometr_reset(self):
        self.__last_odometr = 0
        if self.flag_pyboard:
            s = self.__send("o|")
        else:
            s = self.__send("o,|")
        v = -1
        try:
            s = s.split(",")
            v = float(s[1])
        except:
            pass
        return v

    def vcst(self, k):
        s = self.__send("E," + str(k) + "|")
        v = 0
        try:
            s = s.split(",")
            v = float(s[1])
        except:
            pass
        return v

    def button(self):
        if self.flag_pyboard:
            s = self.__send("B|")
        else:
            # s = self.__send("BUTT,|")
            s = self.__send("B,|")

        v = 0
        try:
            s = s.split(",")
            v = int(float(s[1]))
        except:
            pass
        return v

    def start(self):
        self.button()
        self.rgb(0, 255, 0)
        self.tone(10000, 50)
        while (self.button() == 0):
            pass
        for i in range(10000, 15000, 500):
            self.tone(i, 50)
        self.wait(100)
        self.button()
        self.rgb(0, 0, 0)

    def beep(self):
        self.tone(1000, 100)
        # self.wait(50)

    def green(self, val=255):
        self.rgb(0, val, 0)

    def red(self, val=255):
        self.rgb(val, 0, 0)

    def blue(self, val=255):
        self.rgb(0, 0, val)

    def color_off(self):
        self.rgb(0, 0, 0)

    def sound1(self):
        # for i in range (1000,10000,500):
        for i in range(15000, 1000, -500):
            self.tone(i, 50)

    def sound2(self):
        # for i in range (1000,10000,500):
        for i in range(1000, 15000, 500):
            self.tone(i, 50)

    # функция движения короткими импульсами
    def step(self, motorL, motorR, time_step=20, pulse_go=10, pause_go=20, pulse_stop=5, pause_stop=3, wait=True):
        motorL = self.constrain(motorL, -255, 255)
        motorR = self.constrain(motorR, -255, 255)
        self.motor_left = motorL
        self.motor_rigth = motorR

        m = self.__send(
            "STEP," + str(int(motorL)) + "," + str(int(motorR)) + "," + str(pulse_go) + "," + str(pause_go) + "," + str(
                pulse_stop) + "," + str(pause_stop) + "," + str(time_step) + "|")
        # print(m)
        if wait:
            self.wait(time_step)
        return m

    #
    def send_file_to_pyboard(self, name, data, size):

        m = self.__send("X" + str(name) + "|")
        print("send filename, answ:", m)

        count = 0
        s = ""
        count_byte = 0
        for d in data:
            count_byte += 1

            s += str(ord(d)) + ","
            count += 1

            if count > size or count_byte == (len(data)):

                # c = crc8(s.encode("utf-8"))
                # h = str(c.digest())
                h = str(chr(Crc8DvbS2.calc(s.encode("utf-8"))))
                if h == "b'|'":
                    h = "b'++'"
                if h == "b','":
                    h = "b'--'"

                # print("make hash from", s.encode("utf-8"))
                # print(s.encode("utf-8"))

                s = s + h
                while 1:
                    # print("send: ","x" +s + "|", "   h=",h)
                    m = self.__send("x" + s + "|", wait_time=2)

                    a = m.split(",")
                    # print("answ", m, str(a[1]), h)

                    if a[0] == 'x' and str(a[1]) == h:
                        # print("send ok")
                        break
                    # time.sleep(5)
                    print("error crc", str(a[1]), h)
                    # print("answ", m)
                    # print(str(a[1]), h)
                    # print("sleep and repeet")

                count = 0
                s = ""

        time.sleep(0.1)
        print("send reset")
        m = self.__send("r,|", wait_time=5)

        return m

    def millis(self):
        return int(round(time.time() * 1000))

    def text_to_frame(self, frame, text, x, y, font_color=(255, 255, 255), font_size=2):
        cv2.putText(frame, str(text), (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, font_color, font_size)
        return frame

    def vcc_to_frame(self, frame):
        return self.text_to_frame(frame, str(self.vcc()), 10, 20)

    def dist_to_frame(self, frame):
        return self.text_to_frame(frame, str(self.dist()), 550, 20)

    # def distance_between_points(self, xa, ya, xb, yb, za=0, zb=0):
    #     return np.sqrt(np.sum((np.array((xa, ya, za)) - np.array((xb, yb, zb))) ** 2))

    def distance_between_points(self, x1, y1, x2, y2):
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def median(self, lst):
        if len(lst) > 0:
            quotient, remainder = divmod(len(lst), 2)
            if remainder:
                return sorted(lst)[quotient]
            return sum(sorted(lst)[quotient - 1:quotient + 1]) / 2.

    def constrain(self, x, out_min, out_max):
        if x < out_min:
            return out_min
        elif out_max < x:
            return out_max
        else:
            return x

    def manual(self, c=-1, show_code=False):
        m = c
        if c == -1:
            m = self.get_key()
        frame = self.get_frame()

        if m == 49:  # клавиша1
            if self.manual_regim == 0:
                print("manual on")
                self.manual_regim = 1
                self.red()
            else:
                print("manual off")
                self.manual_regim = 0
                self.color_off()
            self.wait(200)
            self.get_key()
        if m == 8:
            if self.small_frame == 1:
                self.small_frame = 0
            else:
                self.small_frame = 1
            self.wait(200)
            self.get_key()

        if self.manual_regim == 0:
            return self.manual_regim

        if m > -1 and self.manual_regim == 1:

            if m == 38:
                self.move(self.manual_speed, self.manual_speed, 50, True)
            if m == 40:
                self.move(-self.manual_speed, -self.manual_speed, 50, True)
            if m == 39:
                self.move(self.manual_speed, -self.manual_speed, 50, True)
            if m == 37:
                self.move(-self.manual_speed, self.manual_speed, 50, True)
            if m == 188:
                self.manual_angle -= 30
                self.serv(self.manual_angle)
            if m == 190:
                self.manual_angle += 30
                self.serv(self.manual_angle)
            if m == 32:
                self.manual_angle = 0
                self.serv(self.manual_angle)
            if m == 66:
                self.tone(1000, 50)
            if m == 189:
                self.manual_speed -= 20
                if self.manual_speed < 100:
                    self.manual_speed = 100

            if m == 187:
                self.manual_speed += 20
                if self.manual_speed > 250:
                    self.manual_speed = 250

            if m == 86:
                if self.manual_video == 0:
                    self.manual_video = 1
                else:
                    self.manual_video = 0
            if show_code:
                print(m)

                #     self.set_frame(
                # self.dist_to_frame(self.vcc_to_frame(self.text_to_frame(frame, "manual", 280, 20))))

        if self.manual_regim == 1 and self.manual_video == 1:

            if self.small_frame == 1:
                if frame is not None:
                    frame = cv2.resize(frame, None, fx=0.25, fy=0.25)
                    self.set_frame(frame, 10)
                return self.manual_regim

            frame = self.dist_to_frame(self.vcc_to_frame(self.text_to_frame(frame, "manual", 280, 20)))
            # frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.set_frame(frame)

        return self.manual_regim

    def take_list(self):
        pass
