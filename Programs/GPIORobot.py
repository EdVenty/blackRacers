import abc
import subprocess
from typing import List, Type

import cv2
from numpy import invert
# import RPi.GPIO as GPIO
import pigpio
import time
import RobotAPI as rapi
import board
import neopixel

GPIO_PWM_SERVO = 13
GPIO_PWM_MOTOR = 12
GPIO_PIN_CW = 17
GPIO_PIN_CCW = 27

WORK_TIME = 10
DUTY_CYCLE = 50
FREQUENCY = 100

CLOCKWISE = True
COUNTERCLOCKWISE = False

pi = pigpio.pi()


def arduino_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def constrain(x, out_min, out_max):
    return out_min if x < out_min else out_max if x > out_max else x


def hsv_to_rgb(h, s, v):
    if s == 0.0: v*=255; return (v, v, v)
    i = int(h*6.) # XXX assume int() truncates!
    f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)


class AbstractTimeWaiter(abc.ABC):
    @abc.abstractmethod
    def tick(self):
        """Abstract tick. Refreshes some states, calls methods, etc. Calls every loop iteration.
        """
    
    @abc.abstractmethod
    def start(self, time_: int):
        """Start waiter with specified time.
        Args:
            time_ (int): Specified time.
        """

    @abc.abstractmethod
    def stop(self):
        """Stop waiter. Resets time.
        """

class Timer(AbstractTimeWaiter):
    def __init__(self) -> None:
        self._time_set = 0
        self._exceed_in = 0
        self._callbacks = []
        self.working = False

    def callback(self, func):
        """Decorator to register a new callback which will be called when time will exceed.
        Args:
            func (Function): Callback function.
        Returns:
            __wrapper__ (this is decorator, so it must to return wrapper. Don't interact with it in your code.)
        """
        if func not in self._callbacks:
            self._callbacks.append(func)
        def __wrapper__(*args, **kwargs):
            func(args, kwargs)
        return __wrapper__

    def start(self, time_: int):
        """Start timer for a specified time.
        Args:
            time_ (int): Time for waiting.
        """
        self._time_set = time_
        self._exceed_in = time.time() + time_
        self.working = True

    def stop(self):
        """Stop timer. Resets time waiting.
        """
        self._time_set = 0
        self._exceed_in = 0
        self.working = False

    def tick(self):
        """Check for the time exceeding and call callback if needed. Must be called in all iterations of loop. Perfer to put timer to a robot with Robot.add_waiter().
        """
        if self.working and time.time() > self._exceed_in:
            self.working = False
            for c in self._callbacks:
                c()

class Interval(AbstractTimeWaiter):
    def __init__(self) -> None:
        self._time_set = 0
        self._exceed_in = 0
        self._callbacks = []
        self.working = False

    def callback(self, func):
        """Decorator to register a new callback which will be called when time will exceed.
        Args:
            func (Function): Callback function.
        Returns:
            __wrapper__ (this is decorator, so it must to return wrapper. Don't interact with it in your code.)
        """
        if func not in self._callbacks:
            self._callbacks.append(func)
        def __wrapper__(*args, **kwargs):
            func(args, kwargs)
        return __wrapper__

    def start(self, time_: int):
        """Start timeout for a specified time.
        Args:
            time_ (int): Time for waiting.
        """
        self._time_set = time_
        self._exceed_in = time.time() + time_
        self.working = True

    def stop(self):
        """Stop timeout. Resets time waiting.
        """
        self._time_set = 0
        self._exceed_in = 0
        self.working = False

    def tick(self):
        """Check for the time exceeding and call callback if needed, then refreshes time. Must be called in all iterations of loop. Perfer to put timer to a robot with Robot.add_waiter().
        """
        if self.working and time.time() > self._exceed_in:
            start_call_time = time.time()
            for c in self._callbacks:
                c()
            self._exceed_in = self._time_set - (time.time() - start_call_time)

class AbstractComponent(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        self.started = False

    @abc.abstractmethod
    def start(self):
        ...

    @abc.abstractmethod
    def stop(self):
        ...

    def cleanup(self):
        ...


class AbstractOutputComponent(AbstractComponent):
    @abc.abstractmethod
    def write(self):
        ...


class AbstractInputComponent(AbstractComponent):
    @abc.abstractmethod
    def read(self):
        ...


class AbstractInputOutputComponent(AbstractInputComponent, AbstractOutputComponent):
    ...

class AbstractRemoteComponent(AbstractComponent):
    ...

class AbstractGateComponent(AbstractComponent):
    ...

class BoardComponent(AbstractComponent):
    def __init__(self):
        self.started = False

    def start(self):
        self.started = True

    def stop(self):
        self.started = False

    def _read_voltage(self, device: str):
        return float(subprocess.run(["vcgencmd", "measure_volts", device]).stdout.decode('ascii').removeprefix('volt=').removesuffix('V'))

    def read_throttle(self):
        return int(subprocess.run(["vcgencmd", "get_throttled"]).stdout.decode('ascii').removeprefix('throttled='), 16)
    
    def read_voltage_core(self):
        return self._read_voltage('core')

    def read_voltage_sdram_i(self):
        return self._read_voltage('sdram_i')

    def read_voltage_sdram_p(self):
        return self._read_voltage('sdram_p')

    def read_voltage_sdram_c(self):
        return self._read_voltage('sdram_c')

class Motor(AbstractOutputComponent):
    def __init__(self, pwm_pin: int, pin_CW: int, pin_CCW: int, frequency: int = 100, enable_timer=False, delay: int = 0.1) -> None:
        self.pin_pwm = pwm_pin
        self.freq = frequency
        self.pwm = None
        self.pin_CW = pin_CW
        self.pin_CCW = pin_CCW
        self.started = False
        self.timer_enabled = enable_timer
        self.timer = 0
        self.delay = delay

    def start(self):
        pi.set_mode(self.pin_CW, pigpio.OUTPUT)
        pi.set_mode(self.pin_CCW, pigpio.OUTPUT)
        pi.set_mode(self.pin_pwm, pigpio.OUTPUT)
        self.started = True

    def write(self, force: int, clockwise=True):
        assert self.started, "Start servo before using this method."
        if not self.timer_enabled or time.time() > self.timer:
            if clockwise:
                pi.write(self.pin_CCW, 0)
                pi.write(self.pin_CW, 1)
            else:
                pi.write(self.pin_CW, 0)
                pi.write(self.pin_CCW, 1)
            # arduino_map(force, 0, 100, 0, 255)
            pi.set_PWM_dutycycle(self.pin_pwm, constrain(force, 0, 255))
            self.timer = time.time() + self.delay

    def stop(self):
        assert self.started, "Start servo before using this method."
        # self.pwm.stop()
        self.write(0)
        self.started = False

    def cleanup(self):
        # GPIO.cleanup()
        ...


class Button(AbstractInputComponent):
    def __init__(self, pin: int, invert: bool = False) -> None:
        self.pin = pin
        self.invert = invert
        self.started = False

    def start(self):
        pi.set_mode(self.pin, pigpio.INPUT)
        pi.set_pull_up_down(self.pin, pigpio.PUD_UP)
        self.started = True

    def read(self):
        return (0 if self.invert else 1) if pi.read(self.pin) else (1 if self.invert else 0)

    def stop(self):
        self.started = False

    def cleanup(self):
        pass


class Buzzer(AbstractOutputComponent):
    def __init__(self, pin: int):
        self.pin = pin
        self.started = False

    def start(self):
        pi.set_mode(self.pin, pigpio.OUTPUT)
        self.started = True

    def write(self, duty: int):
        pi.set_PWM_dutycycle(self.pin, constrain(duty, 0, 255))

    def set_frequency(self, freq: int):
        pi.set_PWM_frequency(self.pin, freq)

    def stop(self):
        self.write(0)
        self.started = False

    def cleanup(self):
        ...


class Led(AbstractOutputComponent):
    def __init__(self, pin: int, invert: bool = False):
        self.pin = pin
        self.invert = invert
        self.started = False

    def start(self):
        pi.set_PWM_dutycycle(self.pin, abs(255 * self.invert))
        pi.set_mode(self.pin, pigpio.OUTPUT)
        self.started = True

    def write(self, duty: int):
        pi.set_PWM_dutycycle(self.pin, abs(
            255 * constrain(self.invert - duty, 0, 255)))

    def stop(self):
        self.write(0)
        self.started = False

    def cleanup(self):
        ...


class RGBLed(AbstractOutputComponent):
    def __init__(self, pin_red: int, pin_green: int, pin_blue: int, invert: bool = False):
        self.red = Led(pin_red, invert)
        self.green = Led(pin_green, invert)
        self.blue = Led(pin_blue, invert)
        self.started = False

    def start(self):
        self.red.start()
        self.green.start()
        self.blue.start()
        self.started = True

    def write(self, duty_red: int, duty_green: int, duty_blue: int):
        self.red.write(duty_red)
        self.green.write(duty_green)
        self.blue.write(duty_blue)

    def stop(self):
        self.write(0, 0, 0)
        self.started = False

    def cleanup(self):
        self.red.cleanup()
        self.green.cleanup()
        self.blue.cleanup()


class Servo(AbstractOutputComponent):
    def __init__(self, pwm_pin: int, frequency: int = 100) -> None:
        self.pin = pwm_pin
        self.freq = frequency
        self.angle = 0
        self.pwm = None
        self.started = False

    def start(self):
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(self.pin, GPIO.OUT)
        # self.pwm = GPIO.PWM(self.pin, self.freq)
        # self.pwm =
        # self.pwm.start(0)
        self.started = True

    def write(self, angle: int):
        assert self.started, "Start servo before using this method."
        self.angle = angle + 90
        duty = constrain(arduino_map(self.angle, 0, 180, 500, 2500), 500, 2500)
        # duty = float(self.angle) / 10.0 + 2.5
        # self.pwm.ChangeDutyCycle(duty)
        pi.set_servo_pulsewidth(self.pin, duty)

    def stop(self):
        assert self.started, "Start servo before using this method."
        self.write(0)
        # self.pwm.stop()
        self.started = False

    def cleanup(self):
        # GPIO.cleanup()
        ...


class RobotMotor:
    def __init__(self, motor_pwm_pin=12, motor_cw_pin=27, motor_ccw_pin=17) -> None:
        self._motor = Motor(motor_pwm_pin, motor_cw_pin, motor_ccw_pin)
        self._thrust = 0
        self._clockwise = True
        self._start_thrust = 0
        self._required_thrust = 0
        self._acceleration_timer = 0
        self._acceleration_duration = 0
        self._acceleration_enabled = True

    def disable_acceleration(self):
        self._acceleration_enabled = False

    def enable_acceleration(self):
        self._acceleration_enabled = True

    def start(self):
        self._motor.start()

    def stop(self):
        self._motor.stop()

    def cleanup(self):
        self._motor.cleanup()

    def move(self, thrust: int, clockwise=True, acceleration_duration=3):
        if self._acceleration_enabled:
            self._clockwise = clockwise
            self._acceleration_duration = acceleration_duration
            self._start_thrust = self._thrust
            self._required_thrust = thrust
            self._acceleration_timer = time.time()
        else:
            self._motor_write(thrust, clockwise)

    def _motor_write(self, thrust: int, clockwise=True):
        self._motor.write(thrust, clockwise)

    def tick(self):
        if self._thrust != self._required_thrust:
            acceleration_elapsed = constrain(
                time.time() - self._acceleration_timer, 0, self._acceleration_duration)
            self._thrust = arduino_map(
                acceleration_elapsed, 0, self._acceleration_duration, self._thrust, self._required_thrust)
            self._motor_write(abs(self._thrust), self._clockwise)


class GPIORobotApi(rapi.RobotAPI):
    def __init__(self, motor_pwm_pin=12, motor_cw_pin=27, motor_ccw_pin=17, servo_pin=13, button_pin=22, buzzer_pin=22, led_pin_red=2, led_pin_green=3, led_pin_blue=4, invert_led=True, invert_button=True, flag_video=True, flag_keyboard=True, flag_pyboard=False, udp_stream=True, udp_turbo_stream=True, udp_event=True, acceleration_enabled = True, invert_servo = False):
        super().__init__(flag_video, flag_keyboard, False,
                         flag_pyboard, udp_stream, udp_turbo_stream, udp_event)
        self._servo = Servo(servo_pin)
        self._motor = RobotMotor(motor_pwm_pin, motor_cw_pin, motor_ccw_pin)
        self._button = Button(button_pin, invert_button)
        self._buzzer = Buzzer(buzzer_pin)
        self._led = RGBLed(led_pin_red, led_pin_green,
                           led_pin_blue, invert=invert_led)
        self.pixels = neopixel.NeoPixel(board.D18, 3)
        self._board = BoardComponent()

        if not acceleration_enabled:
            self._motor.disable_acceleration()
        
        self._servo.start()
        self._motor.start()
        self._button.start()
        self._buzzer.start()
        self._led.start()
        self._board.start()

        self._fps_counter = 0
        self._fps_timer = time.time() + 1
        self.fps = -1

        self.invert_servo = invert_servo
        self.waiters: List[Type[AbstractTimeWaiter]] = []

    def __del__(self):
        self.stop()

    def stop(self):
        self._servo.stop()
        self._motor.stop()
        self._button.stop()
        self._buzzer.stop()
        self._led.stop()
        self._board.stop()

    def cleanup(self):
        self._servo.cleanup()
        self._motor.cleanup()
        self._button.cleanup()
        self._buzzer.cleanup()
        self._led.cleanup()
        self._board.cleanup()

    def show_fps(self, frame, x=20, y=20, pattern="FPS: {fps}", font_color=(255, 255, 255), font_size=2):
        self.text_to_frame(frame, pattern.format(
            fps=self.fps), x, y, font_color, font_size)

    def move(self, thrust: int, clockwise=True, acceleration_duration=3):
        self._motor.move(thrust, clockwise, acceleration_duration)

    def tick(self):
        self._fps_counter += 1
        if time.time() > self._fps_timer:
            self.fps = self._fps_counter
            self._fps_counter = 0
            self._fps_timer = time.time()
        self._motor.tick()
        for timer in self.waiters:
            timer.tick()

    def serv(self, angle: int):
        self._servo.write(constrain(angle, -80, 50) * (-1 if self.invert_servo else 1))

    def button(self):
        return self._button.read()

    def beep(self):
        self._buzzer.write(255)
        time.sleep(0.1)
        self._buzzer.write(0)

    def light(self, red, green, blue):
        self._led.write(red, green, blue)

    def buzzer(self, value, freq=30):
        self._buzzer.set_frequency(freq)
        self._buzzer.write(value)

    def set_frame(self, frame, quality=30, flip_vertical=False, flip_horizontal=False):
        if flip_vertical:
            frame = cv2.flip(frame, 0)
        if flip_horizontal:
            frame = cv2.flip(frame, 1)
        return super().set_frame(frame, quality)

    def read_throttle(self):
        return self._board.read_throttle()
    
    def read_voltage_core(self):
        return self._board.read_voltage_core()

    def read_voltage_sdram_i(self):
        return self._board.read_voltage_sdram_i()

    def read_voltage_sdram_p(self):
        return self._board.read_voltage_sdram_p()

    def read_voltage_sdram_c(self):
        return self._board.read_voltage_sdram_c()

    def add_waiter(self, waiter: Type[AbstractTimeWaiter]):
        """Add waiter.
        Args:
            waiter (Type[AbstractTimeWaiter]): Any object of type implements AbstractTimeWaiter interface.
        """
        self.waiters.append(waiter)

    def remove_waiter(self, waiter: Type[AbstractTimeWaiter]):
        """Remove waiter.
        Args:
            waiter (Type[AbstractTimeWaiter]): Any object of type implements AbstractTimeWaiter interface.
        """
        self.waiters.remove(waiter)


class GPIORobotDuoMotors(GPIORobotApi):
    def __init__(self, motor_pwm_pin=12, motor_cw_pin=27, motor_ccw_pin=17, motor2_pwm_pin=12, motor2_cw_pin=27, motor2_ccw_pin=17, servo_pin=13, button_pin=22, buzzer_pin=18, led_pin_red=2, led_pin_green=3, led_pin_blue=4, invert_led=True, invert_button=True, flag_video=True, flag_keyboard=True, flag_pyboard=False, udp_stream=True, udp_turbo_stream=True, udp_event=True, acceleration_enabled = True):
        super().__init__(motor_pwm_pin, motor_cw_pin, motor_ccw_pin, servo_pin, button_pin, buzzer_pin, led_pin_red, led_pin_green,
                         led_pin_blue, invert_led, invert_button, flag_video, flag_keyboard, flag_pyboard, udp_stream, udp_turbo_stream, udp_event)
        self._motor2 = RobotMotor(
            motor2_pwm_pin, motor2_cw_pin, motor2_ccw_pin)
        self._motor2.start()
        if not acceleration_enabled:
            self._motor.disable_acceleration()
            self._motor2.disable_acceleration()

    def move(self, thrust1: int, thrust2: int, acceleration_duration=3):
        super().move(abs(thrust1), thrust1 >= 0, acceleration_duration)
        self._motor2.move(abs(thrust2), thrust2 >= 0,
                          acceleration_duration=acceleration_duration)

    def tick(self):
        super().tick()
        self._motor2.tick()

    def stop(self):
        super().stop()
        self._motor2.stop()

    def cleanup(self):
        super().cleanup()
        self._motor2.cleanup()

class GPIORobotDuoMotorsDuoServos(GPIORobotDuoMotors):
    def __init__(self, motor_pwm_pin=12, motor_cw_pin=27, motor_ccw_pin=17, motor2_pwm_pin=12, motor2_cw_pin=27, motor2_ccw_pin=17, servo_pin=13, servo_2_pin=4, button_pin=22, buzzer_pin=18, led_pin_red=2, led_pin_green=3, led_pin_blue=4, invert_led=True, invert_button=True, flag_video=True, flag_keyboard=True, flag_pyboard=False, udp_stream=True, udp_turbo_stream=True, udp_event=True, acceleration_enabled=True):
        super().__init__(motor_pwm_pin, motor_cw_pin, motor_ccw_pin, motor2_pwm_pin, motor2_cw_pin, motor2_ccw_pin, servo_pin, button_pin, buzzer_pin, led_pin_red, led_pin_green, led_pin_blue, invert_led, invert_button, flag_video, flag_keyboard, flag_pyboard, udp_stream, udp_turbo_stream, udp_event, acceleration_enabled)
        self._servo2 = Servo(servo_2_pin)
        self._servo2.start()

    def stop(self):
        super().stop()
        self._servo2.stop()

    def serv2(self, angle: int):
        self._servo2.write(angle)

    def cleanup(self):
        super().cleanup()
        self._servo2.cleanup()

if __name__ == "__main__":
    ...
    # m = Motor(12, 23, 24)
    # m.start()
    # m.write(255)
    # time.sleep(5)
    # m.stop()
    # m.cleanup()