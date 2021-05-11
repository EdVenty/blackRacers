# blackRacers
Robot simulator http://robocenter.fun/robotsimulator.zip.

The robot connection program is `start_robot.py` (the `InetConnection.py` and `regulators.py` files are also required).

The main program for the robot is `wroracer.py`.

The robot API is `RobotAPI.py`.

Video uploaded to YouTube platform https://youtu.be/gwtpSeXLMqE

Robot electrical diagram - `` Schematic_BlackRacers_2021-05-08.png``.

Images of our team and robot can be found in `images/` folder.

____
## Description of the robot
Our robot is based on a bundle of Raspberry PI and PY Board platforms that communicate with each other via the UART protocol. Raspberry PI analyzes the image using computer vision, in particular the OpenCV library, supported by Intel; The PY Board controls the movement of the robot in space using a brushed motor with a gearbox. The robot signals its behavior by means of sound and light indication. Also, the robot can be given commands by means of contact sensors (including buttons).
The robot performs actions and tasks in accordance with the rules of the competition.

### Construction and electronic components
Our robot has a portable 12V battery powered by a bundle of three 18650 Li-ion power supplies.
Electronic components in the robot are connected by conductors connected by soldering.
The robot is equipped with a magnetic holder for the battery compartment. The robot chassis is based on a 1/16 scale toy model. It has oil-filled shock absorbers, the steering is similar to the control device on real cars. The camera on the robot is mounted on a stand modeled in a special program and printed on a high-precision 3D printer made of pla plastic.

### Programs
We created files for our robot to work in the programs JetBrains PyCharm Community Edition 2020 and Microsoft Visul Studio Code v.1.56.0 (the latest at the time of the release of this commit). Loaded onto the robot using a self-written script program start_robot.py The robot control program is based on the high-level dynamically typed programming language Python, which was chosen due to its simplicity, cross-platform and a huge range of libraries.

### Program arrangement:
The code consists of several blocks. Separate sections of the program perform different actions: looking for the starting line, adjusting and controlling the movement of the robot, finding the finish line, bypassing and protecting against collisions with banks, protecting against crashing into the sides of the field.
#### Sound indication of start
When starting up, the robot emits a long beep. This means that the robot has turned on, but the program has not yet loaded. After that, the program itself starts to run. After its launch, two short sound singals are released. The robot is then ready to drive. To start performing tasks and passing the route, you must press the button after the above-mentioned sound signals.
#### The first leg is the start.
The start consists of pressing the button on which the robot starts moving and driving to the turn line. If the line turns out to be blue, then the robot will move clockwise. Otherwise - counterclockwise.
#### The second section of the program is the main pass and avoidance of obstacles in the final heats.
To maintain the position relative to the rim, the position of the extremely 1 black point on the frame along the Y axis is used. Further, using the proportional-integral-differential controller, the robot aligns the positions relative to the rim. The position of the extreme point in the frame is determined depending on the direction the robot is going. To go around objects, it is used to find them in the HSV color range. When an object is found, the robot drives back and turns away from the obstacle.
#### The third section is finding the finish line and stopping.
After passing a certain number of turns, the robot realizes that it has driven three laps and stops at the start zone.
#### Wall collision protection
To protect against collision and, in case of impossibility to correctly adjust the direction of movement by the proportional-integral-differential regulator, a short-term backward movement and a turn from the wall in the opposite direction are used. Thus, even when leaving the required trajectory of movement, the robot will be able to align its position and return to the passage of the task.

### Computer vision and additional libraries
We used a camera and computer vision to identify the different sections of the track. The program used the CV2 library and various libraries necessary for its work. For precise selection of objects on the card, we used the HSV image color scheme and finding the pixels within the specified color limits.
Also, additional libraries were used for the correct and trouble-free operation of the program. A complete list of libraries is given below:
- OpenCV 2 - computer vision
- NumPy - work with arrays that store images captured from the camera thanks to the OpenCV library.
- Time - a library that allows you to find out the system time. Used in the robot program to create a delay during turns.
- RobotAPI - a self-written library of the Center for the Development of Robotics for connecting and communicating with a robot, as well as executing programs.
- JSON - processing data in JSON format. Used to store and quickly access the parameters of the HSV color range stored in the robot's memory.

### 3d Models
We used 3D printing in the design of the robot. The models were developed in Autodesk Inventor 2020, then exported in STL file format and printed on 3D printers.
3D models used in the robot:
- `` Knopka.stl ``
- `` korpus.stl ``

### Operating Instructions and Precautions
1) Always use charged 18650 batteries.
2) Do not turn the robot over to avoid detaching the battery compartment.
3) Do not throw or kick the robot. Don't hurt him physically.
4) Avoid getting water on the surface of the robot.
5) Press the red toggle button to start the robot. Press no more than 1 time per minute.
6) Use the robot only on the designated field. You can find more details about the field in the WRO 2020 regulations of the Future Engineers category.
7) Do not cover or touch the camera lens of the robot.
8) Do not interrupt or modify the electrical circuit.
9) Press the green start button only after one long beep and two short beeps.
10) Avoid getting toxic substances on the surface of the robot.
11) Avoid contact with acetone and other substances that corrode plastics, electronic boards, wire insulation, metals and hot melt glue.
12) Before starting the robot, check the safety of the electrical circuit and the presence of defects on the robot body.
13) Do not run the robot in poor lighting conditions. This will prevent it from recognizing colors from the camera.
14) Do not disassemble the robot body.
15) Do not remove the batteries while the robot is running.
16) Do not touch the robot while driving through the track, field, performing tasks, after pressing the "start" button.
17) Use only for persons over 12 years old.
18) If the robot shuts down unexpectedly, remove the batteries immediately for safety.
19) If the electronic components overheat, stop the robot immediately and remove the batteries.


# blackRacers
Robot simulator http://robocenter.fun/robotsimulator.zip.

Программа соединения с роботом - `start_robot.py` (также необходим файл `InetConnection.py` и `regulators.py`).

Главная программа для робота - `wroracer.py`.

API робота - `RobotAPI.py`.

Видео загруженное на платформу YouTube https://youtu.be/gwtpSeXLMqE

Электрическая схема робота -  ```Schematic_BlackRacers_2021-05-08.png```.

Фотографии нашей команды и фото робота можно найти в папке `images/`.

____
## Описание робота
Наш робот основан на связке платформ Raspberry PI и PY Board, коммуницирующие друг с другом посредством протокола UART. Raspberry PI анализирует картинку с помощью компьютерного зрения, в частности библиотеки OpenCV, поддерживающейся компанией Intel; PY Board контролирует движение робота в пространстве, используя коллекторный мотор с редуктором. Робот сигнализирует о своём поведении с помощью звуковой и световой индикации. Также роботу можно подавать команды посредством контактных сенсором (в том числе кнопки). 
Робот выполняет действия и задания, согласно регламенту соревнования.

### Конструкция и электронные компоненты
Наш робот имеет переносное аккумуляторное питание 12В, с помощью связки трёх Li-ion источников питания типа 18650.
Электронные компоненты в роботе соединяются за счёт проводников, соединённых между собой при помощью пайки.
Робот оснащён магнитным креплением для отсека с бататейками. Шасси робота основанны на игрушечной модели маштаба 1/16. Оно имеет маслонаполненные аммортизаторы, рулевое управление схожее с устройством управления на настоящих машинах. Камера на роботе закрепленна на стойке смоделированной в специальной программе и напечатанной на  высокоточном 3д принтере из pla пластика.

### Программы
Мы создавали файлы для работы нашего робота в программах JetBrains PyCharm Community Edition 2020 и Microsoft Visul Studio Code v.1.56.0 (последняя на момент релиза данного комминта). Загружали на робота посредством самописаного скрипта-программы start_robot.py Программа управления робота основана на высокоуровневом динамически типизированном языке программирования Python, который был выбран благодаря своей простоте, кроссплатформенности и наличии огромного ассортимента библиотек.

### Устройтво программы:
Код состоит из нескольких блоков. Отдельные участки программы выполняют разные действия: ищут стартовую линию, корректируют и управляют движением робота, нахождение финишной линии, обЪезд и защита от столкновения с банками, защита от врезания в борта поля.
#### Звуковая индикация запуска
При запуске робот издаёт длинный звуковой сигнал. Это означает, что робот включился, но программа ещё не подгрузилась. После этого программа сама начинает запускаться. После её запуска издаются два коротких звуковых сингала. После этого робот готов к проезду. Для старта выполнения заданий и прохождения трассы необходимо нажать на кнопку, после выше перечисленных звуковых сигналов.
#### Первый участок - это старт. 
Старт состоит из нажатия на кнопку, по которой робот начинает движение, и проезда до линии поворота. Если линия оказалась синей, то робот будет ехать по часовой стрелке. Иначе - против часовой. 
#### Второй участок программы - это основной проезд и объезд препятствий на финальных заездах.
Для сохранения положения относительно бортика используется распознование положения крайней точки черного цвета на кадре по оси Y. Далее с помощью пропорционально-интегрально-дифференциального регулятора робот выравнивает положения относительно бортика. Положение крайней точки в кадре определяется в зависимости от направления, куда едет робот. Для объезда объектов используется нахождения их в цветовом диапазоне HSV. При нахождении объекта робот отъезжает назад и отворачивает от препядствия.
#### Третий участок - это нахождения финиша и остановка. 
После проезда определённого количества поворотов робот понимает, что он проехал три круга и останавливается в зоне старта.
#### Защита от столкновения со стеной
Для защиты от столкновения и, в случае невозможности корректно отрегулировать пропорциально-интегрально-дифференциальным регулятором направление движения, используется кратковременный отъезд назад и отворот от стены в противоположную сторону. Таким образом, даже при слёте с необходимой траектории движения, робот сможет выравнить своё положение и вернуться к прохождению задания.

### Компьютерное зрение и дополнительные библиотеки
Для определения различных участков трассы мы исполользовали камеру и компьютерное зрение. В программе была использованна библиотека CV2 и различные библиотеки необходимые для её работы. Для точного выделения объектов на кардре мы использовали цветовую схему изображения HSV и нахождение пикселей в заданных цветовых пределах. 

Также были использованы дополнительные библиотеки для корректной и безотказной работы программы. Полный список библиотек приведён ниже:
- OpenCV 2 - компьютерное зрение
- NumPy - работа с массивами, в которых храняться изображения, снятые с камеры благодаря библиотеке OpenCV.
- Time - библиотека, позволяющая узнать системное время. Используется в программе робота для создания задержки во время поворотов.
- RobotAPI - самописная библиотека Центра Развития Робототехники для соединения и коммуникации с роботом, а также выполнения программ.
- JSON - обработка данных в формате JSON. Используется для хранения и быстрого доступа к сохранённым в памяти робота параметров диапазона цветов HSV.

### 3д Модели
В конструкции робота мы использовали 3Д печать. Модели были разработанны в программе Autodesk Inventor 2020, затем экспортированы в формате файла STL и напечатаны на 3Д принтерах.
3Д модели используемые в роботе:
- ``` Knopka.stl ```
- ``` korpus.stl ```

### Инструкция по эксплуатации и меры предосторожности
1) Всегда используйте заряженные аккумуляторы модели 18650.
2) Не переворачивайте робота во избежания отделения батерейного отсека.
3) Не кидайте и не пинайте робота. Не причиняйте ему физического вреда.
4) Избегайте попадание воды на поверхность робота.
5) Для запуска робота нажмите на красную кнопку-переключатель. Нажимайте не более 1 раза в минуту.
6) Используйте робота только на предназначенной поле. Подробнее вы можете ознакомиться с полем вы можете в регламенте WRO 2020 категории Future Engineers.
7) Не закрывайте и не трогайте линзу камеры робота.
8) Не обрывайте и не изменяйте электрическую схему.
9) Нажимайте на зелёную кнопку "старт" только после одного долгого звукового сигнала и двух коротких звуковых сигналов.
10) Избегайте попадания токсичных веществ на поверхность робота.
11) Избегайте попадания ацетона и других вещест, разъедающих пластмассу, электронные платы, изоляцию проводов, металлы и термоклей.
12) Перед стартом робота проверяйте сохранность электрической схемы и наличие деффектов на корпусе робота.
13) Не запускайте робота при плохом освещении. Это не позволит ему распознавать цвета по камере.
14) Не разбирайте корпус робота.
15) Не вытаскивайте аккумуляторы во время работы робота.
16) Не трогайте робота во время проезда трассы, поля, выполнения заданий, после нажатия кнопки "старт".
17) Использовать только лицам от 12 лет.
18) При неожиданном отключении робота сразу вытащите аккумуляторы для обеспечения безопасности.
19) При перегреве электронных компонентов немедленно прекратите работу робота и вытащите аккумуляторы.
____
## Контакты | Contacts
Edventy (Андрей Данильченко | Andrew Danilchenko) - edventyh@gmail.com
