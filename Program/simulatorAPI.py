

import sys
import threading
import socket


IP = socket.gethostbyname(socket.gethostname())


class ConnectorDirect():

    def __init__(self, back_plane_ip_address=IP):

        # self.messages = []
        # self.my_blocks = []
        # self.my_grids = []
        #
        # self.program_block_id=0

        # self.__flag_sending = False
        # self.__list_wait = []
        # self.list_messages=[]
        self.socket_direct = socket.socket()
        self.adress = back_plane_ip_address
        self.connect(self.adress)

        my_thread_receive = threading.Thread(target=self.receive_loop)
        my_thread_receive.daemon = True
        my_thread_receive.start()

        self.list_messages = []

        my_thread_sender = threading.Thread(target=self.sender_loop)
        my_thread_sender.daemon = True
        my_thread_sender.start()

        self.timer_last_send=0

        self.program_block_id=0



        # my_thread_sender = threading.Thread(target=self.sender_loop)
        # my_thread_sender.daemon = True
        # my_thread_sender.start()
    def connect(self, adress):
        # BANYAN_IP = socket.gethostbyname(socket.gethostname())
        self.is_connected=False
        try:
            self.socket_direct = socket.socket()
            self.socket_direct.connect((adress, 9093))
            self.is_connected = True
        except Exception as e:
            # print(e)
            pass
        # if self.is_connected:
            # print("Connect ok")

    def receive_loop(self):
        while True:

            try:
                byte_frame = self.socket_direct.recv(500000)
            # byte_frame = str(byte_frame, 'utf-8')
                if byte_frame!=b'':
                    byte_frame=eval(byte_frame[:-1])
                    self.incoming_message_processing("", byte_frame)
                else:
                    time.sleep(0.005)
            except:
                self.connect(self.adress)
                time.sleep(0.005)


    def sender_loop(self):
        while True:
            if len(self.list_messages)>0:
                message, flag =self.list_messages[0]
                if flag:
                    self.send_unity_message(message)
                    # print("sendG",time.time(), message)
                    self.list_messages.remove(self.list_messages[0])
                    self.timer_last_send=time.time()+0.001
                else:
                    if time.time()>self.timer_last_send:
                        self.send_unity_message(message)
                        # print("send",time.time(), message)
                        self.timer_last_send = time.time() + 0.001
                    # else:
                    #     print("not send")
                    self.list_messages.remove(self.list_messages[0])

                # time.sleep(0.0001)
            else:
                time.sleep(0.0001)

    def send_to_unity(self, id, action, flag_garanted_send):

        action = action.replace("'", "|")
        # print("action", action)

        message = {"s": self.program_block_id,
                   "i": id,
                   "a": action
                   }
        message = str(message).replace("'", '"')
        # print("add", message)

        self.list_messages.append([message, flag_garanted_send])


    def incoming_message_processing(self, topic, payload):
        pass

    def send_unity_message(self, unity_message):
        try:
            # print("send", time.time(), unity_message)
            self.socket_direct.send(unity_message.encode("utf-8"))
            self.socket_direct.send(b'~')
        except:
            self.connect(self.adress)
        # self.publish_payload(unity_message, "send_to_unity")

    def clean_up(self):
        self.publisher.close()
        self.subscriber.close()
        self.context.term()
        sys.exit(0)

# if __name__ == "__main__":
#     my_test = Connector(BANYAN_IP)
    #
    # for i in range(2):
    #     my_thread_mouse = threading.Thread(target=test, args=(str(i),))
    #     my_thread_mouse.daemon = True
    #     my_thread_mouse.start()
    # while 1:
    #     pass

##########################################################
# import UnityConnector
import time
# import json
import numpy as np
import base64
import cv2
import socket
import struct


class Block():
    def __init__(self, data, connector):
        self.time_last_message = 0
        self.connector = connector
        self.raw_data = data
        self.id = data['id']
        self.name = data['name']
        self.type = data['type']
        self.update_data = None;
        self.count_update = 0
        self.list_garanted_waiting=[]

        # self.start_demon_sender()



    # def start_demon_sender(self):
    #     # if self.demon_work is False:
    #         self.my_thread_receive = threading.Thread(target=self.sender_garanted_list)
    #         self.my_thread_receive.daemon = True
    #         self.my_thread_receive.start()
    #
    # def sender_garanted_list(self):
    #     while 1:
    #         if len(self.list_garanted_waiting)>0:
    #             self.send_command()
    #         time.sleep(0.001)


    def send_command(self, command=None, flag_garanted_send=False):
        if self.time_last_message < time.time():
            self.time_last_message = time.time() + 0.01
            flag_garanted_send=True

        self.connector.send_to_unity(id=self.id, action=command, flag_garanted_send= flag_garanted_send)
        # if flag_garanted_send:
        #     # if len(self.list_garanted_waiting)>0:
        #     #     if self.list_garanted_waiting[-1]!=command:
        #     #         self.list_garanted_waiting.append(command)
        #     # else:
        #     if command is not None:
        #         self.list_garanted_waiting.append(command)
        #         # print("add", command,len(self.list_garanted_waiting) )
        #
        # if self.time_last_message < time.time():
        #     if len(self.list_garanted_waiting)>0:
        #         command = self.list_garanted_waiting[0]
        #         self.connector.send_to_unity(id=self.id, action=command)
        #         self.list_garanted_waiting.remove(command)
        #         print("send_garanted", time.time(), command)
        #     else:
        #         if command is not None:
        #             self.connector.send_to_unity(id=self.id, action=command)
        #             # print("send", time.time())
        #
        #     self.time_last_message = time.time() + 0.01

    def update_data_from_server(self, data):
        # print(self.name, data)
        self.update_data = data
        self.count_update += 1
        # self.ser()


class Wheel():
    def __init__(self, block):
        self.block = block

    def power(self, value='on'):
        # time.sleep(0.01)
        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)
        # time.sleep(0.01)

    def move(self, value, time_work=100, garanted_send=False):
        self.block.send_command(f"'c':'m', 'v':{value}, 'w':{time_work}", flag_garanted_send=garanted_send)

    def brake(self, value, time_work=100, garanted_send=False):
        self.block.send_command(f"'c':'b', 'v':{value}, 'w':{time_work}", flag_garanted_send=garanted_send)

    def angle(self, value, garanted_send=False):
        self.block.send_command(f"'c':'a','v':{value}",flag_garanted_send=garanted_send)


class Engine():
    def __init__(self, block):
        self.block = block

    def power(self, value='on'):
        # time.sleep(0.01)
        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)
        # time.sleep(0.01)

    def throttle(self, value, time_work=100):
        self.block.send_command(f"'c':'t', 'v':{value}, 'w':{time_work}", flag_garanted_send=True)


class Rotor():
    def __init__(self, block):
        self.block = block

    def power(self, value='on'):
        # time.sleep(0.01)
        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)
        # time.sleep(0.01)

    def angle(self, value, time_work=100):
        self.block.send_command(f"'c':'a', 'v':{value}, 'w':{time_work}", flag_garanted_send=True)


class Camera():
    def __init__(self, block,flag_direct_video = True):
        self.block = block
        self.new_frame = False
        self.flag_new_frame=False
        self.image = np.ones((240, 320, 3), dtype=np.uint8)
        self.flag_direct_video = flag_direct_video

    def power(self, value='on'):
        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)

    def frame(self, wait_new_frame=True):

        # if wait_new_frame:
        #      while self.block.update_data is None:
        #          time.sleep(0.001)
        #          # cv2.waitKey(1)

        if self.block.update_data is not None:
            if self.flag_direct_video:
                base64_message = self.block.update_data
            else:
                base64_message = base64.b64decode(self.block.update_data)

            # if wait_new_frame:
            self.block.update_data = None
            try:
                A = np.frombuffer(base64_message, dtype=np.uint8)

                # image = cv2.imdecode(A, 1)

                self.image = A.reshape(240, 320, 4)

                self.image = self.image[:, :, 1:4]
                self.image = self.image[:, :, ::-1]
                self.image = cv2.flip(self.image, 0)

                # image = A.reshape(240, 320, 3)
                # image = image[:, :, 1]
                # image = cv2.flip(image, 0)
                self.flag_new_frame=True
            except:
                pass
            return self.image.copy()
        else:
            self.flag_new_frame=False
            return self.image.copy()
        # return None
        # cv2.putText(image, str(self.fps), (100, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
        # cv2.imshow("Camera", image)
        # cv2.waitKey(1)


class Replicator():
    def __init__(self, block):
        self.block = block

    def power(self, value='on'):
        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)

    def build(self, value, build_position):
        x, y, z = build_position
        self.block.send_command(f"'c':'b', 'v':{value}, 'x':{x}, 'y':{y}, 'z':{z}", flag_garanted_send=True)


class Lamp():
    def __init__(self, block):
        self.block = block

    def power(self, value='on'):
        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)

    def rgb(self, r, g, b, alpha_component=1):
        # r, g, b = color
        self.block.send_command(f"'c':'c', 'r':{r}, 'g':{g}, 'b':{b}, 'a':{alpha_component}", flag_garanted_send=True)



class Drill():
    def __init__(self, block):
        self.block = block

    def power(self, value='on'):
        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)

    # def rgb(self, r, g, b, alpha_component=1):
    #     # r, g, b = color
    #     self.block.send_command(f"'c':'c', 'r':{r}, 'g':{g}, 'b':{b}, 'a':{alpha_component}", flag_garanted_send=True)


class Sensor():
    def __init__(self, block):
        self.block = block
        self.speed = 0
        self.position = {'x': None, 'y': None, 'z': None}
        self.rotation = {'x': None, 'y': None, 'z': None, 'w': None}
        self.velocity = {'x': None, 'y': None, 'z': None}

    def power(self, value='on'):

        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)

    def get_speed(self):
        # if self.block.update_data is not None:
        #     return self.block.update_data["speed"]
        self.ser()
        return self.speed

    def get_position(self):
        # if self.block.update_data is not None:
        #     return self.block.update_data["position"]
        self.ser()
        return self.position

    def get_rotation(self):
        # if self.block.update_data is not None:
        #     return self.block.update_data["rotation"]
        self.ser()
        return self.rotation

    def get_velocity(self):
        # if self.block.update_data is not None:
        #     return self.block.update_data["rotation"]
        self.ser()
        return self.velocity

    # def eulerAngles(self):
    #     if self.block.update_data is not None:
    #         return self.block.update_data["eulerAngles"]

    def ser(self):
        if self.block.update_data is not None:

            # data_bytes = bytearray(self.block.update_data["s"])
            data_bytes = base64.b64decode(self.block.update_data["s"])
            list_f = []
            for i in range(0, len(data_bytes), 4):
                b = data_bytes[i:i + 4]
                f = struct.unpack('f', b)
                list_f.append(f[0])

            self.speed = list_f[0]
            self.position = {'x': list_f[1], 'y': list_f[2], 'z': list_f[3]}
            self.rotation = {'x': list_f[4], 'y': list_f[5], 'z': list_f[6], 'w': list_f[7]}
            self.velocity = {'x': list_f[8], 'y': list_f[9], 'z': list_f[10]}
            # return
            self.block.update_data = None


class Container():
    def __init__(self, block):
        self.block = block
        self.__content()

    def power(self, value='on'):
        # time.sleep(0.01)
        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)
        # time.sleep(0.01)

    def __content(self):
        self.block.send_command(f"'c':'l'", flag_garanted_send=True)

    def items(self):
        if self.block.update_data is not None:
            if "items" in self.block.update_data:
                return self.block.update_data["items"]
        return []
class Radar():
    def __init__(self, block):
        self.block = block
        self.__content()

    def power(self, value='on'):
        # time.sleep(0.01)
        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)
        # time.sleep(0.01)

    def __content(self):
        self.block.send_command(f"'c':'l'", flag_garanted_send=True)

    def items(self):
        if self.block.update_data is not None:
            if "items" in self.block.update_data:
                return self.block.update_data["items"]
        return []


class ConnectorBlock():
    def __init__(self, block):
        self.block = block

    def power(self, value='on'):
        # time.sleep(0.01)
        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)
        # time.sleep(0.01)

    def drop_all(self):
        self.block.send_command(f"'c':'a'", flag_garanted_send=True)


class ProgramBlock():
    def __init__(self, block):
        self.block = block
        # self.__content()

    def power(self, value='on'):
        # time.sleep(0.01)
        self.block.send_command(f"'c':'{value}'", flag_garanted_send=True)
        # time.sleep(0.01)

    # def __content(self):
    #     self.block.send_command(f"'c':'l'", flag_garanted_send=True)

    def send_file(self, value='fa', filename="main.py", data=b'print("hello")'):
        # time.sleep(0.01)
        self.block.send_command(f"'c':'{value}','n':'{filename}','d':'{data}'", flag_garanted_send=True)
        # time.sleep(0.01)

    def start_script(self):
        print("send start ", self.block.id)
        self.block.send_command(f"'c':'start','n':'','d':''", flag_garanted_send=True)
        pass
    # def stop_script(self):
    #     self.block.send_command(f"'c':'stop','n':'','d':''", flag_garanted_send=True)
    #     pass


class Grid():
    def __init__(self, data, connector):
        self.raw_data = data
        self.id = self.raw_data['id']
        self.name = self.raw_data['name']
        self.blocks = {}
        self.connector = connector

        for block_dict in self.raw_data['blocks']:
            new_block = Block(block_dict, self.connector)
            self.blocks[new_block.id] = new_block

    def get_block_by_name(self, name_block, connector=None):
        for block_id in self.blocks:
            if self.blocks[block_id].name == name_block:
                # if connector is not None:
                #     self.blocks[block_id].connector = connector
                # print(self.blocks[block_id].name)
                return self.blocks[block_id]


import win32api
import win32gui
# import os


class base_robot():
    # @staticmethod
    def get_keys(self):
        list_pressed = []
        for i in range(1, 256):
            if win32api.GetAsyncKeyState(i):
                list_pressed.append(i)
        return list_pressed

    @staticmethod
    def get_mouse():
        flags, hcursor, z = win32gui.GetCursorInfo()
        x, y = z[0], z[1]
        return x, y
    @staticmethod
    def sleep(timer):

        t = time.time()+timer/1000
        while 1:
            cv2.waitKey(1)
            if time.time()>t:
                break

        # time.sleep(timer/1000)

    # @staticmethod
    # def clear_screen():
    #     os.system('cls' if os.name == 'nt' else 'clear')

class UnityAPI():
    def __init__(self, back_plane_ip_address=None):
        # self.server_adress = socket.gethostbyname(socket.gethostname())
        if back_plane_ip_address is None:
            # self.connector = Connector()
            self.connector = ConnectorDirect()
        else:
            # self.connector = Connector(back_plane_ip_address)
            self.connector = ConnectorDirect(back_plane_ip_address)

        self.connector.incoming_message_processing = self.incoming_message_processing

        self.grids = []
        self.grids_raw = {}
        self.flag_good_connection = False
        self.connector.send_to_unity(-1, "AllGrids", True)
        timer = time.time() + 8
        timer_connect = time.time()+1
        print("Try Connect to Simulator...", end="")
        while not self.flag_good_connection:
            time.sleep(0.0001)

            if time.time() > timer_connect:
                self.connector.send_to_unity(-1, "AllGrids", True)
                timer_connect = time.time() + 1
                print(".", end="")

            if time.time() > timer:
                print("")
                print("simulatorAPI: No Unity Answer! Start Simulator first")
                timer = time.time() + 8

        my_thread_receive = threading.Thread(target=self.direct_video_work)
        my_thread_receive.daemon = True
        my_thread_receive.start()

        print("Connect to Simulator OK")
        # break

    def direct_video_work(self):

        self.mySocket_video = socket.socket()
        self.mySocket_video.connect((IP, 9092))
        while 1:
            try:
                byte_frame = self.mySocket_video.recv(500000)

                id_camera = struct.unpack('i', byte_frame[0:4])[0]
                # print("id", id_camera)
                byte_frame = byte_frame[4:]

                # A = np.frombuffer(byte_frame, dtype=np.uint8)
                # image = A.reshape(240, 320, 4)
                # image = image[:, :, 1:4]
                # image = image[:, :, ::-1]
                # image = cv2.flip(image, 0)

                for grid in self.grids:
                    if id_camera in grid.blocks:
                        # print(payload)
                        grid.blocks[id_camera].update_data_from_server(byte_frame)
                        break


            except Exception as e:
                pass
                # print(e)
            #     self.mySocket_video = socket.socket()
            #     self.mySocket_video.connect((BANYAN_IP, 9092))

    def incoming_message_processing(self, topic, payload):
        # print(payload)
        if payload["s"] == '-1':
            if self.flag_good_connection is False:

                if payload["a"] == "AllGrids":

                    self.grids_raw = payload["m"]["grids"]
                    # print(self.grids_raw)
                    # print("My Grids:")
                    for grid_dict in self.grids_raw:
                        # print(grid_dict["name"])
                        new_grid = Grid(grid_dict, self.connector)

                        self.grids.append(new_grid)

                        # for block_dict in grid_dict['blocks']:
                        #     print(block)
                        #     block = Block(block_dict)
                    self.flag_good_connection = True

        else:
            id = base64.b64decode(payload["s"])
            id = struct.unpack('i', id)[0]
            for grid in self.grids:
                if id in grid.blocks:
                    # print(payload)
                    grid.blocks[id].update_data_from_server(payload["m"])
                    break

    def get_grids_names(self):
        names = []
        for grid in self.grids:
            names.append(grid.name)
        return names

    def get_robot(self, name):
        for grid in self.grids:
            if grid.name == name:
                return grid

    def make_cv_robot(self, name="Robot"):
        data = self.get_robot(name)
        robot = RobotCV(data, name=name)
        return robot

    def make_car_robot(self, name="Robot"):
        data = self.get_robot(name)
        robot = CarCV(data, name=name)
        return robot



class RobotCV(base_robot):
    def __init__(self, car, name):
        self.name = name

        self.wheelFR = Wheel(car.get_block_by_name("WheelRootFR"))
        self.wheelFL = Wheel(car.get_block_by_name("WheelRootFL"))
        self.wheelBR = Wheel(car.get_block_by_name("WheelRootBR"))
        self.wheelBL = Wheel(car.get_block_by_name("WheelRootBL"))
        self.camera = Camera(car.get_block_by_name("CameraBlock"))
        self.sensor = Sensor(car.get_block_by_name("SensorBlock"))
        self.lamp = Lamp(car.get_block_by_name("Lamp"))
        self.rotor0 = Rotor(car.get_block_by_name("Rotor"))

        self.drill = None

        try:
            self.drill = Drill(car.get_block_by_name("Drill"))
        except:
            pass
        self.container = None
        try:
            self.container = Container(car.get_block_by_name("Container"))
            # self.container.content()
        except:
            pass
        self.connector1 = None
        try:
            self.connector1 = ConnectorBlock(car.get_block_by_name("Connector"))
            self.connector1.power("on")
            # self.container.content()
        except:
            pass
        self.comp = None
        try:
            self.comp = ProgramBlock(car.get_block_by_name("ProgramBlock"))
            # self.container.content()
        except:
            pass
        self.radar = None
        try:
            self.radar = Radar(car.get_block_by_name("Radar"))
            # self.container.content()
        except:
            pass

        self.on_all()

    def on_all(self):
        self.wheelFR.power("on")
        self.wheelFL.power("on")
        self.wheelBR.power("on")
        self.wheelBL.power("on")

        self.camera.power("on")
        self.sensor.power("on")
        if self.radar is not None:
            self.radar.power()
        self.sleep(50)


    def move(self, left, right, timer=None, wait=False):
        if timer is None:
            timer=100
        else:
            wait=True
        self.wheelFR.move(right, timer, garanted_send=wait)
        self.wheelBR.move(right, timer, garanted_send=wait)

        self.wheelFL.move(left, timer, garanted_send=wait)
        self.wheelBL.move(left, timer, garanted_send=wait)
        if wait:
            time.sleep(timer/1000)



    def brake(self, left, right, timer=None, wait=False):
        if timer is None:
            timer=100
        else:
            wait=True
        self.wheelFR.brake(right, timer, garanted_send=wait)
        self.wheelBR.brake(right, timer, garanted_send=wait)
        self.wheelFL.brake(left, timer, garanted_send=wait)
        self.wheelBL.brake(left, timer, garanted_send=wait)

        if wait:
            time.sleep(timer / 1000)


class CarCV():
    def __init__(self, car, name):
        self.name = name

        self.wheelFR = Wheel(car.get_block_by_name("WheelRootFR"))
        self.wheelFL = Wheel(car.get_block_by_name("WheelRootFL"))
        self.wheelBR = Wheel(car.get_block_by_name("WheelRootBR"))
        self.wheelBL = Wheel(car.get_block_by_name("WheelRootBL"))
        self.camera = Camera(car.get_block_by_name("CameraBlock"))
        self.sensor = Sensor(car.get_block_by_name("SensorBlock"))
        self.lamp = Lamp(car.get_block_by_name("Lamp"))
        # self.rotor0 = Rotor(car.get_block_by_name("Rotor"))

        self.on_all()

    def on_all(self):
        self.wheelFR.power("on")
        self.wheelFL.power("on")
        self.wheelBR.power("on")
        self.wheelBL.power("on")

        self.camera.power("on")
        self.sensor.power("on")

    def turn(self, angle):
        self.wheelFR.angle(angle)
        self.wheelFL.angle(angle)

    def move(self, throttle, time=100):
        self.wheelBR.move(throttle, time)
        self.wheelBL.move(throttle, time)

    def brake(self, power, time=100):
        self.wheelFR.brake(power, time)
        self.wheelBR.brake(power, time)

        self.wheelFL.brake(power, time)
        self.wheelBL.brake(power, time)

    # def get_keys(self):
    #     return self.get_keys()

if __name__ == "__main__":
    print("")
    print("Use simulatorAPI ONLY AS LIBRARY!")
