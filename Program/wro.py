import simulatorAPI as uapi
# import RobotAPI as rapi
import cv2
import numpy as np
import time

robot = uapi.UnityAPI().make_car_robot("Robot")
# robot = rapi.RobotAPI()

manual_angle = 0
manual_throttle = 0

e_old = 0
timer_move = 0

# текущая стадия программы
state = 1
# название стадий
state_names = ["Manual move", "Auto movement", "Left", "Forward", "Right"]

# фильтр черного цвета

timer_stop = 0

# количество поворотов
turn_counter = 0

print("Starting")

class Constants:
    wallRegulatorPoint = 126
    wallRegulatorProportionalCoefficient = 2
    wallRegulatorMinContourArea = 1
    wallRegulatorHSVLow = np.array([0, 0, 00])
    wallRegulatorHSVHigh = np.array([180, 80, 115])

    centerColorHSVLow = np.array([108, 99, 0])
    centerColorHSVHigh = np.array([180, 256, 256])
    centerColorTurnTime = 1.3


class WRO:
    def findCenterColor(self, frame) -> bool:
        found = False
        x1, y1 = 320 // 2 - 10, 200
        x2, y2 = 320 // 2 + 10, 230
        frame_crop = frame[y1:y2, x1:x2]
        # cv2.imshow("frame_crop", frame_crop)
        # рисуем прямоугольник на изображении
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        # переводим изображение с камеры в формат HSV
        hsv = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2HSV)
        # фильтруем по заданным параметрам
        mask = cv2.inRange(hsv, Constants.centerColorHSVLow, Constants.centerColorHSVHigh)
        # выводим маску для проверки
        # cv2.imshow("mask", mask)
        # на отфильтрованной маске выделяем контуры
        contours, hierarchy = cv2.findContours(
            mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        # перебираем все найденные контуры
        flag_line = False
        for contour in contours:
            # Создаем прямоугольник вокруг контура
            x, y, w, h = cv2.boundingRect(contour)
            # вычисляем площадь найденного контура
            area = cv2.contourArea(contour)
            if area > Constants.wallRegulatorMinContourArea:
                # отрисовываем найденный контур
                cv2.drawContours(frame_crop, contour, -1, (0, 0, 255), 2)
                # включаем зеленый свет
                robot.lamp.rgb(0, 1, 0)
                # robot.turn(p)
                # # даем газу,если скорость низкая
                # if robot.sensor.get_speed() < 7:
                #     robot.move(30)
                #     pass
                state = 2
                timer_stop = time.time()
                return True

        return False

    def regulateByWalls(self, frame):
        """Regulates robot's directiob by the wall regulator

        Args:
            frame (cv2 frame): Robot's frame
        """
        x1, y1 = 320 - 10, 0
        x2, y2 = 320, 240
        frame_crop = frame[y1:y2, x1:x2]
        cv2.imshow("Regulator frame crop", frame_crop)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # нахождение контуров
        hsv = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2HSV)
        # фильтруем по заданным параметрам
        mask = cv2.inRange(hsv, Constants.wallRegulatorHSVLow, Constants.wallRegulatorHSVHigh)
        # выводим маску для проверки
        # cv2.imshow("mask", mask)
        # на отфильтрованной маске выделяем контуры
        contours, hierarchy = cv2.findContours(
            mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            if area > 5:
                cv2.drawContours(frame_crop, contour, -1, (0, 0, 255), 2)

                e = Constants.wallRegulatorPoint - y
                p = e * Constants.wallRegulatorProportionalCoefficient
                robot.turn(p)  # повернуть

    def changeState(self, k: int):
        """Changes state by the keycodes

        Args:
            k (int): keycode

        Keycodes:
            49 - 1st state 
            50 - 2nd state 
            51 - 3rd state 
        """

        # если нажата клавиша 1
        if k == 49:
            # переключаем програму в 1 стадию
            state = 0
        # если нажата клавиша 2
        elif k == 50:
            # переключаем програму во 2 стадию
            state = 1
        elif k == 51:
            # переключаем програму в 3 стадию
            state = 2
            timer_stop = time.time()

    def detectDirection(frame) -> int:
        """Detects robot's direction

        Args:
            frame (cv2 frame): Robot's frame

        Returns:
            int: Robot's direction. 0 - not detected, 1 - clockwise, 2 - counterclockwise
        """
        

    def stage0(self, frame, k: int):
        if k == 119 or k == 246:
            manual_throttle += 5
            if manual_throttle > 100:
                manual_throttle = 100
        elif k == 115 or k == 251:
            manual_throttle -= 5
            if manual_throttle < -100:
                manual_throttle = -100
        elif k == 97 or k == 244:
            manual_angle -= 5
            if manual_angle < -35:
                manual_angle = -35
        elif k == 100 or k == 226:
            manual_angle += 5
            if manual_angle > 35:
                manual_angle = 35
        elif k == 32:
            # если нажата клавища пробел, сбрасываем угол и газ
            manual_angle = 0
            manual_throttle = 0
            robot.brake(100, 100)

        # отправляем команды на робота
        robot.move(manual_throttle)
        robot.turn(manual_angle)
        # телеметрия ручного управления
        cv2.putText(frame, "throttle: " + str(round(manual_throttle, 1)), (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)
        cv2.putText(frame, "angle: " + str(round(manual_angle, 1)), (10, 80),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)

    def stage2(self, frame):
        global state
        robot.lamp.rgb(0, 0, 1)
        cv2.putText(frame, "timer: " + str(round(time.time() - timer_stop, 1)), (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                    (0, 0, 255), 2)

        # едем прямо 2 секунды, а потом переключаемся в 1 стадию
        if time.time() < timer_stop + Constants.centerColorTurnTime:
            robot.move(50)
            robot.turn(-20)

        if time.time() > timer_stop + Constants.centerColorTurnTime:
            state = 1

    def stage1(self, frame) -> bool:
        global state, timer_stop, turn_counter
        # ищем цвет и рулим
        if turn_counter >= 4:
            return True
        if self.findCenterColor(frame):
            turn_counter += 1
            state = 2
            timer_stop = time.time()
        else:
            self.regulateByWalls(frame)
            robot.move(50)
        return False

    def main(self):
        while True:
            frame = robot.camera.frame()

            k = cv2.waitKey(1)
            self.changeState(k)

            if state == 2:
                pass
            if state == 0:
                # ручное управлениe
                self.stage0(frame, k)
            if state == 2:
                self.stage2(frame)
            if state == 1:
                # если True, то конец программы
                if self.stage1(frame):
                    robot.turn(0)
                    robot.brake(0, 0)
                    return
            # вывод телеметрии на экран
            cv2.putText(frame, "State: " + state_names[state], (10, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                        (0, 0, 255), 2)
            cv2.putText(frame, "Speed: " + str(round(robot.sensor.get_speed(), 1)), (10, 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                        (0, 0, 255), 2)

            cv2.imshow("Frame", frame)

# if __name__ == "__main__":
wro = WRO()
wro.main()