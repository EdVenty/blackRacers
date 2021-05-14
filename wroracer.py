import cv2
import numpy as np
import time
import RobotAPI as rapi
import json
import regulators

robot = rapi.RobotAPI(flag_pyboard=True)
robot.set_camera(60, 640, 480, 0, 0)
############################################################
# flag_qualification=True


# global_speed = 115
# global_speed = 60
global_speed = 120 #130 USE IT FUCK # 120
pause_finish = 1.3
count_lines_proverka = 0

# пременные порога черной линии
# porog_black_line_minus = 250  #LIme
porog_black_line_minus = 300  #Black
# porog_black_line_minus = 285
# porog_black_line_plus = 300 #Lime
porog_black_line_plus = 300 #Black

flag_qualification = False
# flag_qualification = True
if flag_qualification:
    global_speed += 65
    pause_finish = 0.3
    porog_black_line_plus+=30  # по часовой стрелке
    porog_black_line_minus+=30   # против



delta_green_plus = 8
delta_red_plus = -8

delta_green_minus = 8
delta_red_minus = -8
time_go_back_banka = 380

# global_speed = 0


# state = "Main move"
state = "Manual move"
# state = "Main move"
# state = "HSV"

pause_povorot = 0.8 #0.8 SEC 0.6 sec the qula



timer_finish = None
############################################################

# 1- по часовой, -1 против часовой стрелки
speed_manual = global_speed
direction = 0
manual_angle = 0
manual_throttle = 0


# low_orange = np.array([0, 50, 80])
# up_orange = np.array([50, 256, 256])
#
# # черный
# low_black = np.array([0, 0, 0])
# up_black = np.array([180, 256, 89])
#
# low_blue = np.array([90, 0, 0])
# up_blue = np.array([120, 256, 170])

class HSV_WORK(object):
    """Work whith hsv colors"""
    colors = {}

    def reset(self):

        # print(self.colors)
        self.colors = {
            'orange': [[0, 50, 80], [50, 256, 256]],
            # 'red_low': [[0, 0, 212], [31, 256, 256]],
            #     # 'black_TL': [[0, 0, 0], [256, 256, 86]],
            #     # 'red_STOP_low': [[0, 0, 66], [20, 256, 256]],
            'black': [[0, 0, 0], [180, 256, 89]],
            'green': [[51, 50, 70], [84, 256, 256]],
            'white': [[0, 0, 81], [255, 256, 254]],
            'blue': [[90, 0, 0], [120, 256, 170]],
            #     # 'red_STOP_up': [[149, 0, 150], [256, 256, 256]],
            'red_up': [[96, 0, 0], [255, 256, 256]]
        }

        self.save_to_file()

    def __init__(self):

        self.load_from_file()
        # self.reset()

    def get_color(self, name):
        data = [[0, 0, 0], [256, 256, 256]]
        if isinstance(self.colors, dict):
            if name in self.colors:
                data = self.colors[name]
                # print(green)
        return data

    def constrain(self, x, out_min, out_max):
        if x < out_min:
            return out_min
        elif out_max < x:
            return out_max
        else:
            return x

    def set_color(self, name, data):

        for i in range(len(data)):
            for j in range(len(data[i])):
                data[i][j] = self.constrain(data[i][j], 0, 256)
        self.colors[name] = data

    # def save_to_file(self, filename="/home/pi/robot/colors.txt"):
    def save_to_file(self, filename="colors.txt"):
        print("save to file")
        with open(filename, 'w') as outfile:
            json.dump(self.colors, outfile)
        with open(filename + ".copy", 'w') as outfile:
            json.dump(self.colors, outfile)

    # def load_from_file(self, filename="/home/pi/robot/colors.txt"):
    def load_from_file(self, filename="colors.txt"):
        try:
            with open(filename) as json_file:
                self.colors = json.load(json_file)
        except Exception as e:
            print("error load file", e)
            print("load.copy")
            try:
                with open(filename + ".copy") as json_file:
                    self.colors = json.load(json_file)
            except Exception as e1:
                print("failed load copy", e1)

    def make_mask(self, frame, name):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color = self.get_color(name)
        mask = cv2.inRange(hsv, np.array(color[0]), np.array(color[1]))
        # print("make mask", name, color)
        return mask

    def list_names(self):
        names = []
        for i in self.colors:
            names.append(i)
        return names


hsv_work = HSV_WORK()

# текущая стадия программы

old_state = ""
# название стадий
state_names = ["Manual move", "Move to line", "Main move", "Left", "Right"]

# фильтр черного цвета

# low = np.array([0, 0, 00])
# up = np.array([180, 80, 115])

# синий


timer_state = 0


def Find_black_line(frame, frame_show, direction, flag_draw=True):
    x1, y1 = 640 - 20, 0
    x2, y2 = 640, 480

    if direction == 1:
        x1, y1 = 0, 0
        x2, y2 = 20, 480

    # вырезаем часть изображение
    frame_crop = frame[y1:y2, x1:x2]
    frame_crop_show = frame_show[y1:y2, x1:x2]
    # cv2.imshow("frame_crop", frame_crop)
    # рисуем прямоугольник на изображении
    cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # hsv = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2HSV)
    # фильтруем по заданным параметрам
    # mask = cv2.inRange(hsv, low_black, up_black)

    mask = hsv_work.make_mask(frame_crop, "black")
    # выводим маску для проверки
    # cv2.imshow("mask", mask)
    # на отфильтрованной маске выделяем контуры
    _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # перебираем все найденные контуры
    flag_line = False
    max_y = 0
    for contour in contours:
        # Создаем прямоугольник вокруг контура
        x, y, w, h = cv2.boundingRect(contour)
        # вычисляем площадь найденного контура
        area = cv2.contourArea(contour)
        if area > 20:
            # отрисовываем найденный контур
            if flag_draw:
                cv2.drawContours(frame_crop_show, contour, -1, (0, 0, 255), 2)
            # включаем зеленый свет
            # robot.lamp.rgb(0, 1, 0)
            if max_y < y + h:
                max_y = y + h
    return max_y


def Find_start_line(frame, frame_show, color, flag_draw=True):
    x1, y1 = 320 - 20, 400
    x2, y2 = 320 + 20, 460
    # вырезаем часть изображение
    frame_crop = frame[y1:y2, x1:x2]
    frame_crop_show = frame_show[y1:y2, x1:x2]
    # cv2.imshow("frame_crop", frame_crop)
    # рисуем прямоугольник на изображении
    cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # переводим изображение с камеры в формат HSV
    # hsv = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2HSV)
    # фильтруем по заданным параметрам
    # mask = cv2.inRange(hsv, hsv_low, hsv_high)
    mask = hsv_work.make_mask(frame_crop, color)
    # выводим маску для проверки
    # cv2.imshow("mask", mask)
    # на отфильтрованной маске выделяем контуры
    _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # перебираем все найденные контуры
    for contour in contours:
        # Создаем прямоугольник вокруг контура
        x, y, w, h = cv2.boundingRect(contour)
        # вычисляем площадь найденного контура
        area = cv2.contourArea(contour)
        if area > 200:
            if flag_draw:
                cv2.drawContours(frame_crop_show, contour, -1, (0, 0, 255), 2)
            return True

    return False


def Find_box(frame, frame_show, color, flag_draw=True):
    x1, y1 = 0, 200  # Xanne
    # x1, y1 = 0, 100   #Lime
    x2, y2 = 640, 400
    # вырезаем часть изображение
    frame_crop = frame[y1:y2, x1:x2]
    frame_crop_show = frame_show[y1:y2, x1:x2]
    # cv2.imshow("frame_crop", frame_crop)
    # рисуем прямоугольник на изображении

    # переводим изображение с камеры в формат HSV
    # hsv = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2HSV)
    # фильтруем по заданным параметрам
    # mask = cv2.inRange(hsv, hsv_low, hsv_high)
    mask = hsv_work.make_mask(frame_crop, color)
    # robot.set_frame(mask)
    # выводим маску для проверки
    cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # cv2.imshow("mask", mask)
    # на отфильтрованной маске выделяем контуры
    _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # перебираем все найденные контуры
    for contour in contours:
        # Создаем прямоугольник вокруг контура
        x, y, w, h = cv2.boundingRect(contour)
        # вычисляем площадь найденного контура
        area = cv2.contourArea(contour)
        if area > 300:
            if flag_draw:
                c = (0, 0, 255)
                if color == "green":
                    c = (0, 255, 0)
                cv2.drawContours(frame_crop_show, contour, -1, c, 2)

                cv2.putText(frame_show, str(round(area, 1)), (x + x1, y - 20 + y1),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                            c, 2)
            return x + w / 2, area

    return None, None


def Find_black_box_right(frame, frame_show, color, flag_draw=True):
    # x1, y1 = 360, 255 #Lime
    x1, y1 = 360, 320 # Black
    # x2, y2 = 430, 295
    x2, y2 = 430, 400
    # вырезаем часть изображение
    frame_crop = frame[y1:y2, x1:x2]
    frame_crop_show = frame_show[y1:y2, x1:x2]
    # cv2.imshow("frame_crop", frame_crop)
    # рисуем прямоугольник на изображении
    cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # переводим изображение с камеры в формат HSV
    # hsv = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2HSV)
    # фильтруем по заданным параметрам
    # mask = cv2.inRange(hsv, hsv_low, hsv_high)
    mask = hsv_work.make_mask(frame_crop, color)
    # выводим маску для проверки
    # cv2.imshow("mask", mask)
    # на отфильтрованной маске выделяем контуры
    _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # перебираем все найденные контуры
    for contour in contours:
        # Создаем прямоугольник вокруг контура
        x, y, w, h = cv2.boundingRect(contour)
        # вычисляем площадь найденного контура
        area = cv2.contourArea(contour)
        if area > 1000:
            if flag_draw:
                cv2.drawContours(frame_crop_show, contour, -1, (0, 0, 255), 2)
            return True

    return False


def Find_black_box_left(frame, frame_show, color, flag_draw=True):
    # x1, y1 = 210, 255 # Lime
    x1, y1 = 210, 320 # Black
    # x2, y2 = 280, 295
    x2, y2 = 280, 400
    # вырезаем часть изображение
    frame_crop = frame[y1:y2, x1:x2]
    frame_crop_show = frame_show[y1:y2, x1:x2]
    # cv2.imshow("frame_crop", frame_crop)
    # рисуем прямоугольник на изображении
    cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # переводим изображение с камеры в формат HSV
    # hsv = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2HSV)
    # фильтруем по заданным параметрам
    # mask = cv2.inRange(hsv, hsv_low, hsv_high)
    mask = hsv_work.make_mask(frame_crop, color)
    # выводим маску для проверки
    # cv2.imshow("mask", mask)
    # на отфильтрованной маске выделяем контуры
    _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # перебираем все найденные контуры
    for contour in contours:
        # Создаем прямоугольник вокруг контура
        x, y, w, h = cv2.boundingRect(contour)
        # вычисляем площадь найденного контура
        area = cv2.contourArea(contour)
        if area > 1000:
            if flag_draw:
                cv2.drawContours(frame_crop_show, contour, -1, (0, 0, 255), 2)
            return True

    return False


# robot.wait(500)
# frame1=None
count_lines = 0
e_old = 0
flagfr = 0
index_color = 0
step_hsv = 1
flag_not_save_hsv = 0

hsv_frame = robot.get_frame(wait_new_frame=True)


def put_telemetry(frame_show):
    # вывод телеметрии на экран
    cv2.putText(frame_show, "State: " + state, (10, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (0, 0, 255), 2)
    cv2.putText(frame_show, "Count lines: " + str(count_lines), (10, 80), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (0, 0, 255), 2)

    robot.set_frame(frame_show, 15)


reg_move = regulators.Regulators(0, 0, 0, Ki_border=5)
# robot.serv(180)
# robot.wait(500)
# robot.serv(-180)
# robot.wait(500)
robot.serv(0)


def go_back(angle, time1, time2):
    global timer_finish
    robot.serv(angle)
    robot.move(-global_speed, 0, time1, wait=False)
    robot.wait(time1)

    robot.serv(-angle)
    robot.move(global_speed, 0, time2, wait=False)
    robot.wait(time2)
    if timer_finish is not None:
        timer_finish += time1 / 1000 + time2 / 1000


robot.beep()
robot.wait(300)
robot.beep()

# button_work = False

while True:
    if state != old_state:
        timer_state = time.time()
        old_state = state

    if robot.button():
        # if not button_work:
            state = "Move to line"
            button_work = True
            
        # else: # вырубить
        #     button_work = False
        #     state = "Manual move"

    frame = robot.get_frame(wait_new_frame=True)

    frame_show = frame.copy()

    k = robot.get_key()

    # если нажата клавиша 1
    if k == 48:
        # переключаем програму в 1 стадию
        state = "HSV"
    if k == 49:
        # переключаем програму в 1 стадию
        state = "Manual move"
    # если нажата клавиша 2
    elif k == 50:
        # переключаем програму во 2 стадию
        state = "Move to line"
    elif k == 51:
        # переключаем програму во 2 стадию
        state = "Main move"
        robot.serv(0)
    # elif k == 51:
    #     # переключаем програму в 3 стадию
    #     timer_stop = time.time()

    if state == "Manual move":
        # ручное управление

        if k == 37:
            manual_serv = 25
            robot.serv(manual_serv)
            # print(manual_serv)
        if k == 39:
            manual_serv = -25
            robot.serv(manual_serv)
            # print(manual_serv)
        if k == 32:
            manual_serv = 0
            robot.serv(manual_serv)
            # print(manual_serv)
        if k == 38:
            robot.move(speed_manual, 0, 100, wait=False)
        if k == 40:
            robot.move(-speed_manual, 0, 100, wait=False)

        Find_box(frame, frame_show, "green")
        Find_black_box_right(frame, frame_show, "black")
        Find_black_box_left(frame, frame_show, "black")
        # Find_box(frame, "red_up")
        # отправляем команды на робота
        # robot.move(manual_throttle, 0, 100, wait=False)
        # robot.serv(manual_angle)
        # телеметрия ручного управления
        cv2.putText(frame_show, "throttle: " + str(round(manual_throttle, 1)), (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)
        cv2.putText(frame_show, "angle: " + str(round(manual_angle, 1)), (10, 80),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)
        put_telemetry(frame_show)
    elif state == "Move to line":
        robot.serv(0)
        robot.move(global_speed, 0, 100, wait=False)

        is_orange = Find_start_line(frame, frame_show, "orange")
        is_blue = Find_start_line(frame, frame_show, "blue")

        # print("orange:",is_orange, "Blue:", is_blue)

        if is_orange:
            direction = 1
            state = "Right"
            print("End state Move to line, go ", state)

        if is_blue:
            direction = -1
            state = "Left"
            # frame1 = frame
            print("End state Move to line, go ", state)
        put_telemetry(frame_show)
    elif state == "Left":
        # robot.lamp.rgb(0, 0, 1)
        cv2.putText(frame_show, "timer: " + str(round(time.time() - timer_state, 1)), (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)

        # едем прямо 2 секунды, а потом переключаемся в 1 стадию
        if time.time() < timer_state + pause_povorot:
            robot.move(global_speed, 0, 100, wait=False)
            robot.serv(50)

        if time.time() > timer_state + pause_povorot:
            state = "Main move"

        is_orange = Find_start_line(frame, frame_show, "orange")
        if is_orange:
            state = "Main move"

        put_telemetry(frame_show)
    elif state == "Right":
        # robot.lamp.rgb(0, 0, 1)
        cv2.putText(frame_show, "timer: " + str(round(time.time() - timer_state, 1)), (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)

        # едем прямо 2 секунды, а потом переключаемся в 1 стадию
        if time.time() < timer_state + pause_povorot:
            robot.move(global_speed, 0, 100, wait=False)
            robot.serv(-50)

        if time.time() > timer_state + pause_povorot:
            state = "Main move"
        put_telemetry(frame_show)
    elif state == "Main move":

        if count_lines >= 11:
            # if time.time()>timer_state+1:
            if timer_finish is None:
                timer_finish = time.time() + pause_finish
            if count_lines > 11:
                robot.move(-255, 0, 1000, wait=True)
                exit(0)

            if timer_finish is not None:
                if time.time() > timer_finish:
                    global_speed = 0
                    robot.beep()
                    state = "Finish"

        delta_banka = 0
        delta_speed = 0

        if direction == 1:
            if Find_black_box_left(frame, frame_show, "black"):
                go_back(40, 500, 300)

            is_orange = Find_start_line(frame, frame_show, "orange")
            if is_orange:
                state = "Right"
                count_lines += 1
                count_lines_proverka += 1
                print(count_lines)

            if not flag_qualification:
                cord_red_banka, area_red_banka = Find_box(frame, frame_show, "red_up")
                if area_red_banka is not None:
                    delta_banka = delta_red_plus
                    timer_banka = time.time()
                    if area_red_banka > 11000:
                        go_back(30, time_go_back_banka, 140)
                        if count_lines_proverka < count_lines:
                            count_lines -= 1
                        if timer_finish is not None:
                            timer_finish += time.time() - timer_banka

                cord_green_banka, area_green_banka = Find_box(frame, frame_show, "green")
                if area_green_banka is not None:
                    delta_banka = delta_green_plus
                    # print(area_green_banka)
                    timer_banka = time.time()
                    if area_green_banka > 11000:
                        go_back(-30, time_go_back_banka, 140)
                        if count_lines_proverka < count_lines:
                            count_lines -= 1
                        if timer_finish is not None:
                            timer_finish += time.time() - timer_banka

                if area_green_banka is not None and area_red_banka is not None:

                    # delta_speed = -10

                    if area_red_banka > area_green_banka:
                        delta_banka = delta_red_plus
                    else:
                        delta_banka = delta_green_plus

        if direction == -1:

            if Find_black_box_right(frame, frame_show, "black"):
                go_back(-40, 500, 300)

            is_blue = Find_start_line(frame, frame_show, "blue")
            if is_blue:
                state = "Left"
                count_lines += 1
                count_lines_proverka += 1
                print(count_lines)
            if not flag_qualification:
                cord_red_banka, area_red_banka = Find_box(frame, frame_show, "red_up")
                if area_red_banka is not None:
                    delta_banka = delta_red_minus
                    if area_red_banka > 11000:
                        timer_banka = time.time()
                        go_back(30, time_go_back_banka, 140)
                        if count_lines_proverka < count_lines:
                            count_lines -= 1
                        if timer_finish is not None:
                            timer_finish += time.time() - timer_banka

                cord_green_banka, area_green_banka = Find_box(frame, frame_show, "green")
                if area_green_banka is not None:
                    delta_banka = delta_green_minus
                    # print(area_green_banka)
                    if area_green_banka > 11000:
                        timer_banka = time.time()
                        go_back(-30, time_go_back_banka, 140)
                        if count_lines_proverka < count_lines:
                            count_lines -= 1
                        if timer_finish is not None:
                            timer_finish += time.time() - timer_banka

                if area_green_banka is not None and area_red_banka is not None:

                    # delta_speed = -10

                    if area_red_banka > area_green_banka:
                        delta_banka = delta_red_minus
                    else:
                        delta_banka = delta_green_minus

        # print("delta banka", delta_banka)

        # is_blue = Find_start_line(frame, "blue")

        max_y = Find_black_line(frame, frame_show, direction)
        if max_y > 0:
            # print(max_y)

            reg_move.set(0.6, 0.00001, 0.06)

            porog = porog_black_line_minus
            if direction > 0:
                porog = porog_black_line_plus

            p = reg_move.apply(porog, max_y) * direction  # Lime
            # p = reg_move.apply(300, max_y)*direction #Xanna
            # print(max_y)
            robot.serv(p + delta_banka)
            robot.move(global_speed + delta_speed, 0, 100, wait=False)
        else:
            if direction == -1:
                go_back(-40, 300, 50)
                # robot.serv(-40)
                # robot.move(-global_speed, 0, 300, wait=False)
                # robot.wait(300)
                # if timer_finish is not None:
                #     timer_finish += 0.3
            else:
                go_back(40, 300, 50)
                # robot.serv(40)
                # robot.move(-global_speed, 0, 300, wait=False)
                # robot.wait(300)
                # if timer_finish is not None:
                #     timer_finish += 0.3

        put_telemetry(frame_show)
    elif state == 'HSV':
        # настройка фильтра HSV
        if flagfr == 0:
            hsv_frame = frame
        Y, X, Z = frame.shape
        lst = hsv_work.list_names()
        name_color = lst[index_color]
        mask = hsv_work.make_mask(hsv_frame, name_color)
        color = hsv_work.colors[name_color]
        low_set, up_set = color[0], color[1]
        gray_image = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        cv2.putText(gray_image, str(name_color), (10, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)
        cv2.putText(gray_image, str(color[0]), (10, 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)
        cv2.putText(gray_image, str(color[1]), (10, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)
        cv2.putText(gray_image, "step: " + str(step_hsv), (10, 80), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)

        # gray_image = robot.text_to_frame(gray_image, str(name_color), 20, 20, (0, 0, 255), 2)
        # gray_image = robot.text_to_frame(gray_image, str(color[0]), 170, 20, (0, 0, 255), 2)
        # gray_image = robot.text_to_frame(gray_image, str(color[1]), 170, 45, (0, 0, 255), 2)
        # gray_image = robot.text_to_frame(gray_image, "step: " + str(step_hsv), 20, gray_image.shape[0] - 20,
        #                                  (0, 0, 255), 2)
        if flag_not_save_hsv:
            pass
            # cv2.putText(gray_image, str("need save hsv"), (120, gray_image.shape[0] - 50),
            #             cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 255, 0), 6)

        robot.set_frame(gray_image)
        # cv2.imshow("hsv", gray_image)
        m = k
        if m == 32: flagfr = not flagfr

        if m == 81: low_set[0] -= step_hsv
        if m == 87: low_set[0] += step_hsv
        if m == 69: up_set[0] -= step_hsv
        if m == 82: up_set[0] += step_hsv
        if m == 65: low_set[1] -= step_hsv
        if m == 83: low_set[1] += step_hsv
        if m == 68: up_set[1] -= step_hsv
        if m == 70: up_set[1] += step_hsv
        if m == 90: low_set[2] -= step_hsv
        if m == 88: low_set[2] += step_hsv
        if m == 67: up_set[2] -= step_hsv
        if m == 86: up_set[2] += step_hsv

        if m >= 65 and m <= 90:
            flag_not_save_hsv = True

        hsv_work.set_color(name_color, [low_set, up_set])
        if m == 8:
            if step_hsv == 1:
                step_hsv = 10
            else:
                step_hsv = 1
        if m == 13:
            hsv_work.save_to_file()
            flag_not_save_hsv = False

        if m == 40:  # вниз
            index_color += 1
            lst = hsv_work.list_names()
            if index_color >= len(lst):
                index_color = 0
            robot.wait(200)
            robot.get_key()

        if m == 38:  # вверх
            index_color -= 1
            lst = hsv_work.list_names()
            if index_color < 0:
                index_color = len(lst) - 1
            robot.wait(200)
            robot.get_key()

        name_color = lst[index_color]
        color = hsv_work.colors[name_color]
        low_set, up_set = color[0], color[1]

        if m != -1:
            print(name_color, low_set, up_set)
            print(m)

