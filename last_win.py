
import json
import time

import cv2
import numpy as np
import regulators

import RobotAPI as rapi

# ======================= Константы =========================
time_go_banka = 168 # Устанавливаем время объезда банки
time_ditch_banka = 10
global_speed = 120 # Устанавливаем скорость робота 130
pause_finish = 0.8 # Устанавливаем пауза перед остановкой на финише 1.25
porog_black_line_minus = 275 # Устанавливаем порог чёрной линии по часовой стрелке 305
porog_black_line_plus = 285 # Устанавливаем порог чёрной линии против часовой стрелке
delta_green_plus = 15 # Устанавливаем угол объезда зелёной банки по часовой стрелке
delta_red_plus = -15 # Устанавливаем угол объезда красной банки по часовой стрелке
delta_green_minus = 15 # Устанавливаем угол объезда зелёной банки против часовой стрелке
delta_red_minus = -15 # Устанавливаем угол объезда красной банки против часовой стрелке
time_go_back_banka = 600 # Устанавливаем время отъезда от банки
pause_povorot = 1 # Устанавливаем максимальную задуржку на повороте
go_back_banka_area = 8000 # Устанавливаем площадь банки, при которой робот отъезжает
super_ditch_banka_area = 4000
ditch_banka_area = 2000 # Устанавливаем площадь банки, при которой робот обруливает
# ditch_banka_angle = 30
ditch_banka_mult_plus = 1
ditch_banka_mult_minus = 1
super_ditch_banka_mult_plus = 1.5
super_ditch_banka_mult_minus = 2
max_lines = 11 # * 7
povorot_delay = 17 / 11 * 0.6
speed_manual = global_speed # Устанавливаем скорость ручного управления 
manual_angle = 0 # Устанавливаем угол ручного управления (1- по часовой, -1 против часовой стрелки)
manual_throttle = 0 # Устанавливаем дроссель ручного управления (1- по часовой, -1 против часовой стрелки)
after_povorot_delay = 0.0

flag_qualification = False # Если необходимо проехать квалификацию
if flag_qualification: 
    global_speed += 40.3 # Добавляем скорости на квалификации 55
    pause_finish = 0.38 # Устанавливаем задержку финиша на квалификации
    porog_black_line_plus += 25 # Устанавливаем порог чёрной линии по часовой стрелке на квалификации
    porog_black_line_minus += 25 # Устанавливаем порог чёрной линии против часовой стрелке на квалификации
    pause_povorot = 0.4 # Устанавливаем максимальную задуржку на повороте на квалификации 0.45

# =================== Программные переменные ==================
state = "Manual move" # Устанавливаем текущую стадию на Ручное управление
count_lines_proverka = 0 # Устанавливаем счётчик линий на 0
direction = 0 # Устанавливаем направление по умолчанию на По часовой стрелке
timer_finish = None
timer_povorot_delay = 0
after_povorot_delay_timer = None

robot = rapi.RobotAPI(flag_pyboard=True) # инициализация робота
robot.set_camera(60, 640, 480, 0, 0) # установка разрешения камеры

def constraint(value, min, max):
    return min if value < min else max if value > max else value

class HSV_work(object):
    """Класс для настройки HSV диапазонов."""

    def __init__(self):
        self.colors = {} # Создаем переменную цветов
        self.load_from_file() # Загружаем цвета из файла в переменную colors

    def reset(self):
        """Сбросить все цвета на значения по умолчанию.
        """
        self.colors = { # Сброс цветов
            'orange': [[0, 50, 80], [50, 255, 255]],
            'black': [[0, 0, 0], [180, 255, 89]],
            'green': [[51, 50, 70], [84, 255, 255]],
            'white': [[0, 0, 81], [180, 255, 254]],
            'blue': [[90, 0, 0], [120, 255, 170]],
            'red_up': [[96, 0, 0], [180, 255, 255]]
        }

        self.save_to_file() # Сохранение сброшенных цветов в пзу робота

    def get_color(self, name):
        """Получить значения цвета по названию. 

        Аргументы:
            name (str): Название цвета.

        Возвращает:
            Tuple[Tuple[int, int, int], Tuple[int, int, int]]: HSV диапазон цвета. Если цвет не найден, то возвращается [[0, 0, 0], [255, 255, 255]].
        """
        data = [[0, 0, 0], [180, 255, 255]] # Установка значений диапазона по умолчанию
        if isinstance(self.colors, dict): # Проверка, является ли переменная colors дочерним объектом словаря
            if name in self.colors: # Если название цвета в словаре colors
                data = self.colors[name] # Устанавливаем значение data диапазон цвета.
        return data

    def constrain(self, x, out_min, out_max): 
        """Обрезать значение в рамках out_min и out_max.

        Аргументы:
            x (Any): Входное значение. Если входное значение больше (или равно) минимального и меньше (или равно) максимального, то вернётся входное значение.
            out_min (Any): Минимальное значение. Если входное значение x меньше минимального, то вернётся минимальное значение.
            out_max (Any): Максимальное значение. Если входное значение x больше максимального, то вернётся максимальное значение.

        Возвращает:
            Any: Обрезанное значение по выше приведённым правилам. 
        """
        if x < out_min: # Если входное значение меньше минимального
            return out_min # Вернуть минимальное значение
        elif out_max < x: # Иначе если входное значение больше максимального
            return out_max # Вернуть максимальное значение
        else: # Иначе
            return x # Вернуть входное значение

    def set_color(self, name, data):
        """Установить цветовой диапазон цвету по имени.

        Args:
            name (str): Название цвета.
            data (Tuple[Tuple[int, int, int], Tuple[int, int, int]]): HSV диапазон цвета.
        """
        for i in range(len(data)): # Проходимся по всем элементам data, взяв только их индексы
            for j in range(len(data[i])): # Проходимся по всем элементам data[i], взяв только их индексы
                if j == 0:
                    data[i][j] = self.constrain(data[i][j], 0, 180) # Задаём цветовой диапазон в переменную.
                else:
                    data[i][j] = self.constrain(data[i][j], 0, 255) # Задаём цветовой диапазон в переменную.
        self.colors[name] = data # Устанавливаем цветовой диапазон в colors по названию цвета

    def save_to_file(self, filename="colors.txt"):
        """Сохранить в файл настройки цветовых HSV диапазонов.

        Аргументы:
            filename (str, optional): Название файла. По умолчанию равно "colors.txt".
        """
        print("save to file") # Выводим в консоль "сохранение в файл"
        with open(filename, 'w') as outfile: # Открываем файл в режиме записи
            json.dump(self.colors, outfile) # Сохраняем в файл json-словарь цветовых диапазонов
        with open(filename + ".copy", 'w') as outfile: # Открываем файл-копию в режиме записи
            json.dump(self.colors, outfile) # Сохраняем в файл-копию json-словарь цветовых диапазонов

    def load_from_file(self, filename="colors.txt"):
        """Загрузить настройки цветовых диапазонов из файла.

        Аргументы:
            filename (str, optional): Название файла. По умолчанию равно "colors.txt".
        """
        try: # Пробуем загрузить значения
            with open(filename) as json_file: # Открываем файл цветовых диапазонов в режиме чтения
                self.colors = json.load(json_file) # Загружаем цветовые диапазоны в переменную colors
        except Exception as e: # Если не удалось загрузить
            print("error load file", e) # Печатаем ошибку
            print("load.copy") # Печатаем, что загружаем из файла-копии
            try: # Пытаемся загрузить значения из файла-копии
                with open(filename + ".copy") as json_file: # Открываем файл-копию
                    self.colors = json.load(json_file) # Загружаем значения цветовых диапазонов из файла-копии в переменную colors
            except Exception as e1: # Если не удалось загрузить значения из файла-копии
                print("failed load copy", e1) # Печатаем сообщение об ошибки загрузки из файла-копии

    def make_mask(self, frame, name):
        """Создать бинаризованную маску из изображения по цветовому диапазону.

        Аргументы:
            frame (CV2 frame): CV2 RGB кадр.
            name (str): Название цвета

        Возвращает:
            CV2 frame: CV2 бинаризованное изображение.
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Конвертируем RGB изображение в HSV
        color = self.get_color(name) # Получаем значение цвеетового диапазона по имени
        mask = cv2.inRange(hsv, np.array(color[0]), np.array(color[1])) # Создаём бинаризованную маску из изображения по цветовому диапазону
        return mask # Возвращаем маску

    def list_names(self):
        """Получить список названий цветов.

        Возвращает:
            List[str]: Список названий цветовых диапазонов.
        """
        names = [] # Создаём список названий цветов
        for i in self.colors: # Проходимся по цветам в переменной colors
            names.append(i) # Добавляем названия цветов
        return names # Возвращаем список названия цветов


hsv_work = HSV_work() # Создаём объекта класса
old_state = "" # Создаём перемнную предыдущего состояния

# название стадий
state_names = ["Manual move", "Move to line", "Main move", "Left", "Right"]

timer_state = 0 # Создаём таймер поворота


def Find_black_line(frame, frame_show, direction, flag_draw=True):
    """Получить координаты чёрной линии на изображении.

    Args:
        frame (CV2 frame): Исходное изображение.
        frame_show (CV2 frame): Изображение, на которое выводится графика.
        direction (int): Направление движения робота. 1 или -1.
        flag_draw (bool, optional): Рисовать графику на изображении. По умолчанию True.

    Returns:
        int: Y чёрной линии.
    """
    x1, y1 = 640 - 20, 0 # Задаём 1-е координаты области определения чёрной линии слева.
    x2, y2 = 640, 480 # Задаём 2-е координаты области определения чёрной линии слева.

    if direction == 1: 
        x1, y1 = 0, 0 # Задаём 1-е координаты области определения чёрной линии справа.
        x2, y2 = 20, 480 # Задаём 1-е координаты области определения чёрной линии справа.

    # вырезаем часть изображение
    frame_crop = frame[y1:y2, x1:x2]
    frame_crop_show = frame_show[y1:y2, x1:x2]
    # рисуем прямоугольник на изображении
    cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)

    mask = hsv_work.make_mask(frame_crop, "black")
    # на отфильтрованной маске выделяем контуры
    _, contours, _ = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # перебираем все найденные контуры
    max_y = 0
    for contour in contours:
        # Создаем прямоугольник вокруг контура
        _, y, _, h = cv2.boundingRect(contour)
        # вычисляем площадь найденного контура
        area = cv2.contourArea(contour)
        if area > 20:
            # отрисовываем найденный контур
            if flag_draw:
                cv2.drawContours(frame_crop_show, contour, -1, (0, 0, 255), 2)
            if max_y < y + h:
                max_y = y + h
    return max_y


def Find_start_line(frame, frame_show, color, flag_draw=True):
    global timer_povorot_delay, povorot_delay
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
    black = hsv_work.make_mask(frame_crop, "black")
    mask = hsv_work.make_mask(frame_crop, color) - black
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
    _, contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
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

                cv2.putText(frame_show, str(round(area, 1)) + str(x >= 150 and x <= 500), (x + x1, y - 20 + y1),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                            c, 2)
            return x + w / 2, area, x >= 150 and x <= 500
            # return x + w / 2, area, True

    return None, None, False


def Find_black_box_right(frame, frame_show, color, flag_draw=True):
    # x1, y1 = 360, 255 #Lime
    x1, y1 = 360, 400  # Black
    # x2, y2 = 430, 295
    x2, y2 = 430, 470
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
    x1, y1 = 360, 400  # Black
    # x2, y2 = 430, 295
    x2, y2 = 430, 470
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

def ditch_banka(angle, time):
    global timer_finish
    robot.serv(-angle)
    robot.move(global_speed, 0, time, wait=False)
    robot.wait(time)
    # if timer_finish is not None:
        # timer_finish += time / 1000


robot.beep()
robot.wait(300)
robot.beep()

kusok_koda_timer = None
kusok_koda_timer2 = None
kusok_koda_right = None
# button_work = False

while True:
    if state != old_state:
        timer_state = time.time()
        old_state = state

    if robot.button():
        # time.sleep(5)
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
        if k == 39:
            manual_serv = -25
            robot.serv(manual_serv)
        if k == 32:
            manual_serv = 0
            robot.serv(manual_serv)
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
        robot.move(global_speed-20, 0, 100, wait=False)

        # if kusok_koda_timer is not None and time.time() > kusok_koda_timer:
        #     kusok_koda_timer = None
        #     kusok_koda_timer2 = time.time() + 0.7

        # if kusok_koda_timer2 is not None:
        #     if time.time() > kusok_koda_timer2:
        #         kusok_koda_timer2 = None
        #     else:
        #         robot.serv(kusok_koda_right)
        # else:
        #     robot.serv(0)

        is_orange = Find_start_line(frame, frame_show, "orange")
        is_blue = Find_start_line(frame, frame_show, "blue")
        # ----------------- delete -------------------- #
        # if not flag_qualification and kusok_koda_timer is None:
        #     cord_red_banka, area_red_banka = Find_box(frame, frame_show, "red_up")
        #     if area_red_banka is not None:
        #         if area_red_banka > 7500 and cord_red_banka < SCREEN_WIDTH / 2: # 9500
        #             # robot.serv(60)
        #             kusok_koda_right = 30
        #             kusok_koda_timer = time.time() + 0.2 #0.2
        # if not flag_qualification and kusok_koda_timer is None:
        #     cord_green_banka, area_green_banka = Find_box(frame, frame_show, "green")
        #     if area_green_banka is not None:
        #         if area_green_banka > 2500 and cord_green_banka > SCREEN_WIDTH / 2:# 9500
        #             # robot.serv(60)
        #             kusok_koda_right = -30
        #             kusok_koda_timer = time.time() + 0.5 #0.2

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

        # if not flag_qualification:
        is_orange = Find_start_line(frame, frame_show, "orange")
        if is_orange:
            if after_povorot_delay_timer is None:
                after_povorot_delay_timer = time.time() + after_povorot_delay
            elif time.time() >= after_povorot_delay_timer:
                state = "Main move"

        put_telemetry(frame_show)
    elif state == "Right":
        # robot.lamp.rgb(0, 0, 1) 
        # timer = time.time() + abs((Find_black_line(frame, frame_show, direction) - porog_black_line_plus) * turn_k)
        # robot.serv(0)
        # # time.sleep(timer)
        # while time.time() < timer:
        #     robot.move(global_speed, 0, 100, False)

        cv2.putText(frame_show, "timer: " + str(round(time.time() - timer_state, 1)), (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)

        # едем прямо 2 секунды, а потом переключаемся в 1 стадию
        if time.time() < timer_state + pause_povorot:
            robot.move(global_speed, 0, 100, wait=False)
            robot.serv(-50)

        if time.time() > timer_state + pause_povorot:
            state = "Main move"

        if not flag_qualification:
            is_orange = Find_start_line(frame, frame_show, "blue")
            if is_orange:
                if after_povorot_delay_timer is None:
                    after_povorot_delay_timer = time.time() + after_povorot_delay
                elif time.time() >= after_povorot_delay_timer:
                    state = "Main move"

        put_telemetry(frame_show)
    elif state == "Main move":

        if count_lines >= max_lines:
            # if time.time()>timer_state+1:
            if timer_finish is None:
                timer_finish = time.time() + pause_finish
            if count_lines > 11:
                robot.move(-255, 0, 1000, wait=True)
                # robot.serv(0)
                # # robot.move(-255, 0, 500, wait=True)
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

            if time.time() - timer_povorot_delay > povorot_delay:
                is_orange = Find_start_line(frame, frame_show, "orange")
                if is_orange:
                    timer_povorot_delay = time.time()
                    state = "Right"
                    count_lines += 1
                    count_lines_proverka += 1
                    print(count_lines)

            if not flag_qualification:
                cord_red_banka, area_red_banka, d = Find_box(
                    frame, frame_show, "red_up")
                if area_red_banka is not None:
                    delta_banka = delta_red_plus
                    timer_banka = time.time()
                    if area_red_banka > go_back_banka_area and d:
                        go_back(35, time_go_back_banka, time_go_banka)  # 30
                        if count_lines_proverka < count_lines:
                            count_lines -= 1
                        if timer_finish is not None:
                            timer_finish += time.time() - timer_banka
                    elif area_red_banka > super_ditch_banka_area:
                        delta_banka *= super_ditch_banka_mult_plus
                    elif area_red_banka > ditch_banka_area:
                        delta_banka *= ditch_banka_mult_plus
                    #     # ditch_banka(ditch_banka_angle, time_ditch_banka)  # 30

                    #     if count_lines_proverka < count_lines:
                    #         count_lines -= 1
                    #     if timer_finish is not None:
                    #         timer_finish += time.time() - timer_banka
                    #         delta_banka 

                cord_green_banka, area_green_banka, d = Find_box(
                    frame, frame_show, "green")
                if area_green_banka is not None:
                    delta_banka = delta_green_plus
                    # print(area_green_banka)
                    timer_banka = time.time()
                    if area_green_banka > go_back_banka_area and d:
                        go_back(-35, time_go_back_banka, time_go_banka)
                        if count_lines_proverka < count_lines:
                            count_lines -= 1
                        if timer_finish is not None:
                            timer_finish += time.time() - timer_banka
                    elif area_green_banka > super_ditch_banka_area:
                        delta_banka *= super_ditch_banka_mult_plus
                    elif area_green_banka > ditch_banka_area:
                        delta_banka *= ditch_banka_mult_plus
                    #     ditch_banka(-ditch_banka_angle, time_ditch_banka)
                    #     if count_lines_proverka < count_line-s:
                    #         count_lines -= 1
                    #     if timer_finish is not None:
                    #         timer_finish += time.time() - timer_banka

                if area_green_banka is not None and area_red_banka is not None:

                    # delta_speed = -10

                    if area_red_banka > area_green_banka:
                        delta_banka = delta_red_plus
                    else:
                        delta_banka = delta_green_plus

        if direction == -1:

            if Find_black_box_right(frame, frame_show, "black"):
                go_back(-40, 500, 300)
            
            if time.time() - timer_povorot_delay > povorot_delay:
                is_blue = Find_start_line(frame, frame_show, "blue")
                if is_blue:
                    timer_povorot_delay = time.time()
                    state = "Left"
                    count_lines += 1
                    count_lines_proverka += 1
                    print(count_lines)
            if not flag_qualification:
                cord_red_banka, area_red_banka, d = Find_box(
                    frame, frame_show, "red_up")
                if area_red_banka is not None:
                    delta_banka = delta_red_minus
                    if area_red_banka > go_back_banka_area and d:
                        timer_banka = time.time()
                        go_back(35, time_go_back_banka, time_go_banka)
                        if count_lines_proverka < count_lines:
                            count_lines -= 1
                        if timer_finish is not None:
                            timer_finish += time.time() - timer_banka
                    elif area_red_banka > super_ditch_banka_area:
                        delta_banka *= super_ditch_banka_mult_minus
                        # print("Super")
                    elif area_red_banka > ditch_banka_area:
                        delta_banka *= ditch_banka_mult_minus
                    #     timer_banka = time.time()
                        
                    #     ditch_banka(ditch_banka_angle, time_ditch_banka)
                    #     if count_lines_proverka < count_lines:
                    #         count_lines -= 1
                    #     if timer_finish is not None:
                    #         timer_finish += time.time() - timer_banka

                cord_green_banka, area_green_banka, d = Find_box(
                    frame, frame_show, "green")
                if area_green_banka is not None:
                    delta_banka = delta_green_minus
                    # print(area_red_banka)
                    # print(area_green_banka)
                    if area_green_banka > go_back_banka_area and d:
                        timer_banka = time.time()
                        go_back(-35, time_go_back_banka, time_go_banka)
                        if count_lines_proverka < count_lines:
                            count_lines -= 1
                        if timer_finish is not None:
                            timer_finish += time.time() - timer_banka
                    elif area_green_banka > super_ditch_banka_area:
                        delta_banka *= super_ditch_banka_mult_minus
                        # print("Super")
                    elif area_green_banka > ditch_banka_area:
                        delta_banka *= ditch_banka_mult_minus
                    #     timer_banka = time.time()
                    #     # print('aboba')
                    #     ditch_banka(-ditch_banka_angle, time_ditch_banka)
                    #     if count_lines_proverka < count_lines:
                    #         count_lines -= 1
                    #     if timer_finish is not None:
                    #         timer_finish += time.time() - timer_banka

                if area_green_banka is not None and area_red_banka is not None:

                    # delta_speed = -10

                    if area_red_banka > area_green_banka:
                        delta_banka = delta_red_minus
                    else:
                        delta_banka = delta_green_minus

        # print("delta banka", delta_banka)

        # is_blue = Find_start_line(frame, "blue")

        max_y = Find_black_line(frame, frame_show, direction)
        # max_y = porog_black_line_minus
        # max_y2 = Find_black_line(frame, frame_show, -direction)
        if max_y > 0:
            # print(max_y)

            reg_move.set(0.6, 0.00001, 0.06)

            porog = porog_black_line_minus
            if direction > 0:
                porog = porog_black_line_plus
            
            # p = reg_move.apply(max_y2, max_y) * direction  # Lime
            p = reg_move.apply(porog,  max_y) * direction 
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
        if m == 32:
            flagfr = not flagfr

        if m == 81:
            low_set[0] -= step_hsv
        if m == 87:
            low_set[0] += step_hsv
        if m == 69:
            up_set[0] -= step_hsv
        if m == 82:
            up_set[0] += step_hsv
        if m == 65:
            low_set[1] -= step_hsv
        if m == 83:
            low_set[1] += step_hsv
        if m == 68:
            up_set[1] -= step_hsv
        if m == 70:
            up_set[1] += step_hsv
        if m == 90:
            low_set[2] -= step_hsv
        if m == 88:
            low_set[2] += step_hsv
        if m == 67:
            up_set[2] -= step_hsv
        if m == 86:
            up_set[2] += step_hsv

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
