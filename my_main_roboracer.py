import pyb
import utime, math
import machine
# machine.reset()

from pyb import Pin, Timer

from module import PWM, map, median, constrain

import array

# main.py -- put your code here!
import pyb
import struct

servo1 = pyb.Servo(1)
servo1.angle(0)

import _thread


class Thread:

    def __init__(self, target=None, args=(), kwargs=None):
        self.target = target
        self.args = args
        self.kwargs = {} if kwargs is None else kwargs

    def start(self):
        _thread.start_new_thread(self.run, ())

    def run(self):
        self.target(*self.args, **self.kwargs)


class SBUSReceiver:
    def __init__(self, uart_port):
        self.sbus = UART(uart_port, 100000)
        self.sbus.init(100000, bits=8, parity=0, stop=2, timeout_char=3, read_buf_len=250)

        # constants
        self.START_BYTE = b'0f'
        self.END_BYTE = b'00'
        self.SBUS_FRAME_LEN = 25
        self.SBUS_NUM_CHAN = 18  # 18
        self.OUT_OF_SYNC_THD = 10
        self.SBUS_NUM_CHANNELS = 18  # 18
        self.SBUS_SIGNAL_OK = 0
        self.SBUS_SIGNAL_LOST = 1
        self.SBUS_SIGNAL_FAILSAFE = 2

        # Stack Variables initialization
        self.validSbusFrame = 0
        self.lostSbusFrame = 0
        self.frameIndex = 0
        self.resyncEvent = 0
        self.outOfSyncCounter = 0
        self.sbusBuff = bytearray(1)  # single byte used for sync
        self.sbusFrame = bytearray(25)  # single SBUS Frame
        self.sbusChannels = array.array('H', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # RC Channels
        self.isSync = False
        self.startByteFound = False
        self.failSafeStatus = self.SBUS_SIGNAL_FAILSAFE

    def get_rx_channels(self):
        """
        Used to retrieve the last SBUS channels values reading
        :return:  an array of 18 unsigned short elements containing 16 standard channel values + 2 digitals (ch 17 and 18)
        """
        return self.sbusChannels

    def get_rx_channel(self, num_ch):
        """
        Used to retrieve the last SBUS channel value reading for a specific channel
        :param: num_ch: the channel which to retrieve the value for
        :return:  a short value containing
        """
        return self.sbusChannels[num_ch]

    def get_failsafe_status(self):
        """
        Used to retrieve the last FAILSAFE status
        :return:  a short value containing
        """
        return self.failSafeStatus

    def get_rx_report(self):
        """
        Used to retrieve some stats about the frames decoding
        :return:  a dictionary containg three information ('Valid Frames','Lost Frames', 'Resync Events')
        """

        rep = {}
        rep['Valid Frames'] = self.validSbusFrame
        rep['Lost Frames'] = self.lostSbusFrame
        rep['Resync Events'] = self.resyncEvent

        return rep

    def decode_frame(self):

        # TODO: DoubleCheck if it has to be removed
        for i in range(0, self.SBUS_NUM_CHANNELS - 2):
            self.sbusChannels[i] = 0

        # counters initialization
        byte_in_sbus = 1
        bit_in_sbus = 0
        ch = 0
        bit_in_channel = 0

        for i in range(0, 175):  # TODO Generalization
            if self.sbusFrame[byte_in_sbus] & (1 << bit_in_sbus):
                self.sbusChannels[ch] |= (1 << bit_in_channel)

            bit_in_sbus += 1
            bit_in_channel += 1

            if bit_in_sbus == 8:
                bit_in_sbus = 0
                byte_in_sbus += 1

            if bit_in_channel == 11:
                bit_in_channel = 0
                ch += 1

        # Decode Digitals Channels

        # Digital Channel 1
        if self.sbusFrame[self.SBUS_FRAME_LEN - 2] & (1 << 0):
            self.sbusChannels[self.SBUS_NUM_CHAN - 2] = 1
        else:
            self.sbusChannels[self.SBUS_NUM_CHAN - 2] = 0

        # Digital Channel 2
        if self.sbusFrame[self.SBUS_FRAME_LEN - 2] & (1 << 1):
            self.sbusChannels[self.SBUS_NUM_CHAN - 1] = 1
        else:
            self.sbusChannels[self.SBUS_NUM_CHAN - 1] = 0

        # Failsafe
        self.failSafeStatus = self.SBUS_SIGNAL_OK
        if self.sbusFrame[self.SBUS_FRAME_LEN - 2] & (1 << 2):
            self.failSafeStatus = self.SBUS_SIGNAL_LOST
        if self.sbusFrame[self.SBUS_FRAME_LEN - 2] & (1 << 3):
            self.failSafeStatus = self.SBUS_SIGNAL_FAILSAFE

    def get_sync(self):

        if self.sbus.any() > 0:

            if self.startByteFound:
                if self.frameIndex == (self.SBUS_FRAME_LEN - 1):
                    self.sbus.readinto(self.sbusBuff, 1)  # end of frame byte
                    if self.sbusBuff[0] == 0:  # TODO: Change to use constant var value
                        self.startByteFound = False
                        self.isSync = True
                        self.frameIndex = 0
                else:
                    self.sbus.readinto(self.sbusBuff, 1)  # keep reading 1 byte until the end of frame
                    self.frameIndex += 1
            else:
                self.frameIndex = 0
                self.sbus.readinto(self.sbusBuff, 1)  # read 1 byte
                if self.sbusBuff[0] == 15:  # TODO: Change to use constant var value
                    self.startByteFound = True
                    self.frameIndex += 1

    def get_new_data(self):
        """
        This function must be called periodically according to the specific SBUS implementation in order to update
        the channels values.
        For FrSky the period is 300us.
        """

        if self.isSync:
            if self.sbus.any() >= self.SBUS_FRAME_LEN:

                self.sbus.readinto(self.sbusFrame, self.SBUS_FRAME_LEN)  # read the whole frame

                if (self.sbusFrame[0] == 15 and self.sbusFrame[
                    self.SBUS_FRAME_LEN - 1] == 0):  # TODO: Change to use constant var value

                    self.validSbusFrame += 1
                    self.outOfSyncCounter = 0
                    self.decode_frame()
                else:
                    self.lostSbusFrame += 1
                    self.outOfSyncCounter += 1

                if self.outOfSyncCounter > self.OUT_OF_SYNC_THD:
                    self.isSync = False
                    self.resyncEvent += 1
        else:
            self.get_sync()


l1 = pyb.LED(2)

#
vcc = pyb.ADC("Y12")  # create an analog object from a pin

# mouse
# m_A_shim = PWM("X6", 50000)
# m_B_shim = PWM('X7', 50000)
#
# m_A_1 = Pin('Y9', Pin.OUT_PP)
# m_A_2 = Pin('X8', Pin.OUT_PP)
#
# m_B_1 = Pin('Y10', Pin.OUT_PP)
# m_B_2 = Pin('Y11', Pin.OUT_PP)

# racer
m_A_shim = PWM("X6", 50000)
m_B_shim = PWM('X7', 50000)

m_A_1 = Pin('X8', Pin.OUT_PP)
m_A_2 = Pin('X7', Pin.OUT_PP)

m_B_1 = Pin('Y10', Pin.OUT_PP)
m_B_2 = Pin('Y11', Pin.OUT_PP)

light = PWM("Y10", 50000)
sirena = PWM("Y9", 50000)
sirena.pwm_write(0)
timer_sirena = -1

import pyb
import utime


class Regulators:
    __Kp = 0
    __Ki = 0
    __Kd = 0

    __prev = 0
    __sum = 0
    __freq = 0
    __time = 0

    def __init__(self, Kp, Ki, Kd):
        self.__Kp = Kp
        self.__Ki = Ki
        self.__Kd = Kd
        self.__time = utime.ticks_us()

    def apply(self, to_set, current):
        error = to_set - current
        self.__update_freq()
        # value = self.__Prop(error) + self.__Integ(error) + self.__Diff(error)
        # start
        value = 0
        value += self.__Prop(error)
        value += self.__Integ(error)
        value += self.__Diff(error)
        # end
        self.__prev = error
        return value

    def set(self, Kp, Ki, Kd):
        self.__Kp = Kp
        self.__Ki = Ki
        self.__Kd = Kd

    def __Prop(self, error):
        return error * self.__Kp

    def __Integ(self, error):
        self.__sum += self.__Ki * (1 / self.__freq) * error
        return self.__sum

    def __Diff(self, error):
        return self.__Kd / self.__freq * (error - self.__prev)

    def __update_freq(self):
        self.__freq = -utime.ticks_diff(self.__time, utime.ticks_us())
        self.__time = utime.ticks_us()


reg_move = Regulators(30, 0.0001, 300)

timer_move2 = -1
speed = 0
speed_fix = 0
timer_jumm = 0


def move_fix_speed():
    global reg_move, speed, speed_fix, timer_jumm
    # reg_move.set(5, 0.00001, 0.01)
    # print(speed, utime.ticks_ms() -timer_jumm)
    # k=1
    if speed == 0:
        ttt = (utime.ticks_ms() - timer_jumm)
        if ttt > 40:
            if ttt % 50 == 0:
                if ttt > 200:
                    move(-80, -80)
                    utime.sleep_ms(5)
                    move(100, 100)
                    utime.sleep_ms(20)
                elif ttt > 100:
                    # print("force10", ttt)
                    move(100, 100)
                    utime.sleep_ms(10)
                else:
                    # print("force5",ttt)
                    move(100, 100)
                    utime.sleep_ms(5)

            if ttt > 500:
                # if ttt % 200 == 0:
                timer_jumm = utime.ticks_ms()
                # print("jumm",ttt)
                move(-80, -80)
                utime.sleep_ms(7)
                move(0, 0)
    else:
        timer_jumm = utime.ticks_ms()

    vector = 1
    if speed_fix < 0:
        vector = -1
    p = reg_move.apply(abs(speed_fix), speed)
    # p = constrain(p, -5, 100)
    p = constrain(p, -5, 100)
    # print("p", p, "speed", speed)

    move(p * vector, 0)


def move(m_left, m_right):
    global m_A_shim, m_B_shim, m_A_1, m_A_2, m_B_1, m_B_2

    # print("move ",m_left)
    # m_left = constrain(m_left, -100, 100)
    # m_right = constrain(m_right, -100, 100)
    if m_left >= 0:
        # print("l",m_left)
        m_A_1.high()
        m_A_2.low()
        m_A_shim.pwm_write(m_left)
    else:

        m_A_1.low()
        m_A_2.high()
        m_A_shim.pwm_write(-m_left)

    # if m_right >= 0:
    #     # print("r",m_right)
    #     m_B_1.low()
    #     m_B_2.high()
    #     m_B_shim.pwm_write(m_right)
    # else:
    #     m_B_1.high()
    #     m_B_2.low()
    #     m_B_shim.pwm_write(-m_right)


accel = pyb.Accel()

from pyb import UART


class encoder(object):
    __tencoder2 = 0
    __encoder_tick = 0
    __all_encoder_tick = 0

    def __init__(self):
        self.enc1 = Pin('Y3')
        self.l2 = pyb.LED(3)
        # self.extint = pyb.1ExtInt(self.enc1, pyb.ExtInt.IRQ_RISING_FALLING, pyb.Pin.PULL_DOWN, self.work)
        self.__extint = pyb.ExtInt(self.enc1, pyb.ExtInt.IRQ_RISING_FALLING, pyb.Pin.PULL_NONE, self.work)

    def value(self):
        return self.__encoder_tick

    def odometr(self):
        return self.__all_encoder_tick + self.__encoder_tick

    def reset(self, add=True):
        if add:
            self.__all_encoder_tick += self.__encoder_tick
        self.__encoder_tick = 0

    def reset_odometr(self):
        self.__all_encoder_tick = 0

    def work(self, line):
        # self.__extint.disable()
        self.l2.toggle()
        if self.enc1.value():
            self.__encoder_tick += 1
        # self.__extint.enable()


enc = encoder()

print("Start work")

# uart = UART(6, 115200, stop=2, timeout=5)  # timeout=5, timeout_char=3
uart = UART(6, 115200, stop=1)  # timeout=5, timeout_char=3

r = -1
timer_move = 0
vcc_list = []
tt = utime.ticks_ms()
# ccc=0
chanels = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# import gc
sbus = SBUSReceiver(2)


def update_rx_data(timRx):
    global chanels
    sbus.get_new_data()
    chanels = sbus.get_rx_channels()
    # print(chanels)


timRx = pyb.Timer(4)
timRx.init(freq=2778)
timRx.callback(update_rx_data)

tencoder = utime.ticks_ms()

p2 = Pin("Y6")  # Y6
tim = Timer(1, freq=500)
ch = tim.channel(1, Timer.PWM, pin=p2)

for i in range(100, 3000, 10):
    tim.freq(i)
    ch.pulse_width_percent(30)
    utime.sleep_ms(1)
ch.pulse_width_percent(100)

msgs = ""
buffer = bytearray()
buf = bytearray()
flag_packet = False
light_flag = False

sw = pyb.Switch()
button_press = 0


def press():
    global button_press
    button_press = 1


sw.callback(press)


class crc8(object):
    digest_size = 1
    block_size = 1

    _table = [0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15,
              0x38, 0x3f, 0x36, 0x31, 0x24, 0x23, 0x2a, 0x2d,
              0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65,
              0x48, 0x4f, 0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d,
              0xe0, 0xe7, 0xee, 0xe9, 0xfc, 0xfb, 0xf2, 0xf5,
              0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd,
              0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b, 0x82, 0x85,
              0xa8, 0xaf, 0xa6, 0xa1, 0xb4, 0xb3, 0xba, 0xbd,
              0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
              0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea,
              0xb7, 0xb0, 0xb9, 0xbe, 0xab, 0xac, 0xa5, 0xa2,
              0x8f, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a,
              0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32,
              0x1f, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0d, 0x0a,
              0x57, 0x50, 0x59, 0x5e, 0x4b, 0x4c, 0x45, 0x42,
              0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a,
              0x89, 0x8e, 0x87, 0x80, 0x95, 0x92, 0x9b, 0x9c,
              0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
              0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec,
              0xc1, 0xc6, 0xcf, 0xc8, 0xdd, 0xda, 0xd3, 0xd4,
              0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c,
              0x51, 0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44,
              0x19, 0x1e, 0x17, 0x10, 0x05, 0x02, 0x0b, 0x0c,
              0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34,
              0x4e, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5c, 0x5b,
              0x76, 0x71, 0x78, 0x7f, 0x6a, 0x6d, 0x64, 0x63,
              0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
              0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13,
              0xae, 0xa9, 0xa0, 0xa7, 0xb2, 0xb5, 0xbc, 0xbb,
              0x96, 0x91, 0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83,
              0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc, 0xcb,
              0xe6, 0xe1, 0xe8, 0xef, 0xfa, 0xfd, 0xf4, 0xf3]

    def __init__(self, initial_string=b''):
        """Create a new crc8 hash instance."""
        self._sum = 0x00
        self._update(initial_string)

    def update(self, bytes_):
        """Update the hash object with the string arg.

        Repeated calls are equivalent to a single call with the concatenation
        of all the arguments: m.update(a); m.update(b) is equivalent
        to m.update(a+b).
        """
        self._update(bytes_)

    def digest(self):
        """Return the digest of the bytes passed to the update() method so far.

        This is a string of digest_size bytes which may contain non-ASCII
        characters, including null bytes.
        """
        return self._digest()

    def hexdigest(self):
        """Return digest() as hexadecimal string.

        Like digest() except the digest is returned as a string of double
        length, containing only hexadecimal digits. This may be used to
        exchange the value safely in email or other non-binary environments.
        """
        return hex(self._sum)[2:].zfill(2)

    # if PY2:
    #     def _update(self, bytes_):
    #         if isinstance(bytes_, unicode):
    #             bytes_ = bytes_.encode()
    #         elif not isinstance(bytes_, str):
    #             raise TypeError("must be string or buffer")
    #         table = self._table
    #         _sum = self._sum
    #         for byte in bytes_:
    #             _sum = table[_sum ^ ord(byte)]
    #         self._sum = _sum
    #
    #     def _digest(self):
    #         return chr(self._sum)
    # else:
    def _update(self, bytes_):
        if isinstance(bytes_, str):
            raise TypeError("Unicode-objects must be encoded before" \
                            " hashing")
        elif not isinstance(bytes_, (bytes, bytearray)):
            raise TypeError("object supporting the buffer API required")
        table = self._table
        _sum = self._sum
        for byte in bytes_:
            _sum = table[_sum ^ byte]
        self._sum = _sum

    def _digest(self):
        return bytes([self._sum])

    def copy(self):
        """Return a copy ("clone") of the hash object.

        This can be used to efficiently compute the digests of strings that
        share a common initial substring.
        """
        crc = crc8()
        crc._sum = self._sum
        return crc


def encoder_work():
    global speed, enc
    # tencoder = utime.ticks_ms() + 10
    tencoder = utime.ticks_ms() + 10
    while 1:
        if utime.ticks_ms() > tencoder:
            speed = enc.value()
            if speed > 80:
                # print("sboy", speed)
                speed = 0
                enc.reset(add=False)
            else:
                enc.reset()
            # tencoder = utime.ticks_ms() + 10
            tencoder = utime.ticks_ms() + 10
        utime.sleep_ms(1)


tr1 = Thread(target=encoder_work)
tr1.start()


def fix_move_t():
    global timer_move2, timer_move
    while 1:
        if timer_move2 > -1:
            move_fix_speed()
            if timer_move2 < utime.ticks_ms():
                move(0, 0)
                timer_move2 = -1
        else:
            utime.sleep_ms(1)

        if timer_move > -1:
            if timer_move < utime.ticks_ms():
                move(0, 0)
                timer_move = -1
        # utime.sleep_ms(1)


tr_move = Thread(target=fix_move_t)
tr_move.start()

filename = ""
last_error = 0
while 1:

    val = vcc.read()  # read an analog value
    # vcc_list.append(float(val) * 0.00254)
    vcc_list.append(float(val) * 0.00388)  # roboracer 0
    # vcc_list.append(float(val) * 0.00373)  # roboracer DT
    # vcc_list.append(float(val) * 0.00379)  # roboracer DANIL
    if len(vcc_list) > 100:
        vcc_list.pop(0)

    if utime.ticks_ms() - last_error > 3000:
        l1.off()

    # if timer_sirena > -1:
    #     if timer_sirena < utime.ticks_ms():
    #         sirena.pwm_write(0)
    #         timer_sirena = -1

    if uart.any() > 0:
        buf += uart.read(uart.any())
        i = 0
        stop_marker = 0
        for b in buf:
            if b == 124:
                stop_marker = i
                flag_packet = True
            i += 1

        buffer = buf[:stop_marker]
        buf = buf[stop_marker:]

    if flag_packet == True:
        # l1.off()
        flag_packet = False

        msgss = b''

        try:
            msgss = str(buffer, "utf-8").split('|')
        except:
            continue
        buffer = bytearray()

        # msgss = msgss[:-1]
        # m = msgs.split('|')

        # print(buffer)

        for msgs in msgss:
            if len(msgs) == 0:
                continue
            try:

                answ = ""
                command = msgs[0]
                # print(msgs)

                # if msg.find("M") > -1:
                if command == 'M':
                    # print("move work")
                    m = msgs.split(',')
                    # print(m)
                    timer_move = utime.ticks_ms() + int(m[3])
                    m1 = map(int(m[1]), -255, 255, -100, 100)
                    m2 = map(int(m[2]), -255, 255, -100, 100)
                    # timer_move = utime.ticks_ms() + float(10)
                    # m1 = map(int(10), -255, 255, -100, 100)
                    # m2 = map(int(10), -255, 255, -100, 100)
                    move(m1, m2)
                    # answ = 'M,0|'
                elif command == 'F':
                    m = msgs.split(',')
                    if timer_move2 == -1:
                        timer_jumm = utime.ticks_ms()
                    timer_move2 = utime.ticks_ms() + int(m[3])

                    # m1 = map(int(m[1]), -255, 255, -100, 100)
                    # m2 = map(int(m[2]), -255, 255, -100, 100)
                    p = float(m[4])
                    i = float(m[5])
                    d = float(m[6])
                    reg_move.set(p, i, d)
                    speed_fix = int(m[1])

                    # answ = 'F,0|'
                elif command == 'C':
                    # RGB color
                    answ = 'C,0|'
                elif command == 'D':
                    answ = 'D,100|'
                elif command == 'P':
                    # VCC
                    answ = "P," + str(int(speed)) + '|'
                    # answ = '0|'

                elif command == 'V':
                    # VCC
                    v = '%.2f' % round(median(vcc_list), 2)
                    answ = "V," + str(v) + '|'
                    # answ = '0|'
                elif command == 'B':
                    # BUTTON
                    answ = "B," + str(button_press) + '|'
                    button_press = 0
                elif command == 'T':
                    # TONE
                    m = msgs.split(',')
                    # print("tone", m)
                    tim.freq(int(m[1]))
                    ch.pulse_width_percent(1)
                    utime.sleep_ms(int(m[2]))
                    ch.pulse_width_percent(100)
                    answ = "T," + '0|'
                elif command == 'S':  # S,4,-600,-20,1,40|
                    # SERVO
                    m = msgs.split(',')
                    # print(m)
                    servo1.angle(int(float(m[2])))
                    # answ = "S," + '0|'
                    # print("servo",int(float(m[1])))
                    # uart.write('S,1 \r\n')
                elif command == 'A':
                    # ACCEL
                    x, y, z = accel.filtered_xyz()
                    # print(x, y, z)
                    answ = "A," + str(x) + "," + str(y) + "," + str(z) + "|"
                elif command == 'R':
                    # RC
                    answ = 'RC,5,' + str(chanels[0]) + "," + str(chanels[1]) + "," + str(chanels[2]) + "," + str(
                        chanels[3]) + "," + str(chanels[4]) + '|'

                elif command == 'L':
                    # LIGHT
                    m = msgs.split(',')
                    # print("ligth", m)
                    light.pwm_write(int(m[1]))
                    answ = 'L,' + str(m[1]) + '|'

                elif command == 'Q':
                    # SIRENA
                    m = msgs.split(',')
                    sirena.pwm_write(m[2])
                    # print(m[1])
                    timer_sirena = utime.ticks_ms() + int(m[1])
                    answ = 'B,' + str(m[1]) + '|'

                elif command == 'O':
                    # odometr
                    # m = msgs.split(',')
                    # sirena.pwm_write(m[2])
                    # print(m[1])
                    # timer_sirena = utime.ticks_ms() + int(m[1])
                    odometr = enc.odometr()
                    answ = 'O,' + str(round(odometr * 0.2, 1)) + ','+str(round(odometr * 0.2, 1))+'|'
                elif command == 'o':
                    # odometr
                    # m = msgs.split(',')
                    # sirena.pwm_write(m[2])
                    # print(m[1])
                    # timer_sirena = utime.ticks_ms() + int(m[1])
                    enc.reset_odometr()
                    answ = 'o,' + str(0) + '|'

                elif command == 'X':
                    # print("take file")
                    m = msgs[1:].split(',')
                    filename = str(m[0])
                    print("file begin", filename)
                    file = open(filename, 'wb')
                    answ = 'X,' + filename + '|'

                elif command == 'x':
                    # print("take parth file")
                    # print(msgs)
                    # tx = utime.ticks_us()
                    if filename != '':
                        if msgs[1] == 'x':
                            msgs = msgs[1:]

                        m = msgs[1:].split(',')
                        b = str(m[len(m) - 1])
                        # print(msgs)
                        data = str(msgs[1:-(len(b))])
                        # print(data)
                        c = crc8(data.encode("utf-8"))
                        h = str(c.digest())
                        if h == "b'|'":
                            h = "b'++'"
                        if h == "b','":
                            h = "b'--'"

                        # print("hash",h,b)
                        if h == b:
                            s = ""
                            # print("save to file", data.split(","))
                            for i in data.split(","):
                                if i != '':
                                    s += chr(int(i))
                            # print("save to file", s)
                            try:
                                file.write(s)
                            except:
                                print("eroor ssave ", s)
                        else:
                            print("error crc", h, b)
                        answ = 'x,' + h + '|'
                        # print(answ)
                    else:
                        answ = 'x,0|'
                    # print(utime.ticks_us()-tx)

                elif command == 'r':
                    import machine

                    answ = 'r,1|'
                    uart.write(answ)
                    if filename != '':
                        file.close()
                    machine.reset()

            except Exception as e:
                #                print("ERROR!", e, msgss)
                l1.on()
                last_error = utime.ticks_ms()

            # flag_send = 0
            if answ != "":
                # while flag_send < 10 and answ != "":
                    try:
                        # for c in answ:
                        #     uart.writechar(ord(c))
                        # print("write", answ)

                        uart.write(answ)
                        # if flag_send > 0:
                        #     print("send ok", flag_send)
                        # break
                    except Exception as e:
                        #                       print("error send ",e, answ, msgs)
                        # break
                        pass
                    # flag_send += 1

        buffer = bytearray()
