import cv2
import time
import GPIORobot as rapi
import numpy as np
import json
from enum import Enum
import gmenu
from datetime import datetime
from regulators import Regulators

# === settings ====
speed = 180
brake_speed = 110
is_looking_for_obstacles = True
is_video_recording = True
is_bilateral_filter_applying = False
is_additional_task_enabled = True
camera_fps = 30
camera_quality = (640, 480)
mode = "Final"
# ==================

text_style_telemetry = { # style dict
	'foreground_color': (255, 255, 255),
	'background_color': (0, 0, 0)
}

text_style_results = { # style dict
	'foreground_color': (255, 255, 255),
	'background_color': (0, 0, 0)
}

statistics = { # statistics dict
	"stop_frames": 0,
	"wall_missed_frames": 0,
	"turn_left_frames": 0,
	"turn_right_frames": 0,
	"obstacles_frames": 0
}

fps_c = 0 # accumulation of frames
fps = 0 # framerate of previous second
timer = time.time() # main timer
lines = 0 # amount of detected lines
direction = 1 # if number is positive then clockwise. Otherwise, counterclockwise
direction_found = False # if robot has already detected his direction.
correction = -10 # correction of servo angle
running = False # if driving is active
time_start = 0

last_line_detection_timestamp = 0
line_detection_delay = 0.8
finish_duration = 1
finish_started = False
finish_started_timestamp = 0
finish_lines = 11
sections_time = []

banka_counter_last_banka_type = 'none'
banka_counter_red = 0
banka_counter_green = 0

# initialization of robot
robot = rapi.GPIORobotApi(acceleration_enabled=False, invert_servo=False, button_pin=15)
robot.set_camera(camera_fps, camera_quality[0], camera_quality[1], 0)
# light up RGB strip
robot.pixels[0] = (255, 0, 0)
robot.pixels[1] = (0, 255, 0)
robot.pixels[2] = (0, 0, 255)

# some stuff for hue fluent light of RGB strip
play_pixels_interval = rapi.Interval()
play_pixels_hue = 0
play_pixels_hue_shift = 20

@play_pixels_interval.callback # register interval callback
def play_pixels_interval_callback():
	global play_pixels_hue
	# change pixels colors with a little shift
	robot.pixels[0] = rapi.hsv_to_rgb(play_pixels_hue, 1, 1)
	robot.pixels[1] = rapi.hsv_to_rgb(play_pixels_hue + play_pixels_hue_shift, 1, 1)
	robot.pixels[2] = rapi.hsv_to_rgb(play_pixels_hue + play_pixels_hue_shift * 2, 1, 1)
	play_pixels_hue += 2
	play_pixels_hue %= 360

class HSV_work:
	"""HSV ranges saving, configuring and loading."""

	def __init__(self):
		self.colors = {} # create variable out of colors
		self.load_from_file() # load color from config file into valiable

	def reset(self):
		"""Set all HSV ranges to a default values.
		"""
		self.colors = {
			"orange": [[5, 0, 30], [15, 255, 255]], 
			"black": [[0, 0, 0], [180, 255, 90]], 
			"green": [[66, 132, 68], [86, 255, 246]], 
			"white": [[0, 0, 81], [180, 255, 254]], 
			"blue": [[93, 36, 0], [141, 255, 255]], 
			"red_up": [[170, 90, 90], [180, 255, 255]], 
			"red_down": [[0, 100, 100], [3, 255, 255]],
			"yellow": [[0, 0, 0], [180, 255, 255]]
		}
		self.try_make_files()
		self.save_to_file() # save default values to a config file

	def try_make_files(self, filename="colors.txt"):
		try:
			with open(filename, 'w') as outfile: # open file in a writing mode
				json.dump(self.colors, outfile) # save stringified dict of color to a config file
			with open(filename + ".copy", 'w') as outfile: # open copy file in a writing mode
				json.dump(self.colors, outfile) # save stringified dict of color to a copy of config file
		except:
			print("WARNING: Failed to create colors file. That means they are already exists.")

	def get_color(self, name):
		"""Get HSV range by color's name

		Arguments:
			name (str): Color's name.

		Returns:
			Tuple[Tuple[int, int, int], Tuple[int, int, int]]: HSV color range. If not found then [[0, 0, 0], [255, 255, 255]].
		"""
		data = [[0, 0, 0], [180, 255, 255]] # set HSV range to a default value
		if isinstance(self.colors, dict): # check if colors valiable is instance of dict
			if name in self.colors:
				data = self.colors[name] # set data to an existing HSV range
		return data

	def constrain(self, x, out_min, out_max): 
		"""Constrain value in a definite range.

		Arguments:
			x (Any): Input value.
			out_min (Any): Minimum value.
			out_max (Any): Maximum value

		Returns:
			Any: Constrained value in a range from `out_min` to an `out_max`.
		"""
		if x < out_min:
			return out_min # return min value if input value lower than minimum.
		elif out_max < x:
			return out_max # return max value if input value upper than maximum.
		else:
			return x # otherwise, return input value

	def set_color(self, name, data):
		"""Set HSV range by color's name.

		Args:
			name (str): Color's name.
			data (Tuple[Tuple[int, int, int], Tuple[int, int, int]]): HSV color range.
		"""
		for i in range(len(data)):
			for j in range(len(data[i])):
				if j == 0:
					data[i][j] = self.constrain(data[i][j], 0, 180)
				else:
					data[i][j] = self.constrain(data[i][j], 0, 255)
		self.colors[name] = data 

	def save_to_file(self, filename="colors.txt"):
		"""Save HSV ranges to a config file.

		Аргументы:
			filename (str, optional): Config file's name. Defaults to `"colors.txt"`.
		"""
		print("save to file")
		with open(filename, 'w') as outfile:
			json.dump(self.colors, outfile) 
		with open(filename + ".copy", 'w') as outfile:
			json.dump(self.colors, outfile) 

	def load_from_file(self, filename="colors.txt"):
		"""Load HSV rangef from a config file.

		Аргументы:
			filename (str, optional): Config file's name. Defaults to `"colors.txt"`.
		"""
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

hsv_work = HSV_work()
reg_move = Regulators(0, 0, 0, Ki_border=5)
reg_move.set(0.4, 0.00, 0.002)

menu = gmenu.GMenu()

def show_banka_position(position_y, color):
	"""show_banka_position"""
	top = 270
	bottom = 430
	c = round(rapi.arduino_map(position_y, 0, bottom - top, 0, 2))
	robot.pixels.fill((0, 0, 0))
	while c >= 0:
		robot.pixels[c] = color
		c -= 1

def find_black_line(frame, frame_show, direction, flag_draw=True):
	"""Получить координаты чёрной линии на изображении.

	Args:
		frame (CV2 frame): Исходное изображение.
		frame_show (CV2 frame): Изображение, на которое выводится графика.
		direction (int): Направление движения робота. 1 или -1.
		flag_draw (bool, optional): Рисовать графику на изображении. По умолчанию True.

	Returns:
		int: Y чёрной линии.
	"""
	global left_pix, mask
	x1, y1 = 640 - 20, 285 # Задаём 1-е координаты области определения чёрной линии слева.
	x2, y2 = 640, 480 # Задаём 2-е координаты области определения чёрной линии слева.

	if direction == 1: 
		x1, y1 = 0, 285 # Задаём 1-е координаты области определения чёрной линии справа.
		x2, y2 = 20, 480 # Задаём 1-е координаты области определения чёрной линии справа.
	
	# if flag_qualification:
	#     x1, y1 = 640 - 20, 200 # Задаём 1-е координаты области определения чёрной линии слева.
	#     x2, y2 = 640, 480 # Задаём 2-е координаты области определения чёрной линии слева.

	#     if direction == 1: 
	#         x1, y1 = 0, 200 # Задаём 1-е координаты области определения чёрной линии справа.
	#         x2, y2 = 20, 480 # Задаём 1-е координаты области определения чёрной линии справа.

	# вырезаем часть изображение
	frame_crop_show = frame_show[y1:y2, x1:x2]
	# рисуем прямоугольник на изображении
	cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)

	# _, mask = cv2.threshold(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 40, 255, cv2.THRESH_BINARY_INV)
	# mask = mask[y1:y2, x1:x2]
	mask = cv2.subtract(hsv_work.make_mask(frame[y1:y2, x1:x2], 'black'), hsv_work.make_mask(frame[y1:y2, x1:x2], "blue"))
	# mask -= hsv_work.make_mask(frame[y1:y2, x1:x2], "blue")
	# mask -= hsv_work.make_mask(frame[y1:y2, x1:x2], "green")
	_, contours, _ = cv2.findContours(
		mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

	# перебираем все найденные контур
	contours = [(i, cv2.boundingRect(i)) for i in contours if cv2.contourArea(i) > 100]
	if contours:
		contour, (_, y, _, h) = max(contours, key=lambda x: x[1][1] + x[1][3])
		if flag_draw:
			cv2.drawContours(frame_crop_show, contour, -1, (0, 0, 255), 2)
		left_pix = y + h
		return y + h
		
	return 0

def find_box(frame, frame_show, color, mode=0, flag_draw=True):
	"""mode - qualification"""
	x1, y1 = 20, 270  # Xanne
	# x1, y1 = 0, 100   #Lime
	x2, y2 = 620, 430
	if mode == 1:
		x1, y1 = 20, 350
		x2, y2 = 620, 430
	# вырезаем часть изображение
	# frame_crop = cv2.GaussianBlur(frame[y1:y2, x1:x2], (5, 5), 10)
	frame_crop = frame[y1:y2, x1:x2]
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
	contours = [i for i in contours if cv2.contourArea(i) > 200]
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
			# cv2.drawContours(frame_crop_show, contour, -1, c, 2)
			cv2.rectangle(frame_show, (x + x1, y + y1), (x + x1 + w, y + y1 + h), (0, 0, 0), 2)

			# cv2.putText(frame_show, str(round(area, 1)), (x + x1, y - 40 + y1),
			#             cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
			#             c, 2)
			# cv2.putText(frame_show, str(x + w/2) + " " + str(y + h), (x + x1, y - 60 + y1),
			#             cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
			#             c, 2)
		# frame_show[y1:y2, x1:x2] = frame_crop_show
		return x, y, w, h

	return None, None, None, None

def find_start_line(frame, frame_show, color, flag_draw=True):
	x1, y1 = 320 -20, 450
	x2, y2 = 320 + 20, 480

	xc1, yc1 = 320 -20, 450 - 60
	xc2, yc2 = 320 + 20, 480 - 60

	# check -----------------------
	# frame_crop = frame[yc1:yc2, xc1:xc2]
	# frame_crop_show = frame_show[y1:y2, x1:x2]
	# cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)
	# black = hsv_work.make_mask(frame_crop, "black")
	# mask = hsv_work.make_mask(frame_crop, color) - black
	# _, contours, _ = cv2.findContours(
	# 	mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	# for contour in contours:
	# 	area = cv2.contourArea(contour)
	# 	if area > 100:
	# 		return False
	# end check -------------------

	frame_crop = frame[y1:y2, x1:x2]
	frame_crop_show = frame_show[y1:y2, x1:x2]
	cv2.rectangle(frame_show, (x1, y1), (x2, y2), (0, 255, 0), 2)
	black = hsv_work.make_mask(frame_crop, "black")
	mask = hsv_work.make_mask(frame_crop, color) # - black
	_, contours, _ = cv2.findContours(
		mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	for contour in contours:
		area = cv2.contourArea(contour)
		if area > 100:
			if flag_draw:
				cv2.drawContours(frame_crop_show, contour, -1, (0, 0, 255), 2)
			return True

	return False

def find_stop(frame, frame_show, direction, flag_draw=True, mode=0) -> bool:
	x1, y1 = 280-30, 310
	x2, y2 = 300-30, 380

	x1_1, y1_1 = 340+30, 310
	x2_1, y2_1 = 360+30, 380

	if mode == 1:
		x1, y1 = 280-50, 310
		x2, y2 = 300-50, 380

		x1_1, y1_1 = 340+50, 310
		x2_1, y2_1 = 360+50, 380

	if direction == 1:
		frame_crop = frame[y1:y2, x1:x2]
	else:
		frame_crop = frame[y1_1:y2_1, x1_1:x2_1]

	trigger1 = False
	#trigger2 = False

	mask = cv2.subtract(hsv_work.make_mask(frame_crop, "black"), hsv_work.make_mask(frame_crop, "blue"))

	# на отфильтрованной маске выделяем контуры
	_, contours, _ = cv2.findContours(
		mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

	if contours:
		contour = max(contours, key=lambda x: cv2.contourArea(x))
		if cv2.contourArea(contour) > 100:
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
		# else:
		# 	cv2.rectangle(frame_show, (x1_1, y1_1), (x2_1, y2_1), (0, 0, 255) if trigger1 else (0, 255, 0), 2)
	return trigger1 # or trigger2

class Keys(Enum):
	ARROW_UP = 38
	ARROW_DOWN = 40
	UNKNOWN = 160
	W = 87
	A = 65
	S = 63
	D = 68
	SPACE = 32

def process_key(key_int: int):
	global speed, running
	if key_int != -1:
		try:
			key = Keys(key_int)
			if key == Keys.ARROW_DOWN:
				speed -= 1
				if speed < 0:
					speed = 0
			elif key == Keys.ARROW_UP:
				speed += 1
				if speed > 255:
					speed = 255
			elif key == Keys.SPACE:
				running = not running
			
		except ValueError:
			pass
			# print(key_int)

try:
	while True:
		robot.serv(0)
		robot.move(0)

		play_pixels_interval.start(0.1)
		robot.add_waiter(play_pixels_interval)
		while not running:
			process_key(robot.get_key())
			if robot.button():
				running = True
			frame = robot.get_frame(wait_new_frame=1)
			draw = frame.copy()
			fps_c += 1
			if time.time() > timer + 1:
				fps = fps_c
				fps_c = 0
				timer = time.time()

			menu.text(f"FPS: {fps}", **text_style_telemetry)
			menu.text(f"Speed: {speed}", **text_style_telemetry)
			menu.blit(draw)
			robot.set_frame(draw)
			robot.tick()

		robot.remove_waiter(play_pixels_interval)	
		if is_video_recording:
			video_writer = cv2.VideoWriter(f'/home/pi/{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.avi', cv2.VideoWriter_fourcc(*'DIVX'), 30, (640, 480))
		time_start = time.time()
		while running:
			process_key(robot.get_key())
			fps_c += 1
			if time.time() > timer + 1:
				fps = fps_c
				fps_c = 0
				timer = time.time()
				
			frame = robot.get_frame(wait_new_frame=1)

			if is_bilateral_filter_applying:
				frame = cv2.bilateralFilter(frame, 5, 80, 80)
			draw = frame.copy()

			black1 = find_black_line(frame, draw, direction)
			black2 = find_black_line(frame, draw, -direction)

			is_orange = find_start_line(frame, draw, 'orange')
			is_blue = find_start_line(frame, draw, 'blue')

			is_stop = find_stop(frame, draw, direction)
			
			x_green_banka, y_green_banka, w_green_banka, h_green_banka = find_box(frame, draw, "green")
			if x_green_banka is not None:
				delta_green = (300 + (y_green_banka + h_green_banka) * 1.4) - x_green_banka

			x_red_banka, y_red_banka, w_red_banka, h_red_banka = find_box(frame, draw, "red_up")
			if x_red_banka is not None:
				delta_red = (300 - (y_red_banka + h_red_banka) * 1) - (x_red_banka + w_red_banka)

			banka_p = 0
			if x_green_banka is not None and x_red_banka is not None:
				if y_red_banka + h_red_banka > y_green_banka + h_green_banka:
					banka_p = delta_red
					show_banka_position(y_red_banka + h_red_banka, (255, 0, 0))
				else:
					banka_p = delta_green
					show_banka_position(y_green_banka + h_green_banka, (0, 255, 0))
			elif x_green_banka is not None:
				banka_p = delta_green
				show_banka_position(y_green_banka + h_green_banka, (0, 255, 0))
			elif x_red_banka is not None:
				banka_p = delta_red
				show_banka_position(y_red_banka + h_red_banka, (255, 0, 0))
			else:
				robot.pixels.fill((0, 0, 0))
			banka_p *= 0.25

			if not direction_found:
				if is_orange:
					direction = 1
					lines += 1
					direction_found = True
					last_line_detection_timestamp = time.time()
					print("Direction 1")
				if is_blue:
					direction = -1
					lines += 1
					direction_found = True
					last_line_detection_timestamp = time.time()
					print("Direction -1")
			elif direction == 1 and is_orange and time.time() > last_line_detection_timestamp + line_detection_delay:
				robot.beep()
				if 0 < lines < 5:
					sections_time.append(time.time() - last_line_detection_timestamp)
				lines += 1
				print(f"Turn {lines - 1} of {finish_lines}")
				last_line_detection_timestamp = time.time()
				if is_additional_task_enabled and yellow_found:
					finish_lines += lines - 1
					print("Shit added.")
				yellow_found = False
			elif direction == -1 and is_blue and time.time() > last_line_detection_timestamp + line_detection_delay:
				robot.beep()
				if 0 < lines < 5:
					sections_time.append(time.time() - last_line_detection_timestamp)
				lines += 1
				print(f"Turn {lines - 1} of {finish_lines}")
				last_line_detection_timestamp = time.time()
				if is_additional_task_enabled and yellow_found:
					finish_lines += lines - 1
					print("Shit added.")
				yellow_found = False
			if is_video_recording and finish_started:
				menu.text(f"Finish now...")
			if lines > finish_lines and not finish_started:
				finish_started = True
				finish_started_timestamp = time.time()
			elif finish_started and time.time() >= finish_started_timestamp + sections_time[(finish_lines + 1) % 4] / 2:
				assert False, 'Finish'

			if is_stop:
				p = -90 * direction
				menu.text("STOP", **text_style_telemetry)
				statistics["stop_frames"] += 1
			elif is_looking_for_obstacles and banka_p != 0:
				p = banka_p
			elif black1 == 0 and black2 == 0:
				p = -90 * direction
				menu.text("AAA, sensors missed!", **text_style_telemetry)
				statistics["wall_missed_frames"] += 1
			elif abs(black2 - black1) < 10:
				p = 0
			else:
				p = reg_move.apply(black2, black1) * direction
				if black1 == 0:
					p = 90 * direction
					menu.text("right", **text_style_telemetry)
					statistics["turn_right_frames"] += 1
				if black2 == 0:
					p = -90 * direction
					menu.text("left", **text_style_telemetry)
					statistics["turn_left_frames"] += 1
			robot.serv(p + correction)
			robot.move(brake_speed if is_stop else speed)
			
			menu.text(f"Time: {(time.time() - time_start):.2f}s", **text_style_telemetry)
			menu.text(f"Lap: {lines // 4 + 1}", **text_style_telemetry)
			menu.text(f"Lines: {lines}", **text_style_telemetry)
			menu.text(f"FPS: {fps}", **text_style_telemetry)
			menu.text(f"Speed: {speed}", **text_style_telemetry)
			menu.blit(draw)
			if is_video_recording:
				video_writer.write(draw)
			robot.set_frame(draw, 15)
			robot.tick()
		if is_video_recording:
			video_writer.release()
finally:
	time_end = time.time()
	robot.move(0)
	robot.stop()
	robot.tick()
	if is_video_recording:
		video_writer.release()
	print(f"Passed in {time_end - time_start} seconds.")
	total_stats = [
		f"Total time is {(time_end - time_start):2f}s",
		f"Lines passed are {lines} of {finish_lines}",
		f"Laps passed are {lines // 4 + 1}",
		f"SST: {sections_time[3]:.2f}s, FST: {sections_time[0]:.2f}s, OST: {sections_time[1]:.2f}s, OFST: {sections_time[2]:.2f}s",
		f"Slowed down for {(statistics['stop_frames'] / camera_fps):.2f}s",
		f"Turned right for {(statistics['turn_right_frames'] / camera_fps):.2f}s",
		f"Turned left for {(statistics['turn_left_frames'] / camera_fps):.2f}s",
		f"Wall missed for {(statistics['wall_missed_frames'] / camera_fps):.2f}s",
		f"Obstacles detected for {(statistics['obstacles_frames'] / camera_fps):.2f}s",
		f"Driving mode was {mode}"
	]
	with open(f'/home/pi/{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log', 'x') as file:
		file.writelines(["Driving statistics:", ""])
		file.writelines(total_stats)
	while True:
		frame = robot.get_frame(wait_new_frame=1)
		for stat in total_stats:
			menu.text(stat, **text_style_results)
		menu.blit(frame)
		robot.set_frame(frame)