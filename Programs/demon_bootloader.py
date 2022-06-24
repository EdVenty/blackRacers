import asyncio

import os
import pty

import time

import fcntl



dir = "/home/pi/robot/"
# orange
# dir = "/root/robot/"

flag_stop = False
console_out = ""

myhost = os.uname()[1]
if myhost.find("ras") == 0:
    dir = "/home/pi/robot/"
else:
    dir = "/root/robot/"


def set_nonblocking(file_handle):
    """Make a file_handle non-blocking."""
    global OFLAGS
    OFLAGS = fcntl.fcntl(file_handle, fcntl.F_GETFL)
    nflags = OFLAGS | os.O_NONBLOCK
    fcntl.fcntl(file_handle, fcntl.F_SETFL, nflags)


master, slave = pty.openpty()
set_nonblocking(master)


async def main():
    global console_out, proc, master_ip, filename

    filename = "demon_starter.py"
    print("Bootloader work", filename)
    asyncio.ensure_future(run_subprocess())

    await asyncio.sleep(3)

    while True:
        try:
            # print(proc)

            if proc==False:
                asyncio.ensure_future(run_subprocess())
                await asyncio.sleep(0.001)

            # asyncio.sleep(0.001)
            await asyncio.sleep(0.01)
            if proc:
                if len(console_out) == 0:
                    if proc.returncode == None:
                        asyncio.ensure_future(run_subprocess_read())

            if len(console_out) > 0:
                print (console_out)
            console_out=""
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
                # s = str(os.read(master, 4096).decode("utf-8"))
                s = str(os.read(master, 65536).decode("utf-8"))

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
        console_out += str(os.read(master, 65536).decode("utf-8"))
    except BlockingIOError:
        pass

    proc = False
    print("END proc")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()  # prevents annoying signal handler error