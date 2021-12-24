import json
import time
# import RPi.GPIO as GPIO

import cv2
import numpy as np
import regulators

import RobotAPI as rapi

dev_mode = True

# ======================= Константы =========================
GK = 10 # кривизна колес :)
time_go_banka = 800 # Устанавливаем время объезда банки
time_ditch_banka = 10
set_speed = 75
povorot_sub = -20


global_speed = 30 # Устанавливаем скорость робота 130
pause_finish = 1.3 # Устанавливаем пауза перед остановкой на финише 1.2521
black_line_porog_clockwise = 80 # Устанавливаем порог чёрной линии по часовой стрелке 305
black_line_porog_counterclockwise = 95 # Устанавливаем порог чёрной линии по часовой стрелке 305
# porog_black_line_plus = 55 # Устанавливаем порог чёрной линии против часовой стрелке
delta_green_plus = 15 # Устанавливаем угол объезда зелёной банки по часовой стрелке
delta_red_plus = -15 # Устанавливаем угол объезда красной банки по часовой стрелке
delta_green_minus = 10 # Устанавливаем угол объезда зелёной банки против часовой стрелке
delta_red_minus = -10 # Устанавливаем угол объезда красной банки против часовой стрелке
time_go_back_banka = 600 # Устанавливаем время отъезда от банки
pause_povorot = 0.4 # Устанавливаем максимальную задуржку на повороте
go_back_banka_area = 12000 # Устанавливаем площадь банки, при которой робот отъезжает
slow_banka_area = 6000
ditch_banka_area = 500 # Устанавливаем площадь банки, при которой робот обруливает
# break_banka_area = 4000
break_speed = global_speed
# ditch_banka_angle = 30
ditch_banka_mult_plus = 1
ditch_banka_mult_minus = 1
super_ditch_banka_mult_plus = 1.5
super_ditch_banka_mult_minus = 1.5
max_lines = 11
# povorot_delay = 17 / 11 * 0.6
povorot_delay = 0.5
speed_type = 'global'

next_line_need = False
manual_angle = 0 # Устанавливаем угол ручного управления (1- по часовой, -1 против часовой стрелки)
manual_throttle = 0 # Устанавливаем дроссель ручного управления (1- по часовой, -1 против часовой стрелки)
after_povorot_delay = 0.3
flag_video = True
fps = 0
fps_last = 0
fps_timer = time.time()
last_max_y = None
little_straight_time = 0
fragments = [False, False, False, False]
last_banka_delta = 0
after_banka_delay = 0.2 #sus
after_banka_timer = 0
tick_timer = 0
tick_old = 0

# PIN_GREEN = 36
# PIN_RED =38
# PIN_BLUE = 40
# DUTY = 100
# FREQ = 100
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(PIN_GREEN, GPIO.OUT)
# GPIO.setup(PIN_RED, GPIO.OUT)
# GPIO.setup(PIN_BLUE, GPIO.OUT)

# pwmGreen = GPIO.PWM(PIN_GREEN, FREQ)
# pwmRed = GPIO.PWM(PIN_RED, FREQ)
# pwmBlue = GPIO.PWM(PIN_BLUE, FREQ)
# pwmGreen.start(DUTY)
# pwmRed.start(DUTY)
# pwmBlue.start(DUTY)

flag_qualification = False # Если необходимо проехать квалификацию
if flag_qualification:  
    povorot_delay = 1
    global_speed = 80
    pause_finish = 1.2
    pause_povorot = 0.4
    max_lines = 11
    # pause_finish = 0.6 # Устанавливаем задержку финиша на квалификации
    # pause_povorot = 0.7 # Устанавливаем максимальную задуржку на повороте на квалификации 0.45
    black_line_porog_clockwise = 80
speed_manual = 85
# =================== Программные переменные ==================
state = "Manual move" # Устанавливаем текущую стадию на Ручное управление
count_lines_proverka = 0 # Устанавливаем счётчик линий на 0
direction = 0 # Устанавливаем направление по умолчанию на По часовой стрелке
timer_finish = None
timer_povorot_delay = 0
after_povorot_delay_timer = None
average_time = None
straight_timer = 0.1
straight_k = 0.1
p = 0
ff = False
banka_timer = 0
left_pix = 0

robot = rapi.RobotAPI(flag_pyboard=True) # инициализация робота
robot.set_camera(40, 640, 480, 0, -100) # установка разрешения камеры

# def set_color(r, g, b):
#     pwmRed.ChangeSutyCycle(100 - r)
#     pwmGreen.ChangeSutyCycle(100 - g)
#     pwmBlue.ChangeSutyCycle(100 - b)

# set_color(100, 0, 0)

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
            'red_up': [[96, 0, 0], [180, 255, 255]],
            'red_down': [[96, 0, 0], [180, 255, 255]]
        }
        self.try_make_files()
        self.save_to_file() # Сохранение сброшенных цветов в пзу робота

    def try_make_files(self, filename="colors.txt"):
        try:
            with open(filename, 'w') as outfile: # Открываем файл в режиме записи
                json.dump(self.colors, outfile) # Сохраняем в файл json-словарь цветовых диапазонов
            with open(filename + ".copy", 'w') as outfile: # Открываем файл-копию в режиме записи
                json.dump(self.colors, outfile) # Сохраняем в файл-копию json-словарь цветовых диапазонов
        except:
            print("WARNING: Failed to create colors file. That means they are already exists.")

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
# hsv_work.reset()

# def Find_threshold_line(frame, frame_show):
#     thrsh = cv2.adaptiveThreshold(cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY), 5, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 0)
#     cv2.drawContours(frame_show, thrsh, -1, (255, 0, 0))

def Find_stop(frame, frame_show, direction, flag_draw=True, mode=0):
    x1, y1 = 280-20, 280
    x2, y2 = 300-20, 350

    x1_1, y1_1 = 340+20, 280
    x2_1, y2_1 = 360+20, 350

    if mode == 1:
        x1, y1 = 280-20, 280
        x2, y2 = 300-20, 350

        x1_1, y1_1 = 340+20, 280
        x2_1, y2_1 = 360+20, 350

    if direction == 1:
        frame_crop = frame[y1:y2, x1:x2]
    else:
        frame_crop = frame[y1_1:y2_1, x1_1:x2_1]

    trigger1 = False
    #trigger2 = False

    mask = hsv_work.make_mask(frame_crop, "black")
    # на отфильтрованной маске выделяем контуры
    _, contours, _ = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if contours:
        contour = max(contours, key=lambda x: cv2.contourArea(x))
        if cv2.contourArea(contour) > 150:
            trigger1 = True

    # mask2 = hsv_work.make_mask(frame_crop1, "black")
    # # на отфильтрованной маске выделяем контуры
    # _, contours, _ = cv2.findContours(
    #     mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # # contours = [(i, cv2.boundingRect(i)) for i in contours]
    # if contours:
    #     contour = max(contours, key=lambda x: cv2.contourArea(x))
    #     if cv2.contourArea(contour) > 100:
    #         trigger2 = True

    if flag_draw:
        if direction == 1:
            cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 0, 255) if trigger1 else (0, 255, 0), 2)
        else:
            cv2.rectangle(frame_show, (x1_1, y1_1), (x2_1, y2_1), (0, 0, 255) if trigger1 else (0, 255, 0), 2)
    return trigger1# or trigger2
    # return False
    

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
    global left_pix
    x1, y1 = 640 - 20, 200 # Задаём 1-е координаты области определения чёрной линии слева.
    x2, y2 = 640, 480 # Задаём 2-е координаты области определения чёрной линии слева.

    if direction == 1: 
        x1, y1 = 0, 200 # Задаём 1-е координаты области определения чёрной линии справа.
        x2, y2 = 20, 480 # Задаём 1-е координаты области определения чёрной линии справа.
    
    if flag_qualification:
        x1, y1 = 640 - 20, 200 # Задаём 1-е координаты области определения чёрной линии слева.
        x2, y2 = 640, 480 # Задаём 2-е координаты области определения чёрной линии слева.

        if direction == 1: 
            x1, y1 = 0, 200 # Задаём 1-е координаты области определения чёрной линии справа.
            x2, y2 = 20, 480 # Задаём 1-е координаты области определения чёрной линии справа.

    # вырезаем часть изображение
    # frame_crop = frame[y1:y2, x1:x2]
    frame_crop_show = frame_show[y1:y2, x1:x2]
    # рисуем прямоугольник на изображении
    cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)

    _, mask = cv2.threshold(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 300, 255, cv2.THRESH_OTSU)
    mask = mask[y1:y2, x1:x2]
    mask = cv2.bitwise_not(mask)
    # mask = hsv_work.make_mask(frame_crop, "black")
    # на отфильтрованной маске выделяем контуры
    _, contours, _ = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # перебираем все найденные контур
    contours = [(i, cv2.boundingRect(i)) for i in contours if cv2.contourArea(i) > 300]
    if contours:
        contour, (_, y, _, h) = max(contours, key=lambda x: x[1][1] + x[1][3])
        if flag_draw:
            cv2.drawContours(frame_crop_show, contour, -1, (0, 0, 255), 2)
        left_pix = y + h
        return y + h
        
    return 0


def Find_start_line(frame, frame_show, color, flag_draw=True, p=False):
    global timer_povorot_delay, povorot_delay
    x1, y1 = 320 -60, 440
    x2, y2 = 320 + 60, 480
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
        if area > 100:
            if flag_draw:
                cv2.drawContours(frame_crop_show, contour, -1, (0, 0, 255), 2)
            if p: print(area)
            return True

    return False


def Find_box(frame, frame_show, color, mode=0, flag_draw=True):
    """mode - qualification"""
    x1, y1 = 0, 280  # Xanne
    # x1, y1 = 0, 100   #Lime
    x2, y2 = 640, 430
    if mode == 1:
        x1, y1 = 0, 285
        x2, y2 = 640, 430
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
    mask = hsv_work.make_mask(frame_crop, color)
    if color == 'red_up':
        mask += hsv_work.make_mask(frame_crop, 'red_down')
    # robot.set_frame(mask)
    # выводим маску для проверки
    cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # cv2.imshow("mask", mask)
    # на отфильтрованной маске выделяем контуры
    _, contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # перебираем все найденные контуры
    contours = [i for i in contours if cv2.contourArea(i) > 500]
    if contours:
        contour = max(contours, key=cv2.contourArea)
        # Создаем прямоугольник вокруг контура
        x, y, w, h = cv2.boundingRect(contour)
        # вычисляем площадь найденного контура
        area = cv2.contourArea(contour)
        
        if flag_draw:
            c = (255, 255, 255)
            if color == "green":
                c = (255, 255, 255)
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
delta_banka =0
hsv_frame = robot.get_frame(wait_new_frame=True)


def put_telemetry(frame_show):
    # вывод телеметрии на экран
    global fps, fps_last, fps_timer, left_pix, dev_mode
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
    cv2.putText(frame_show, "Frag: " + str(fragments), (10, 140), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (255, 255, 255), 2)
    cv2.putText(frame_show, "Speed: " + speed_type, (10, 160), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                (255, 255, 255), 2)
    cv2.putText(frame_show, str(left_pix), (10, 400), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 2)
    if not dev_mode:
        robot.set_frame(cv2.resize(frame_show, (320, 240)), 10)
    else:
        robot.set_frame(frame_show, 15)
    if ff:
        cv2.rectangle(frame_show, (380, 20), (620, 60), (0, 255, 0), -1)

# robot.serv(GK+180)
# robot.wait(500)
# robot.serv(GK+-180)
# robot.wait(500)
robot.serv(GK+0)


def go_back(angle, time1, time2):
    global timer_finish
    robot.serv(GK+angle)
    robot.move(-150, 0, time1, wait=False)
    robot.wait(time1)

    robot.serv(GK+0)
    # robot.serv(GK+-angle)
    robot.move(150, 0, time2, wait=False)
    robot.wait(time2)
    if timer_finish is not None:
        timer_finish += time1 / 1000 + time2 / 1000


robot.beep()
robot.wait(300)
robot.beep()

kusok_koda_timer = None
kusok_koda_timer2 = None
kusok_koda_right = None
before_povorot = False
orange_reached = False
# button_work = False

reg_move = regulators.Regulators(0, 0, 0, Ki_border=5)
reg_move.set(0.85, 0, 0.085)
if flag_qualification:
    reg_move.set(0.3, 0.000, 0.04)

def calc_banka(frame, frame_show):
    global direction
    delta_banka = 0
    near_banka = False
    if direction == 0:
        if not flag_qualification:
            x_green_banka, y_green_banka, area_green_banka, d = Find_box(frame, frame_show, "green")
            if area_green_banka is not None:
                # print(x_green_banka, y_green_banka, area_green_banka, d)
                if area_green_banka >= slow_banka_area:
                    near_banka = True
                delta_green_plus = 0
                # if x_green_banka < 550:
                delta_green_plus = (640 - x_green_banka)/30
                if y_green_banka >= 140:
                    delta_green_plus *= 2
                delta_banka = delta_green_plus
            x_red_banka, y_red_banka, area_red_banka, d = Find_box(frame, frame_show, "red_up")
            if area_red_banka is not None:
                if area_red_banka >= slow_banka_area:
                    near_banka = True
                delta_red_plus = 0
                # if x_red_banka > 90:
                delta_red_plus = x_red_banka/8
                if y_red_banka >= 140:
                    delta_red_plus *= 2
                delta_banka = delta_red_plus
                delta_banka = -delta_banka

            if area_green_banka is not None and area_red_banka is not None:
                if area_red_banka > area_green_banka:
                    delta_banka = delta_red_plus
                else:
                    delta_banka = delta_green_plus
    elif direction == 1:
        if not flag_qualification:
            x_green_banka, y_green_banka, area_green_banka, d = Find_box(frame, frame_show, "green")
            if area_green_banka is not None:
                # print(x_green_banka, y_green_banka, area_green_banka, d)
                if area_green_banka >= slow_banka_area:
                    near_banka = True
                delta_green_plus = 0
                # if x_green_banka < 550:
                delta_green_plus = (640 - x_green_banka)/13
                if y_green_banka >= 100:
                    delta_green_plus *= 10
                delta_banka = delta_green_plus
            x_red_banka, y_red_banka, area_red_banka, d = Find_box(frame, frame_show, "red_up")
            if area_red_banka is not None:
                if area_red_banka >= slow_banka_area:
                    near_banka = True
                delta_red_plus = 0
                # if x_red_banka > 90:
                delta_red_plus = x_red_banka/8
                if y_red_banka >= 140:
                    delta_red_plus *= 3
                delta_banka = delta_red_plus
                delta_banka = -delta_banka

            if area_green_banka is not None and area_red_banka is not None:
                if area_red_banka > area_green_banka:
                    delta_banka = delta_red_plus
                else:
                    delta_banka = delta_green_plus
            
    if direction == -1:
        if not flag_qualification:
            x_green_banka, y_green_banka, area_green_banka, d = Find_box(frame, frame_show, "green")
            if area_green_banka is not None:
                if area_green_banka >= slow_banka_area:
                    near_banka = True
                delta_green_plus = 0
                # if x_green_banka < 550:
                delta_green_plus = (640 - x_green_banka)/15
                if y_green_banka >= 140:
                    delta_green_plus *= 1.5
                delta_banka = delta_green_plus

            x_red_banka, y_red_banka, area_red_banka, d = Find_box(frame, frame_show, "red_up")
            if area_red_banka is not None:
                if area_red_banka >= slow_banka_area:
                    near_banka = True
                delta_red_plus = 0
                # if x_red_banka > 90:
                delta_red_plus = x_red_banka/10
                if y_red_banka >= 140:
                    delta_red_plus *= 2
                delta_banka = delta_red_plus
                delta_banka = -delta_banka

            if area_green_banka is not None and area_red_banka is not None:
                if area_red_banka > area_green_banka:
                    delta_banka = delta_red_plus
                else:
                    delta_banka = delta_green_plus
    return delta_banka, near_banka

while True:
    if state != old_state:
        timer_state = time.time()
        old_state = state
    tick_old = tick_timer
    tick_timer = time.time()
    if robot.button():
        # time.sleep(5)
        # if not button_work:
        state = "Move to line"
        button_work = True

        # else: # вырубить
        #     button_work = False
        #     state = "Manual move"

    frame = robot.get_frame(wait_new_frame=True)
    frame = cv2.flip(frame, -1)
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
    # elif k == 51:
    #     # переключаем програму во 2 стадию
    #     state = "Main move"
    #     robot.serv(GK+0)
    # elif k == 51:
    #     # переключаем програму в 3 стадию
    #     timer_stop = time.time()
    if time.time() - fps_timer >= 1:
        fps_last = fps
        fps = 0
        fps_timer = time.time()

    if state in ['Move to line', 'Main move'] and global_speed < set_speed:
        global_speed += 2
        
    fps += 1
    if state == "Manual move":
        # ручное управление
        # print(k)
        if k == 37:
            manual_serv = 45
            robot.serv(GK+manual_serv)
        if k == 39:
            manual_serv = -45
            robot.serv(GK+manual_serv)
        if k == 32:
            manual_serv = 0
            robot.serv(GK+manual_serv)
        if k == 38:
            robot.move(speed_manual, 0, 100, wait=False)
        if k == 40:
            robot.move(-speed_manual, 0, 100, wait=False)
        if k == 66:
            robot.beep()
            print('b')
        Find_stop(frame, frame_show, direction)
        # Find_threshold_line(frame, frame_show)

        x_green_banka, y_green_banka, area_green_banka, d = Find_box(frame, frame_show, "green")
        if area_green_banka is not None:
            # print(x_green_banka, y_green_banka, area_green_banka, d)
            delta_green_plus = 0
            if x_green_banka + 150 - y_green_banka < 500:
                delta_green_plus = (500 - x_green_banka)/8
            if y_green_banka > 90:
                delta_green_plus += (y_green_banka - 90)/10
            delta_banka = delta_green_plus

        x_red_banka, y_red_banka, area_red_banka, d = Find_box(frame, frame_show, "red_up")
        if area_red_banka is not None:
            delta_red_plus = 0
            if x_red_banka - 150 + y_red_banka > 140:
                delta_red_plus = (x_red_banka - 140)/8
            if y_red_banka > 90:
                delta_red_plus += (y_red_banka - 90)/10
            delta_banka = delta_red_plus

        if area_green_banka is not None and area_red_banka is not None:
            if area_red_banka > area_green_banka:
                delta_banka = delta_red_plus
            else:
                delta_banka = delta_green_plus

        # Find_black_box_right(frame, frame_show, "black")
        # Find_black_box_left(frame, frame_show, "black")
        # Find_box(frame, "red_up")
        # отправляем команды на робота
        # robot.move(manual_throttle, 0, 100, wait=False)
        # robot.serv(GK+manual_angle)
        # телеметрия ручного управления
        # cv2.putText(frame_show, "throttle: " + str(round(manual_throttle, 1)), (10, 60),
        #             cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
        #             (0, 0, 255), 2)
        # cv2.putText(frame_show, "angle: " + str(round(manual_angle, 1)), (10, 80),
        #             cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
        #             (0, 0, 255), 2)
        put_telemetry(frame_show)
    elif state == "Move to line":
        max_y = Find_black_line(frame, frame_show, 1)
        # max_y2 = black_line_porog_clockwise
        max_y2 = Find_black_line(frame, frame_show, -1)
            
        # if flag_qualification:
        #     ff = Find_stop(frame, frame_show, direction)
        # else:
        #     ff = Find_stop(frame, frame_show, direction, mode=1)
        delta_banka, near_banka = calc_banka(frame, frame_show)
        k = 2

        if delta_banka != 0:
            robot.serv(GK+delta_banka + k)
        else:
            p = reg_move.apply(constraint(max_y2, 75, 95), constraint(max_y, 75, 95))
            robot.serv(GK+p)
        robot.move(global_speed, 0, 100, wait=False)

        # if kusok_koda_timer is not None and time.time() > kusok_koda_timer:
        #     kusok_koda_timer = None
        #     kusok_koda_timer2 = time.time() + 0.7

        # if kusok_koda_timer2 is not None:
        #     if time.time() > kusok_koda_timer2:
        #         kusok_koda_timer2 = None
        #     else:
        #         robot.serv(GK+kusok_koda_right)
        # else:
        #     robot.serv(GK+0)

        is_orange = Find_start_line(frame, frame_show, "orange")
        is_blue = Find_start_line(frame, frame_show, "blue")
        # ----------------- delete -------------------- #
        # if not flag_qualification and kusok_koda_timer is None:
        #     cord_red_banka, area_red_banka = Find_box(frame, frame_show, "red_up")
        #     if area_red_banka is not None:
        #         if area_red_banka > 7500 and cord_red_banka < SCREEN_WIDTH / 2: # 9500
        #             # robot.serv(GK+60)
        #             kusok_koda_right = 30
        #             kusok_koda_timer = time.time() + 0.2 #0.2
        # if not flag_qualification and kusok_koda_timer is None:
        #     cord_green_banka, area_green_banka = Find_box(frame, frame_show, "green")
        #     if area_green_banka is not None:
        #         if area_green_banka > 2500 and cord_green_banka > SCREEN_WIDTH / 2:# 9500
        #             # robot.serv(GK+60)
        #             kusok_koda_right = -30
        #             kusok_koda_timer = time.time() + 0.5 #0.2

        if is_orange:
            direction = 1
            state = "Right"
            print("End state Move to line, go ", state)
        if is_blue:
            direction = -1
            black_line_porog_clockwise += 10
            state = "Left"
            # frame1 = frame
            print("End state Move to line, go ", state)
        put_telemetry(frame_show)
    elif state == "Left":
        cv2.putText(frame_show, "timer: " + str(round(time.time() - timer_state, 1)), (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)
        timer_povorot_delay = time.time()
        # едем прямо 2 секунды, а потом переключаемся в 1 стадию
        if time.time() < timer_state + pause_povorot:
            # speed = global_speed if Find_stop(frame, frame_show, direction, mode=1 if flag_qualification else 0) else global_speed
            # fs = Find_stop(frame, frame_show, direction, mode=1 if flag_qualification else 0)
            # speed = global_speed if fs else global_speed
            # if count_lines >= 5:
            #     if not fragments[(count_lines-1) % 4]:
            #         speed_type = 'povorot'
            #         robot.move(global_speed, 0, 100, wait=False)
            #     else:
            #         speed_type = 'stop' if fs else 'low'
            #         robot.move(speed, 0, 100, wait=False)
            # else:
            #     robot.move(speed, 0, 100, wait=False)
            if count_lines == 0:
                robot.move(global_speed+povorot_sub, 0, 100, wait=False)
            else:
                robot.move(global_speed+povorot_sub, 0, 100, wait=False) 
            # if time.time() < little_straight_time: 
            #     after_povorot_delay_timer = None
            #     robot.serv(GK+0) 
            # else:
            if flag_qualification:
                robot.serv(GK+15)
            else:
                robot.serv(GK+45)
        else:
            next_line_need = True
            state = "Main move"

        # 
        is_orange = Find_start_line(frame, frame_show, "orange")
        if is_orange:
            if after_povorot_delay_timer is None:
                after_povorot_delay_timer = time.time() + after_povorot_delay
            elif time.time() >= after_povorot_delay_timer:
                state = "Main move"
        if not flag_qualification:
            x_green_banka, y_green_banka, area_green_banka, d = Find_box(frame, frame_show, "green", 1)
            x_red_banka, y_red_banka, area_red_banka, d = Find_box(frame, frame_show, "red_up", 1)
            if area_green_banka is not None or area_red_banka is not None:
                if area_red_banka is not None and x_red_banka > 10:
                    state = "Main move"
                    if count_lines < 5:
                        fragments[count_lines-1] = True
                    print("Bankus in povorotus")
                    next_line_need = True

            # cord_red_banka, area_red_banka, d = Find_box(
            #             frame, frame_show, "red_up")
            # if area_red_banka is not None:
            #     if area_red_banka > ditch_banka_area:
            #         state = "Main move"

            # cord_green_banka, area_green_banka, d = Find_box(
            #             frame, frame_show, "green")
            # if area_green_banka is not None:
            #     if area_green_banka > ditch_banka_area:
            #         state = "Main move"
        straight_timer = time.time() 


        put_telemetry(frame_show)
    elif state == "Right":
        cv2.putText(frame_show, "timer: " + str(round(time.time() - timer_state, 1)), (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)
        timer_povorot_delay = time.time()
        # едем прямо 2 секунды, а потом переключаемся в 1 стадию
        if time.time() < timer_state + pause_povorot:
            # speed = global_speed if Find_stop(frame, frame_show, direction, mode=1 if flag_qualification else 0) else global_speed
            # fs = Find_stop(frame, frame_show, direction, mode=1 if flag_qualification else 0)
            # speed = global_speed if fs else global_speed
            # if count_lines >= 5:
            #     if not fragments[(count_lines-1) % 4]:
            #         speed_type = 'povorot'
            #         robot.move(global_speed, 0, 100, wait=False)
            #     else:
            #         speed_type = 'stop' if fs else 'low'
            #         robot.move(speed, 0, 100, wait=False)
            # else:
            #     robot.move(speed, 0, 100, wait=False)
            if count_lines == 0:
                robot.move(global_speed+povorot_sub, 0, 100, wait=False)
            else:
                robot.move(global_speed+povorot_sub, 0, 100, wait=False)
            # if time.time() < little_straight_time:
            #     after_povorot_delay_timer = None
            #     robot.serv(GK+0)
            # else:
            if flag_qualification:
                robot.serv(GK+-30)
            else:
                robot.serv(GK+-58)
        else:
            state = "Main move"
        
        # if before_povorot and Find_black_line(frame, frame_show, -direction) > 250:
        #     state = "Main move"

        if not flag_qualification:
            is_orange = Find_start_line(frame, frame_show, "blue")
            if is_orange:
                if after_povorot_delay_timer is None:
                    after_povorot_delay_timer = time.time() + after_povorot_delay
                elif time.time() >= after_povorot_delay_timer:
                    state = "Main move"

            # if not orange_reached:
            #     is_orange = Find_start_line(frame, frame_show, "orange")

            x_green_banka, y_green_banka, area_green_banka, d = Find_box(frame, frame_show, "green", 1)
            x_red_banka, y_red_banka, area_red_banka, d = Find_box(frame, frame_show, "red_up", 1)
            if area_green_banka is not None or area_red_banka is not None:
                state = "Main move"
                if count_lines < 5:
                    fragments[count_lines-1] = True
                print("Bankus in povorotus")

         
        straight_timer = time.time()
        

        put_telemetry(frame_show)
    elif state == "Main move":

        orange_reached = False
        if count_lines >= max_lines:
            # if time.time()>timer_state+1:
            if timer_finish is None:
                timer_finish = time.time() + pause_finish
            if count_lines > max_lines:
                robot.serv(GK+0)
                robot.move(-200, 0, 1000, wait=True)
                # robot.serv(GK+0)
                # # robot.move(-255, 0, 500, wait=True)
                exit(0)

            if timer_finish is not None:
                if time.time() > timer_finish:
                    global_speed = 0
                    robot.beep()
                    robot.beep()
                    state = "Finish"

        delta_banka = 0
        delta_speed = 0
        peed = global_speed
        near_banka = False
        delta_banka, near_banka = calc_banka(frame, frame_show)
        # max_y = Find_black_line(frame, frame_show, direction)
        if flag_qualification:
            max_y2 = Find_black_line(frame, frame_show, -direction)
            # if max_y2 == 0:
            #     max_y2, max_y = max_y, max_y2
            max_y = Find_black_line(frame, frame_show, direction)
        else:
            if direction == 1:
                max_y2 = black_line_porog_clockwise
            else:
                max_y2 = black_line_porog_counterclockwise
            max_y = Find_black_line(frame, frame_show, direction)
            
        if flag_qualification:
            ff = False
        else:
            ff = Find_stop(frame, frame_show, direction, mode=1)
        speed = global_speed if ff else global_speed
        # if abs(max_y2 - max_y) < 10:
        #     p = 0
        # else:
        p = reg_move.apply(max_y2, max_y)
        p = -120*direction if ff else p * direction

        if timer_finish is not None and ff:
            timer_finish += tick_timer - tick_old

        if count_lines >= 5:
            speed_type = 'global'
        elif ff:
            speed_type = 'stop'
        else:
            speed_type = 'low'
        
        # if next_line_need:
        #     if direction == -1:
        #         is_orange = Find_start_line(frame, frame_show, "orange")
        #         if is_orange:
        #             count_lines+= 1
        #             count_lines_proverka+= 1
        #             print("+1")
        #             next_line_need = False

        if direction == 1:
            if time.time() - timer_povorot_delay > povorot_delay:
                is_orange = Find_start_line(frame, frame_show, "orange", p=True)
                if is_orange:
                    before_povorot = True
                    count_lines+= 1
                    count_lines_proverka+= 1
                    print("RIGHT")
                    state = "Right"
                    
                    # little_straight_time = time.time() + p*-0.5
                    # print(count_lines, p*-10)
        else:
            if time.time() - timer_povorot_delay > povorot_delay:
                is_blue = Find_start_line(frame, frame_show, "blue", p=True)
                if is_blue:
                    before_povorot = True
                    count_lines+= 1
                    count_lines_proverka+= 1
                    state = "Left"
                    print("LEFT")

        if delta_banka != 0 and not flag_qualification:
            last_banka_delta = delta_banka
            after_banka_timer = time.time() + after_banka_delay
            robot.serv(GK+delta_banka)

        else:
            if time.time() < after_banka_timer:
                robot.serv(GK+0)
            else:
                # robot.serv(GK+p+k)
                # if -5 < p < 5:
                #     robot.serv(GK+0)
                # else:
                robot.serv(GK+p+k)

        # if delta_banka == 0:
        #     robot.serv(GK+p)
        # else:
        #     robot.serv(GK+delta_banka)
        
        robot.move(speed, 0, 100, wait=False)
       

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