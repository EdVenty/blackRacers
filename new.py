import time
from typing import Tuple, Union

import cv2
import numpy as np
import regulators

import RobotAPI as rapi

time_go_banka = 600 # Устанавливаем время объезда банки
time_go_back_banka = 600 # Устанавливаем время отъезда от банки
max_lines = 12

flag_qualification = False  # Если необходимо проехать квалификацию
if flag_qualification:
    global_speed = 0  # Добавляем скорости на квалификации 240 в оражневую, 220 в синею
    povorot_speed = 0  # Скорость поворота в квалификации 180
    pause_finish = 0.38  # Устанавливаем задержку финиша на квалификации
    pause_povorot = 0.4  # Устанавливаем максимальную задуржку на повороте на квалификации 0.45

COLOR_RED = ..., ... # сюда HSV min и max через запятую
COLOR_GREEN = ..., ...
COLOR_BLACK = ..., ...
COLOR_ORANGE = ..., ...
COLOR_BLUE = ..., ...

STATE_MOVE_TO_LINE = 2
STATE_MAIN_MOVE = 1
STATE_RIGHT = 2
STATE_LEFT = 3
STATE_FINISH = 4

state = STATE_MAIN_MOVE  # Устанавливаем текущую стадию на Ручное управление
robot = rapi.RobotAPI(flag_pyboard=True, flag_send_video=True)
robot.set_camera(100, 640, 480, 0, 0)  # установка разрешения камеры
timer_state = 0  # Создаём таймер поворота
reg_move = regulators.Regulators(0, 0, 0, Ki_border=5)
reg_move.set(0.5, 0.000, 0.05)
fps = 0
fps_last = 0
fps_timer = time.time()
timer_finish = None
direction = 0
count_lines = 0
delta_banka = 0
second_line_reached = False
timer_povorot_delay = None
before_povorot = False
p = 0

def make_mask(frame, color: Tuple[np.ndarray, np.ndarray]):
    return cv2.inRange(frame, color[0], color[1])


def Find_black_line(frame, frame_show, direction, flag_draw=True):
    # Задаём 1-е координаты области определения чёрной линии слева.
    x1, y1 = 640 - 20, 240
    # Задаём 2-е координаты области определения чёрной линии слева.
    x2, y2 = 640, 340

    if direction == 1:
        # Задаём 1-е координаты области определения чёрной линии справа.
        x1, y1 = 0, 240
        # Задаём 1-е координаты области определения чёрной линии справа.
        x2, y2 = 20, 340

    # вырезаем часть изображение
    frame_crop = frame[y1:y2, x1:x2]
    frame_crop_show = frame_show[y1:y2, x1:x2]
    # рисуем прямоугольник на изображении
    cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)

    mask = make_mask(frame_crop, COLOR_BLACK)
    # на отфильтрованной маске выделяем контуры
    _, contours, _ = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # перебираем все найденные контур
    contours = [(i, cv2.boundingRect(i))
                for i in contours if cv2.contourArea(i) > 20]
    if contours:
        contour, (_, y, _, h) = max(contours, key=lambda x: x[1][1] + x[1][3])
        if flag_draw:
            cv2.drawContours(frame_crop_show, contour, -1, (0, 0, 255), 2)
        return y + h


def Find_start_line(frame, frame_show, color, flag_draw=True):
    global timer_povorot_delay, povorot_delay
    x1, y1 = 320 - 40, 420
    x2, y2 = 320 + 40, 480
    # вырезаем часть изображение
    frame_crop = frame[y1:y2, x1:x2]
    frame_crop_show = frame_show[y1:y2, x1:x2]
    # рисуем прямоугольник на изображении
    cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)
    black = make_mask(frame_crop, COLOR_BLACK)
    mask = make_mask(frame_crop, COLOR_ORANGE if color ==
                     'orange' else COLOR_BLUE) - black
    # на отфильтрованной маске выделяем контуры
    _, contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
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
    x1, y1 = 40, 250  # Xanne
    # x1, y1 = 0, 100   #Lime
    x2, y2 = 600, 440
    # вырезаем часть изображение
    # frame_crop = cv2.GaussianBlur(frame[y1:y2, x1:x2], (5, 5), 10)
    frame_crop = frame[y1:y2, x1:x2]
    frame_crop_show = frame_crop.copy()
    # cv2.imshow("frame_crop", frame_crop)
    # рисуем прямоугольник на изображении

    # переводим изображение с камеры в формат HSV
    # hsv = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2HSV)
    # фильтруем по заданным параметрам
    # mask = cv2.inRange(hsv, hsv_low, hsv_high)
    mask = make_mask(frame_crop, COLOR_GREEN if color ==
                     'green' else COLOR_RED)
    # robot.set_frame(mask)
    # выводим маску для проверки
    cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # cv2.imshow("mask", mask)
    # на отфильтрованной маске выделяем контуры
    _, contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # перебираем все найденные контуры
    contours = [i for i in contours if cv2.contourArea(i) > 300]
    if contours:
        contour = max(contours, key=cv2.contourArea)
        # Создаем прямоугольник вокруг контура
        x, y, w, h = cv2.boundingRect(contour)
        # вычисляем площадь найденного контура
        area = cv2.contourArea(contour)

        if flag_draw:
            c = (0, 0, 255)
            if color == "green":
                c = (0, 255, 0)
            cv2.drawContours(frame_crop_show, contour, -1, c, 2)

            cv2.putText(frame_show, str(round(area, 1)), (x + x1, y - 40 + y1),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                        c, 2)
            cv2.putText(frame_show, str(x + w/2) + " " + str(y + h), (x + x1, y - 60 + y1),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                        c, 2)
        frame_show[y1:y2, x1:x2] = frame_crop_show
        return x + w / 2 + x1, y + h, area, x >= 150 and x <= 400
        # return x + w / 2, area, True

    return None, None, None, False


def Find_black_box_right(frame, frame_show, color, flag_draw=True):
    # x1, y1 = 360, 255 #Lime
    x1, y1 = 360, 400  # Black
    # x2, y2 = 430, 295
    x2, y2 = 410, 450
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
    mask = make_mask(frame_crop, color)
    # выводим маску для проверки
    # cv2.imshow("mask", mask)
    # на отфильтрованной маске выделяем контуры
    _, contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
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
    x1, y1 = 220, 400  # Black
    # x2, y2 = 430, 295
    x2, y2 = 270, 450
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
    mask = make_mask(frame_crop, COLOR_BLACK)
    # выводим маску для проверки
    # cv2.imshow("mask", mask)
    # на отфильтрованной маске выделяем контуры
    _, contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
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


def increment_fps():
    global fps_last, fps, fps_timer
    if time.time() - fps_timer >= 1: #Считаем FPS
        fps_last = fps
        fps = 0
        fps_timer = time.time()
    fps += 1


def go_back(angle, time1, time2):
    global timer_finish
    robot.serv(angle)
    robot.move(-150, 0, time1, wait=False)
    robot.wait(time1)

    robot.serv(0)
    # robot.serv(-angle)
    robot.move(150, 0, time2, wait=False)
    robot.wait(time2)
    if timer_finish is not None:
        timer_finish += time1 / 1000 + time2 / 1000


def calc_banka(frame, frame_show, direction) -> Tuple[int, Union[int, None]]:
    """Расчитать угол объезда банки и отъезда назад.

    Аргументы:
        frame (CV2 RGB Frame): Исходный кадр
        frame_show (CV2 RGB Frame): Кадр для показа и рисования
        direction (int): 1 - движение по часовой; 2 - против

    Returns:
        (int, int | None): Кортеж: 1) угол объезда банок; 2) int - угол отъезда; None - нет необходимости отъезжать от банки
    """
    x_green_banka, y_green_banka, area_green_banka, d = Find_box(frame, frame_show, "green")
    go_back_angle = None
    if area_green_banka is not None:
        if direction == 1:
            delta_green_plus = 0
            if x_green_banka + 150 - y_green_banka < 500:
                delta_green_plus = (500 - x_green_banka)/6
            if y_green_banka > 90:
                delta_green_plus += (y_green_banka - 90)/5
            delta_banka = delta_green_plus
            if y_green_banka > 180 and x_green_banka < 480:
                go_back_angle = -35

    x_red_banka, y_red_banka, area_red_banka, d = Find_box(frame, frame_show, "red_up")
    if area_red_banka is not None:
        if direction == 1:
            delta_red_plus = 0
            if x_red_banka - 150 + y_red_banka > 140:
                delta_red_plus = (x_red_banka - 140)/6
            if y_red_banka > 90:
                delta_red_plus += (y_red_banka - 90)/5
            delta_banka = delta_red_plus
            delta_banka = -delta_banka
            if y_red_banka > 180 and x_red_banka > 120:
                go_back_angle = 30

    if area_green_banka is not None and area_red_banka is not None:
        if area_red_banka > area_green_banka:
            delta_banka = delta_red_plus
        else:
            delta_banka = delta_green_plus

    return delta_banka, go_back_angle


def check_finish():
    global count_lines, max_lines, timer_finish, state, global_speed
    if count_lines >= max_lines:
        if timer_finish is None:
            timer_finish = time.time() + pause_finish
        if count_lines > max_lines:
            robot.serv(0)
            robot.move(-200, 0, 1000, wait=True)
            robot.beep()
            robot.beep()
            global_speed = 0
            state = STATE_FINISH
        if timer_finish is not None:
            if time.time() > timer_finish:
                global_speed = 0
                robot.beep()
                robot.beep()
                state = STATE_FINISH


def show(frame_show):
    """Передать кадр на компюьютер (если подключён по wifi или ethernet)

    Аргументы:
        frame (CV2 RGB Frame): Кадр для передачи
    """
    global fps, fps_last, fps_timer
    cv2.putText(frame_show, "State: " + state, (10, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (255, 255, 255), 2)
    cv2.putText(frame_show, "Count lines: " + str(count_lines), (10, 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (255, 255, 255), 2)
    cv2.putText(frame_show, "Direction: " + str(direction), (10, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (255, 255, 255), 2)
    cv2.putText(frame_show, "P: " + str(p), (10, 80), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (255, 255, 255), 2)
    cv2.putText(frame_show, "Delta banka: " + str(delta_banka), (10, 100), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (255, 255, 255), 2)
    cv2.putText(frame_show, "FPS: " + str(fps_last), (10, 120), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (255, 255, 255), 2)
    
    robot.set_frame(frame_show, 15)


def move_to_line(frame):
    global direction, global_speed
    frame_show = frame.copy()
    robot.serv(0)
    robot.move(global_speed-20, 0, 100, wait=False)
    is_orange = Find_start_line(frame, frame_show, "orange")
    is_blue = Find_start_line(frame, frame_show, "blue")
    if is_orange:
        direction = 1
        state = STATE_RIGHT
        print("End state Move to line, go ", state)
    if is_blue:
        direction = -1
        state = STATE_LEFT
        print("End state Move to line, go ", state)
    show(frame_show)


def main_move(frame):
    global second_line_reached, count_lines, timer_povorot_delay, before_povorot, state, p
    frame_show = frame.copy()
    second_line_reached = False
    check_finish()
    delta, go_back_angle = calc_banka(frame, frame_show, direction)
    if go_back_angle:
        go_back(go_back_angle, time_go_back_banka, time_go_banka)
    if direction == 1 and Find_black_box_left(frame, frame_show, "black"):
        go_back(40, 500, 300)
    elif Find_black_box_right(frame, frame_show, "black"):
        go_back(-40, 500, 300)
    max_y = Find_black_line(frame, frame_show, direction)
    max_y2 = Find_black_line(frame, frame_show, -direction)
    if direction == -1:
        is_blue = Find_start_line(frame, frame_show, "blue")
        if is_blue:
            timer_povorot_delay = time.time()
            before_povorot = True
            state = STATE_LEFT
            count_lines += 1
    else:
        is_orange = Find_start_line(frame, frame_show, "orange")
        if is_orange or max_y2 < 230:
            timer_povorot_delay = time.time()
            before_povorot = True
            state = STATE_RIGHT

    p = reg_move.apply(max_y2, max_y) * direction

    if delta_banka == 0:
        robot.serv(p)
    else:
        robot.serv(delta_banka)
    robot.move(global_speed, 0, 100, wait=False)
    
    show(frame_show)


def right(frame):
    global before_povorot, povorot_speed, state, flag_qualification, second_line_reached, count_lines
    frame_show = frame.copy()
    cv2.putText(frame_show, "timer: " + str(round(time.time() - timer_state, 1)), (10, 60),
                cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (0, 0, 255), 2)
    if time.time() < timer_state + pause_povorot:
        robot.move(povorot_speed, 0, 100, wait=False)
        if before_povorot:
            robot.serv(-5)
        else:
            robot.serv(-60)
    else:
        state = STATE_MAIN_MOVE
    if before_povorot and Find_black_line(frame, frame_show, -direction) > 250:
        state = STATE_MAIN_MOVE
    if not flag_qualification:
        is_orange = Find_start_line(frame, frame_show, "blue")
        if is_orange:
            if time.time() >= timer_povorot_delay:
                state = STATE_MAIN_MOVE
            if not second_line_reached:
                if is_orange:
                    robot.beep()
                    second_line_reached = True
                    count_lines += 1
                    before_povorot = False
        x_green_banka, y_green_banka, area_green_banka, d = Find_box(frame, frame_show, "green")
        x_red_banka, y_red_banka, area_red_banka, d = Find_box(frame, frame_show, "red_up")
        if area_green_banka is not None or area_red_banka is not None:
            state = STATE_MAIN_MOVE
            print("Bankus in povorotus")
    show(frame_show)


def left(frame):
    global before_povorot, second_line_reached, state, count_lines
    frame_show = frame.copy()
    cv2.putText(frame_show, "timer: " + str(round(time.time() - timer_state, 1)), (10, 60),
                cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (0, 0, 255), 2)
    if time.time() < timer_state + pause_povorot:
        robot.move(povorot_speed, 0, 100, wait=False)
        if before_povorot:
            robot.serv(5)
        else:
            robot.serv(60)
    else:
        state = STATE_MAIN_MOVE
    if before_povorot and Find_black_line(frame, frame_show, -direction) > 250:
        state = STATE_MAIN_MOVE
    if not flag_qualification:
        is_blue = Find_start_line(frame, frame_show, "orange")
        if is_blue:
            if time.time() >= timer_povorot_delay:
                state = STATE_MAIN_MOVE
            if not second_line_reached:
                if is_blue:
                    robot.beep()
                    second_line_reached = True
                    count_lines += 1
                    before_povorot = False
        x_green_banka, y_green_banka, area_green_banka, d = Find_box(frame, frame_show, "green")
        x_red_banka, y_red_banka, area_red_banka, d = Find_box(frame, frame_show, "red_up")
        if area_green_banka is not None or area_red_banka is not None:
            state = STATE_MAIN_MOVE
            print("Bankus in povorotus")
    show(frame_show)


def main():
    while True:
        frame = robot.get_frame(wait_new_frame=True)
        increment_fps()
        if state == STATE_MOVE_TO_LINE:
            move_to_line(frame)
        elif state == STATE_MAIN_MOVE:
            main_move(frame)
        elif state == STATE_RIGHT:
            right(frame)
        elif state == STATE_LEFT:
            left(frame)


if __name__ == '__main__':
    main()