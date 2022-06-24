import asyncio
import json
import os
import pty
# import socket
import time
from threading import Thread
import fcntl
import numpy as np
import zmq
import zlib
import base64
import subprocess
import pickle
import RPi.GPIO as GPIO

import InetConnection as InetConnection

# 18.05.2018

pause_reqest = 0.05
myhost = os.uname()[1]

master_ip = "0"
OFLAGS = None

os.system('sudo modprobe bcm2835-v4l2')


def set_nonblocking(file_handle):
    """Make a file_handle non-blocking."""
    global OFLAGS
    OFLAGS = fcntl.fcntl(file_handle, fcntl.F_GETFL)
    nflags = OFLAGS | os.O_NONBLOCK
    fcntl.fcntl(file_handle, fcntl.F_SETFL, nflags)


master, slave = pty.openpty()
set_nonblocking(master)

port = "5557"

context = zmq.Context(1)
socket = context.socket(zmq.REP)
socket.setsockopt(zmq.SNDTIMEO, 1000)
socket.setsockopt(zmq.RCVTIMEO, 1000)

socket.bind("tcp://*:%s" % port)
flag_stop = False
console_out = ""
proc = False
filename = ""
# raspberry
dir = "/home/pi/robot/"
# orange
# dir = "/root/robot/"

if myhost.find("ras") == 0:
    dir = "/home/pi/robot/"
else:
    dir = "/root/robot/"

frame_byte = np.array([[10, 10], [10, 10]], dtype=np.uint8)
frame_json = ""
flag_stopt_video = False
keypress = ""
flag_video_demon_work = False
flag_key_demon_work = False

pass_hash = ""
try:
    file = open(dir + "password", "r+")
    pass_hash = file.readline()
    file.close()
except:
    pass
print("pass hash (", pass_hash, ")")


def key_to_robot():
    global keypress, flag_stopt_key, flag_key_demon_work
    # видео клиент. берет кадры с запущенного робота

    # while 1:
    #     if proc:
    #         break
    flag_key_demon_work = True
    context_key = zmq.Context(1)
    socket_key = context_key.socket(zmq.REQ)
    # socket_key.setsockopt(zmq.SNDTIMEO, 100)
    # socket_key.setsockopt(zmq.RCVTIMEO, 100)

    socket_key.connect("tcp://127.0.0.1:5559")
    # flag_stopt_key = False
    print("START KEY DEMON")
    flag_stopt_key = False
    sleep_pause = 0.01
    timer_work = time.time() + 5
    while 1:
        # try:

        if flag_stopt_key == True or time.time() - timer_work > 0:
            # flag_stopt_key=False
            print("STOP KEY DEMON")
            break
        if keypress != "":
            timer_work = time.time() + 5
            while 1:
                f = 0
                try:
                    socket_key.send_string(keypress, zmq.NOBLOCK)  # zmq.NOBLOCK
                    # print("send key", keypress, time.time())
                    f = 1
                    keypress = ""
                except zmq.ZMQError as e:
                    if e.errno == zmq.ETERM:
                        # print("error1", e)
                        pass
                if f == 1:
                    break
                else:
                    time.sleep(sleep_pause)

                if time.time() - t > 1:
                    break
            message_s = ""
            t = time.time()
            while 1:
                f = 0
                try:
                    message_s = socket_key.recv_string(zmq.NOBLOCK)
                    f = 1
                except zmq.ZMQError as e:
                    if e.errno == zmq.ETERM:
                        pass
                        # print("error2", e)
                if message_s != "" or f == 1:
                    break
                if time.time() - t > 1:
                    time.sleep(sleep_pause)
                    break
                time.sleep(sleep_pause)

        else:
            time.sleep(sleep_pause)

    flag_key_demon_work = False


def video_from_robot():
    global frame_byte, frame_json, flag_stopt_video, flag_video_demon_work
    # видео клиент. берет кадры с запущенного робота

    context_video = zmq.Context(1)
    socket_video = context_video.socket(zmq.REQ)
    # socket_video.setsockopt(zmq.SNDTIMEO, 100)
    # socket_video.setsockopt(zmq.RCVTIMEO, 100)

    socket_video.connect("tcp://127.0.0.1:5555")

    flag_stopt_video = False
    flag_video_demon_work = True
    print("START VIDEO DEMON")
    last_frame = np.ones((480, 640, 3), dtype=np.uint8)
    frame_json = dict(
        # arrayname="jpg",
        dtype=str(last_frame.dtype),
        shape=last_frame.shape,
    )
    # cv2.putText(last_frame, str("Wait image from robot..."),
    #             (self.last_frame.shape[1] // 8, self.last_frame.shape[0] // 2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2,
    #             (255, 255, 255), 2)
    while 1:

        if flag_stopt_video == True:
            # flag_stopt_video = False
            frame_byte = np.zeros_like(frame_byte)
            print("STOP VIDEO DEMON")
            flag_video_demon_work = False
            break

        try:
            socket_video.send_string("|", zmq.NOBLOCK)  # zmq.NOBLOCK
        except:
            # print("error0")
            pass
        md = ""
        t = time.time()
        while 1:

            try:
                md = socket_video.recv_json(zmq.NOBLOCK)
            except zmq.ZMQError as e:
                # time.sleep(0.001)
                # print("error1",ee)
                # ee+=1
                pass
            if md != "":
                break
            else:
                time.sleep(0.001)
            if time.time() - t > 0.1:
                # print("break video")
                break

        if md != "":
            msg = 0
            t = time.time()
            while 1:
                try:
                    msg = socket_video.recv(zmq.NOBLOCK)
                except:
                    pass
                    # print("error2")
                if msg != 0:
                    break
                if time.time() - t > 0.1:
                    # print("break video")
                    break

            try:
                frame_json = md
                frame_byte = msg
                time_frame = time.time()
            except:
                pass
        else:
            time.sleep(0.001)

        # try:
        #     print("try")
        #     socket_video.send_string("|", zmq.NOBLOCK)
        #     frame_json = socket_video.recv_json(0)
        #     if frame_json != None:
        #         frame_byte = socket_video.recv(0)
        #         print(frame_json, len(frame_byte))
        #     else:
        #         time.sleep(0.01)
        # except Exception as e:
        #     print("video error",e)
        #     pass


def udp_work_comand():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = ''

    server_address = (host, 4999)
    sock.bind(server_address)

    # клиент к демону
    context_inet1 = zmq.Context(1)
    socket_udp = context_inet1.socket(zmq.REQ)
    # socket_inet.setsockopt(zmq.SNDTIMEO, 1000)
    # socket_inet.setsockopt(zmq.RCVTIMEO, 100)

    socket_udp.connect("tcp://127.0.0.1:%s" % port)
    # flag_no_data = False
    while 1:
        try:
            data, address = sock.recvfrom(65507)

            # data = data.decode('utf-8').split("|")
            # data = data.decode('utf-8').split("|")

            if data[0] == ord("s"):
                print("UDP stop")
                socket_udp.send_string("stop")
                answ = socket_udp.recv_string()
                time.sleep(1)
                socket_udp.send_string("data")
                answ = socket_udp.recv_string()
                if len(answ) > 0:
                    print(answ)
                    sock.sendto(answ.encode('utf-8'), address)


            elif data[0] == ord("r"):
                d = pickle.loads(zlib.decompress(data[1:]))
                print("UDP", "run|" )

                socket_udp.send_string("run|" + d)
                answ = socket_udp.recv_string()
                # flag_no_data = True


            # elif data[0] == ord("f"):
            #     d = pickle.loads(zlib.decompress(data[1:]))
            #     print("UDP", "file|" + d)
            #     socket_udp.send_string("file|" + d)
            #     answ = socket_udp.recv_string()
            #     flag_no_data = False
            #
            # elif data[0] == ord("g"):
            #     d = pickle.loads(zlib.decompress(data[1:]))
            #     print("UDP", "start|" + d)
            #     socket_udp.send_string("start|" + d)
            #     answ = socket_udp.recv_string()
            #     flag_no_data = True
            #     socket_udp.send_string("data")
            #     answ = socket_udp.recv_string()

            elif data[0] == ord("d"):
                print("UDP file data", len(data))
                d = pickle.loads(zlib.decompress(data[1:]))
                socket_udp.send(zlib.compress(d, 1))
                answ = socket_udp.recv_string()
                # flag_no_data = True

            elif data[0] == ord("t"):
                # print("UDP take", flag_no_data)
                # if flag_no_data:
                # t = time.time()
                socket_udp.send_string("data")
                answ = socket_udp.recv_string()
                if len(answ) > 0:
                    print(answ)
                    sock.sendto(answ.encode('utf-8'), address)
                # print("UDP console", time.time()-t, len(data))

            time.sleep(0.0001)
        except Exception as e:
            print(e)


def inet_work():
    global socket, filename, proc, myhost, frame_byte, frame_json, flag_stopt_video, keypress, flag_video_demon_work, flag_stopt_key
    global pause_reqest

    ic = InetConnection.InetConnect(myhost, "robot")
    ic.connect()
    lime_last_video_req = 0

    # клиент к демону
    context_inet = zmq.Context(1)
    socket_inet = context_inet.socket(zmq.REQ)
    # socket_inet.setsockopt(zmq.SNDTIMEO, 1000)
    # socket_inet.setsockopt(zmq.RCVTIMEO, 100)

    socket_inet.connect("tcp://127.0.0.1:%s" % port)

    pause = 0.5
    pause_reqest = pause
    last_message = ""
    print("Start Inet Work")
    while 1:
        try:
            answer = ic.take_answer()
            # time.sleep(0.1)
            if len(answer) == 0:
                time.sleep(pause)
                continue
            # if answer[0]!="0":
            #     print("in", answer, time.time())

            elif int(answer[0]) > -1:
                if time.time() > lime_last_video_req + 1:
                    pause_reqest = pause

                # print("Start file from inet", answer)
                # пришел запрос, надо ответить
                if len(answer) < 2:
                    time.sleep(pause_reqest)
                    continue

                message = answer[1].split("|")

                last_message = message[0]
                if message[0] == "":
                    if last_message == "":
                        time.sleep(pause_reqest)
                    continue
                if pass_hash != "":
                    if pass_hash != message[-1]:
                        print("wrong pass", answer)
                        ic.send_to(answer[0], "|WRONG PASSWORD")
                        # time.sleep(1)
                        continue

                # print("inet_message", message)

                if message[0] == "start":
                    print("Start", message[1])

                    # if flag_key_demon_work==False:
                    #     my_thread_key = Thread(target=key_to_robot)
                    #     my_thread_key.daemon = True
                    #     my_thread_key.start()

                    # посылаем данные консоли
                    filename = message[1]
                    try:
                        socket_inet.send_string("start|" + filename)
                        answ = socket_inet.recv_string()
                        ic.send_to(answer[0], answ)
                    except:
                        pass
                    continue

                if message[0] == "stop":
                    print("Stop")
                    flag_stopt_video = True
                    # посылаем данные консоли
                    try:
                        socket_inet.send_string("stop")
                        answ = socket_inet.recv_string()
                        print(answ)
                        ic.send_to(answer[0], answ)
                        flag_stopt_key = True
                    except:
                        pass
                    continue

                if message[0] == "d":
                    # print("Data inet")
                    # посылаем данные консоли

                    socket_inet.send_string("data")
                    answ = socket_inet.recv_string()
                    # print(answ)
                    if answ != "":
                        ic.send_to(answer[0], answ)
                    continue

                if message[0] == "file":
                    print("File inet size", len(message[2]))
                    # посылаем данные консоли
                    try:
                        socket_inet.send_string("file|" + message[1])
                        answ = socket_inet.recv_string()
                        # socket_inet.send(message[2].encode('utf-8'))
                        try:
                            socket_inet.send(zlib.compress(zlib.decompress(base64.b64decode(message[2]))), 1)
                        except:
                            print("error compress inet")
                            pass

                        answ = socket_inet.recv_string()
                        print("anser inet file", answ)
                        print(answ)
                        ic.send_to(answer[0], message[1])
                    except:
                        pass
                    continue

                if message[0] == "run":
                    print("Run file")
                    flag_stopt_video = True
                    while flag_video_demon_work:
                        flag_stopt_video = True
                        print("stop video demon", flag_stopt_video)
                        time.sleep(0.01)

                    socket_inet.send_string("run|" + str(message[1]))
                    answ = socket_inet.recv_string()

                    print("Started", answ)
                    ic.send_to(answer[0], answ)
                    if flag_video_demon_work == False:
                        my_thread_video = Thread(target=video_from_robot)
                        my_thread_video.daemon = True
                        my_thread_video.start()

                    # flag_stopt_video = False

                    continue

                if message[0] == "p":
                    # print('flag_video_demon_work',flag_video_demon_work)

                    if flag_video_demon_work == False:
                        my_thread_video = Thread(target=video_from_robot)
                        my_thread_video.daemon = True
                        my_thread_video.start()
                    # flag_stopt_video = False
                    # print("frame inet")
                    # забираем кадр
                    # print(frame_json)
                    # convert to string

                    frame_json_str = json.dumps(frame_json)
                    # load to dict
                    # my_dict = json.loads(input)
                    # ic.send_to(answer[0], "1")
                    # print("send bytes", frame_json_str, len(frame_byte))
                    ic.send_bytes_to(answer[0], frame_json_str, frame_byte)
                    lime_last_video_req = time.time()
                    pause_reqest = 0.001
                    continue
                if message[0] == "startvideo":
                    print("Start video")
                    # посылаем данные консоли
                    if flag_video_demon_work == False:
                        my_thread_video = Thread(target=video_from_robot)
                        my_thread_video.daemon = True
                        my_thread_video.start()

                    ic.send_to(answer[0], "|start_video")
                    continue
                if message[0] == "stopvideo":
                    print("Stop video")
                    # посылаем данные консоли
                    # flag_stopt_video = True
                    # ic.send_to(answer[0], "|stop_video")
                    continue

                if message[0] == "k":
                    # print("Send keqy")
                    if flag_key_demon_work == False:
                        my_thread_key = Thread(target=key_to_robot)
                        my_thread_key.daemon = True
                        my_thread_key.start()
                        time.sleep(0.01)

                    try:
                        keypress = message[1]
                        # print(time.time(), keypress)
                    except:
                        pass
                    # посылаем данные консоли
                    # ic.send_to(answer[0], "1")
                    continue
                if message[0] == "pause":
                    print("Send keqy")
                    pause = float(message[1])
                    # посылаем данные консоли
                    # ic.send_to(answer[0], "1")
                    continue
                if message[0] == "ip":
                    print("IP")
                    host_ip = subprocess.check_output(['hostname', '-I'])
                    print("Send IP", host_ip)
                    ic.send_to(answer[0], "|ip|" + str(host_ip))

                    continue
                if message[0] == "0" or message[0] == 0:
                    time.sleep(0.01)

                    continue

                # ic.send_to(answer[0], "wrong_packet")

            if int(answer[0]) == -1:
                print("registration")
                ic.registration()


        except Exception as E:
            print(E)
            time.sleep(0.05)
            pass


def test_wifi():
    count_fail = 0
    time.sleep(60 * 10)
    while 1:
        # print("test wifi")
        try:
            subprocess.call(['/home/pi/robot/wifi_reconnect.sh'])
        except:
            pass

        # test connection and reset
        wifi_ip = subprocess.check_output(['hostname', '-I'])
        # print(wifi_ip)
        if wifi_ip is not None:
            # print(wifi_ip)
            count_fail = 0
        else:
            count_fail += 1

        if count_fail > 3:
            # os.system('sudo shutdown -r now')
            os.system('sudo reboot')
        time.sleep(60)


my_thread_udp = Thread(target=udp_work_comand)
my_thread_udp.daemon = True
my_thread_udp.start()

my_thread_inet = Thread(target=inet_work)
my_thread_inet.daemon = True
my_thread_inet.start()

my_thread_wifi = Thread(target=test_wifi)
my_thread_wifi.daemon = True


# my_thread_wifi.start()


def decompress(obj):
    res = True
    file_data = b''
    try:
        print("dec data", obj)
        file_data = zlib.decompress(obj)
    except:
        print("error decompress")
        res = False
        exit(0)
    return res, file_data


async def main():
    global console_out, proc, master_ip, filename
    # time_start =time.time()

    filename = "/autostart.py"
    print("Autostart file", filename)
    asyncio.ensure_future(run_subprocess())
    await asyncio.sleep(0.001)

    # process = asyncio.create_subprocess_exec(*["python3", "print1.py"], stdout=slave)
    #            print("start", process.returncode)

    flag_file = False
    # filename = ""
    print("Start demon")
    while True:
        try:
            # if time.time() - time_start>10:
            #     exit(0)
            #  Wait for next request from client

            if flag_file:
                # print("wait file data")
                t = time.time()
                message = ""
                while 1:
                    try:
                        message = socket.recv()
                    except:
                        pass
                    if message != "":
                        break
                    if time.time() - t > 10:
                        break

                # message = message.decode("utf-8")

                # print("filename", filename)
                # print("file", message)
                # message = zlib.decompress(message)

                flag_file = False
                if message == "":
                    print("bad file")
                    continue
                flag_save_file = False
                # try:
                # zlib.crc32()
                flag_save_file, file_data = decompress(message)
                # file_data = zlib.decompress(message)
                # flag_save_file=True
                # except:
                #     print("error compress")
                #     # socket.send_string("-1")
                #     # continue
                # print("save file")
                if flag_save_file:
                    text_file = open(dir + filename, "wb")
                    text_file.write(file_data)
                    text_file.close()

                try:
                    socket.send_string("|file_saved")
                except:
                    pass
                print("continue")
                # continue

            message = ""
            try:
                message = socket.recv_string(zmq.NOBLOCK)
            except:
                pass
            # print("mess",message)
            # if len(message) > 0:
            #     print("Received request: %s" % message)

            if message == "":
                # time.sleep(0.02)
                time.sleep(pause_reqest)
                # print(pause_reqest)
                # print("message empty")
                continue
            await asyncio.sleep(0.001)
            # time.sleep(0.001)
            # print("message", message)
            message = message.split("|")

            if message[0].find("data") >= 0:
                snd = "|STOPED "
                if proc:
                    if len(console_out) == 0:
                        if proc.returncode == None:
                            # print(console_out)
                            asyncio.ensure_future(run_subprocess_read())
                            # print(console_out)
                            snd = console_out

                if len(console_out) > 0:
                    snd = console_out
                    # print(len(console_out))
                    # if len(console_out) < 1024:
                    #    await asyncio.sleep(0.1)
                # print("send: "+snd)
                try:
                    socket.send_string(snd)
                except:
                    pass
                console_out = ""
                continue

            if message[0].find("stop") >= 0:
                # print("stop")

                if proc:
                    if proc.returncode == None:
                        # print("k1", proc.returncode)
                        asyncio.ensure_future(run_subprocess_read())
                        proc.kill()
                        # await asyncio.sleep(2)
                        while proc:
                            await asyncio.sleep(0.05)
                        # print("k2",proc.returncode)

                console_out_summ = ""



                # while len(console_out)>0:
                #     print("len", len(console_out))
                #     console_out_summ+=console_out
                #     print(console_out)
                #     console_out=""
                #     time.sleep(0.001)
                #
                try:
                    socket.send_string(console_out + "\r\n|STOPED ")
                    # socket.send_string("|STOPED ")
                except:
                    pass
                console_out = ""

                proc = False
                print("stoping", console_out)

                #clear buff
                t = time.time()
                while 1:
                    f = 0
                    try:
                        s = str(os.read(master, 4096).decode("utf-8"))
                        print("clear", s)
                    except BlockingIOError:
                        f = 1

                    if time.time() - t > 1 or f == 1:
                        break
                continue
                # break
            elif message[0].find("ping") >= 0:
                try:
                    socket.send_string("|" + myhost + "|" + master_ip)
                except:
                    pass
                continue

            elif message[0].find("take") >= 0:
                # назначаем хозяина
                master_ip = message[1]
                print("take", master_ip)
                try:
                    socket.send_string("|take|" + myhost + "|" + master_ip)
                except:
                    pass
                continue

            elif message[0].find("drop") >= 0:
                # скидываем хозяина]
                master_ip = "0"
                print("drop", master_ip)
                try:
                    socket.send_string("|drop|" + myhost + "|" + master_ip)
                except:
                    pass
                continue

            elif message[0].find("file") >= 0:
                # принимаем файл
                print("filename", filename)

                filename = message[1]

                try:
                    socket.send_string("|filename|" + filename)
                except:
                    pass
                # await asyncio.sleep(0.01)
                flag_file = True
                # print("zagolovok prinat")
                continue

            elif message[0].find("start") >= 0:
                #            flag_stop = False

                console_out = ""
                filename = message[1]
                print("start file", filename)
                if proc == False:
                    asyncio.ensure_future(run_subprocess())
                    print("start ok")
                    try:
                        socket.send_string("|start|ok")
                    except:
                        pass
                else:
                    print("already run")
                    try:
                        socket.send_string("|start|already run")
                    except:
                        pass
                #            process = asyncio.create_subprocess_exec(*["python3", "print1.py"], stdout=slave)
                #            print("start", process.returncode)
                continue

            elif message[0].find("exit") >= 0:
                print("exit")
                break

            elif message[0].find("run") >= 0:
                print("run")

                if proc:
                    if proc.returncode == None:
                        asyncio.ensure_future(run_subprocess_read())
                        proc.kill()
                        while proc:
                            await asyncio.sleep(0.001)

                t=time.time()
                while 1:
                    f=0
                    try:
                        s=str(os.read(master, 4096).decode("utf-8"))
                        print("clear",s)
                    except BlockingIOError:
                        f=1

                    if time.time() - t > 1 or f==1:
                        break
                console_out = ""
                # flag_save_file, file_data = decompress(message)
                #
                # if flag_save_file:
                #     text_file = open(dir + filename, "wb")
                #     text_file.write(file_data)
                #     text_file.close()
                # print(message)
                b = base64.b64decode(message[1].encode('utf-8'))
                data = pickle.loads(zlib.decompress(b))
                # print(data)

                text_file = open(dir + data["filename"], "wb")
                text_file.write(data["data"])
                text_file.close()

                filename = data["filename"]
                asyncio.ensure_future(run_subprocess())
                print("start ok")

                socket.send_string("|run|" + data["filename"])
                continue
        except:
            pass


async def run_subprocess_read():
    global proc, console_out
    if proc:
        if proc.returncode == None:
            # s = stdout.readline()
            # print("read..")
            s = ""
            try:
                # return 1-n bytes or exception if no bytes
                # s = str(os.read(master, 1024))
                # s = str(os.read(master, 1024).decode("utf-8"))
                s = str(os.read(master, 4096).decode("utf-8"))

            except BlockingIOError:
                # sys.stdout.write('no data read\r')
                #   print("block")
                pass

            # print("..ok")
            # if s.find("EXIT")>=0:
            #     print("end of programm")
            #     proc=False
            console_out += s
            return s

cleanup_keys = {
    "HIGH": GPIO.HIGH,
    "LOW": GPIO.LOW,
    "OUT": GPIO.OUT
}

async def run_subprocess():
    global proc, slave, console_out, filename
    print('Starting subprocess', dir + filename)
    proc = await asyncio.create_subprocess_exec(
        # 'python3', 'print1.py', stdout=slave, stderr=slave)
        'python3', dir + filename, stdout=slave, stderr=slave)
    # 'python3', 'robot_keras2.py', stdout = slave, stderr = slave)
    # 'python3', 'manual_client.py', stdout = slave, stderr = slave)
    # 'python3', 'robot_keras.py', stdout=slave, stderr=slave)

    # 'python3', 'print1.py', stdout=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    try:
        console_out += str(os.read(master, 4096).decode("utf-8"))
    except BlockingIOError:
        pass

    proc = False
    print("END proc")
    with open("./cleanup.json", 'r', encoding='utf-8') as file:
        GPIO.setmode(GPIO.BCM)
        cleanup = json.loads(file.read())
        for pin in cleanup["pins"]:
            pin_int = int(pin)
            GPIO.setup(pin_int, cleanup_keys[cleanup["pins"][pin]["type"]])
            GPIO.output(pin_int, cleanup_keys[cleanup["pins"][pin]["low"]])
    GPIO.cleanup()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()  # prevents annoying signal handler error
