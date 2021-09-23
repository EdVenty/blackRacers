# USER'S GUIDE
BR-2G
![Рисунок1](https://user-images.githubusercontent.com/80317959/129823910-77be7fb0-0ab2-45dd-8bca-df48c1715f8c.png)
BlackRacers
WRO 2021
---
## Repository Overview
1. Team photos: are located in the “Item number 1 - our photos” folder
	- Photo (`` Ours photo.jpeg `` )- the official photo of the team, and ( ``ours funny photo.jpg `` ) - funny
2. The robot's photos are located in the folder " Item number 2 - photos of the robot from 6 sides ”
	- Photos (` Robot_...jpg `) show the structure of the robot from different sides
3. The link to the video is located in the folder " Item number 3-Url the address of the YouTube video
	- Link ``Url the address of the YouTube video.md``
4. Diagrams: located in the folder "Item number 4-schematic diagrams of electromechanical components."
	- The electrical diagram is presented in the file: ``Schematic_BlackRacer. png``, the scheme was designed in the EasyEDA program, the file: ``SCH_BlackRacer_team. Json``
	- The kinetic scheme was compiled using GOST 'a, file:`` kinematic_scheme.jpg``
5. 3D models: they are located in the folder " Item number 5-3d models used in the robot”
	- `Knopka`: the model is laid out in two files(stl and itp), the model was designed in Autodesk Inventor 2020
	- `kuzov_BlackRacer`: the model is laid out in two files(stl and itp), the model was designed in Autodesk Inventor 2020
6. Files in the main partition:
	- `wroracer` -a program that runs on the robot and controls its actions
	- ` RoboAPI.py` - module of communication with the robot
	- ` README.md ` -a file with the user's guide and an overview of the repository
	- `` main.py`` - Pyboard program, responsible for the operation of the main program
	- `` module.py`` - Pyboard program responsible for motion functions
	
---

# Program arrangement:

The code consists of several blocks. Separate sections of the program perform different actions: looking for the starting line, adjusting and controlling the movement of the robot, finding the finish line, bypassing and protecting against collisions with banks, protecting against crashing into the sides of the field.

## Sound indication of start

When starting up, the robot emits a long beep. This means that the robot has turned on, but the program has not yet loaded. After that, the program itself starts to run. After its launch, two short sound singals are released. The robot is then ready to drive. To start performing tasks and passing the route, you must press the button after the above-mentioned sound signals.

## The first leg is the start.

The start consists of pressing the button on which the robot starts moving and driving to the turn line. If the line turns out to be blue, then the robot will move clockwise. Otherwise - counterclockwise.

## The second section of the program is the main pass and avoidance of obstacles in the final heats.

To maintain the position relative to the rim, the position of the extremely 1 black point on the frame along the Y axis is used. Further, using the proportional-integral-differential controller, the robot aligns the positions relative to the rim. The position of the extreme point in the frame is determined depending on the direction the robot is going. To go around objects, it is used to find them in the HSV color range. When an object is found, the robot drives back and turns away from the obstacle.

## The third section is finding the finish line and stopping.

After passing a certain number of turns, the robot realizes that it has driven three laps and stops at the start zone.

## Wall collision protection

To protect against collision and, in case of impossibility to correctly adjust the direction of movement by the proportional-integral-differential regulator, a short-term backward movement and a turn from the wall in the opposite direction are used. Thus, even when leaving the required trajectory of movement, the robot will be able to align its position and return to the passage of the task.

## Computer vision and additional libraries

We used a camera and computer vision to identify the different sections of the track. The program used the CV2 library and various libraries necessary for its work. For precise selection of objects on the card, we used the HSV image color scheme and finding the pixels within the specified color limits. Also, additional libraries were used for the correct and trouble-free operation of the program. A complete list of libraries is given below:

OpenCV 2 - computer vision
NumPy - work with arrays that store images captured from the camera thanks to the OpenCV library.
Time - a library that allows you to find out the system time. Used in the robot program to create a delay during turns.
RobotAPI - a self-written library of the Center for the Development of Robotics for connecting and communicating with a robot, as well as executing programs.
JSON - processing data in JSON format. Used to store and quickly access the parameters of the HSV color range stored in the robot's memory.

---

## Software Setup
To configure the use of the BR-2G robot, you will need to install the following software:
1. All subsequent programs have been tested and configured for the Windows 10 operating system, and the manual also describes the installation for this system. If you have another system installed, please use the Google search engine or its analogues to search for the installation of programs yourself. If you do not have a graphical system shell (command line), then the installation of client programs may differ significantly from the manual. We strongly recommend using the latest builds of systems not lower than Windows 10, otherwise, you will be responsible for the incorrect installation or malfunction of the robot components.

2. A program for communicating with devices via SSH and SFTP. For example, Bitvise SSH Client, which can be downloaded from the official website.
- To do this, follow the link https://www.bitvise.com/ssh-client-download and click the "Bitvise SSH Client Installer" button.

![image002](https://user-images.githubusercontent.com/80317959/129824608-fe3af042-959d-4ccf-aaa3-9312ea026d93.png)
- Open the downloaded installation file.

![image003](https://user-images.githubusercontent.com/80317959/129824636-e8de3e8c-bb1c-483a-855b-0d9d3c0097fc.png)
- After opening, allow the application to make changes on the device. Click "Yes".
- After the permission, you will have two windows:

![image005](https://user-images.githubusercontent.com/80317959/129824695-265f6b38-87fe-4b9e-ade9-dca456e5ce2c.png)

In a small window, check the box "I agree to accept all the terms of the License Agreement" and click "Install".

![image007](https://user-images.githubusercontent.com/80317959/129825008-e49fb9a8-92bf-45db-86e1-4af12a27a9df.png)
- If the installation is successful, you will see a window informing you about this. Click "OK"

![image009](https://user-images.githubusercontent.com/80317959/129825065-348fbeca-04e7-4684-9839-575cc17a7070.png)

3. Download the robot repository from the GitHub site.
- Follow the link https://github.com/EdVenty/blackRacers/archive/refs/heads/main.zip. A browser window will open with the robot's repository.
- Click on the green "Code" button.

![image011](https://user-images.githubusercontent.com/80317959/129826395-4ee6dedc-dc83-436f-965b-425b9c9f78ea.png)
- You will see the following window:

![image013](https://user-images.githubusercontent.com/80317959/129826444-9871a02d-922c-4320-82cf-2d65a1e288a2.png)

Click on the "Download ZIP" button to download the repository archive.
- The repository is downloaded to the archive in the ".zip " format.

![image014](https://user-images.githubusercontent.com/80317959/129826627-684fa183-e1f1-48c9-8475-d2be2f3f2759.png)
- If you do not have "WinRAR" or other archivers installed, then the following explorer window will open:

![image016](https://user-images.githubusercontent.com/80317959/129985270-b3985063-01fc-4f07-a192-b956ab9d7fde.png)
- Copy the single root folder and extract to any other folder on your disk.

![image018](https://user-images.githubusercontent.com/80317959/129985324-43f1e20e-9be0-4e70-a4d2-710ae2fcd5f5.png)
![image018](https://user-images.githubusercontent.com/80317959/129985341-140a5d90-bbbe-4e24-b57b-8a1d6e348ace.png)
- The repository is downloaded to your computer.
4. A program for communicating with the robot via the UART protocol, for downloading the firmware to the PyBoard microcontroller, for example, "PuTTY".
- Follow the link https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html. You will see a window for downloading the PuTTY installer. Find the following area (the labels may differ):

![image022](https://user-images.githubusercontent.com/80317959/129985851-20ef1c04-061d-4afa-99b1-0106ab5dd788.png)
- Click on the link to the right of the "64-bit x86" field, if you have a 64-bit system, otherwise- "32-bit x86". You should download the following file:

![image024](https://user-images.githubusercontent.com/80317959/129986069-605bf70e-d59b-412b-8215-d9bc005b6f69.png)
- Open it

![image026](https://user-images.githubusercontent.com/80317959/129986296-8776bb72-eb84-4783-977d-6702f69d060e.png)
- Click the "Next" button, and the following window will open:

![image028](https://user-images.githubusercontent.com/80317959/130030272-3a698115-ee36-4511-a88e-f467bb842c21.png)
- Click "Next". The following will appear:

![image030](https://user-images.githubusercontent.com/80317959/130030407-2f390cc3-8b28-4c80-920c-4b3b338ecaab.png)
- Click "Install". The application will request administrator rights, allow them to be granted by clicking "Yes". Further
the installation will take place.
- After successful installation, the following window will appear. Click "Finish".

![image032](https://user-images.githubusercontent.com/80317959/130030609-64e3354e-ea19-42e0-a4c4-2fbd59216a82.png)

5. Raspberry PI Imager.
- Download the installer from the official website at the link: https://downloads.raspberrypi.org/imager/imager_latest.exe.
You should download the following file:

![image033](https://user-images.githubusercontent.com/80317959/130031606-22081287-5b88-4826-a3c2-456c6e7bc2a1.png)
- Open the file and allow the installer access to administrator rights by clicking "Yes".
The following window should open for you.

![image035](https://user-images.githubusercontent.com/80317959/130031886-b7429d1f-504d-4a2c-b48a-a117bbfccf59.png)
- Click "Install", and, after installation, the following window will open. Click "Finish".

![image037](https://user-images.githubusercontent.com/80317959/130032500-3600d9b7-3f30-4c25-b77d-f89b9b0f11ed.png)
6. Install the "Python" runtime environment.
- Follow the link https://www.python.org/downloads/windows/ and find the item "Python 3.7.0 – June 27, 2018".

![image040](https://user-images.githubusercontent.com/80317959/130032611-b26346bb-3bce-4021-be20-45af27a90dd0.png)
- Click on the link "Download Winfows executable installer". The installer file will be downloaded from you.
- Open the downloaded file.

![image042](https://user-images.githubusercontent.com/80317959/130032738-bdb4e622-3bc8-4060-bd38-4f25fdbef2d7.png)
- The installer window will open for you. Click the check mark to the left of the "Add Python 3.7 to PATH" field.

![image045](https://user-images.githubusercontent.com/80317959/130032849-ac41a10a-6b06-4485-9e5e-d3d9674d8831.png)
- Click the "Install Now" button. Wait for the installation.

![image048](https://user-images.githubusercontent.com/80317959/130032917-3e350ddb-30ba-40ab-9966-665bd0496228.png)
- After the successful installation, you will see a window informing you about this. Click "Close".

![image050](https://user-images.githubusercontent.com/80317959/130032976-06563953-6dff-4e86-8617-baa6b6f3ac91.png)
---
## Download the software to the robot.
Next, you need to upload the necessary files and programs to the robot. To download to the robot, you will need the programs, the installation of which is shown above, as well as:
- USB-A (male) to micro-USB (male) wire (at least 15 centimeters).
- Ethernet cable
- SD card with at least 8 gigabytes of memory.
- A computer with an Ethernet port.

Installation progress:
1. Install Raspbian OS Lite on the SD card.
- Insert the SD card into the computer.
- Open the Raspberry PI Imager. You should see the following window:

![image052](https://user-images.githubusercontent.com/80317959/130036760-86111ffc-cba3-455e-b008-d119deb70e67.png)
- Click the "CHOOSE OS" button. You will see a window for selecting the Raspberry PI operating system.

![image054](https://user-images.githubusercontent.com/80317959/130036829-8c43f8da-4fbf-4732-8686-6d3b5e17c9b6.png)
- Click " Raspberry PI OS (other)". You will see the following:

![image056](https://user-images.githubusercontent.com/80317959/130036902-13bc52c9-aaa3-4b28-a84e-234d4cc7ec1c.png)
- Select " Raspberry PI OS Lite (32-bit)". The window will reset to the initial one, and the operating system will be selected.

![image058](https://user-images.githubusercontent.com/80317959/130039118-d082de0d-5b57-4934-9ebf-8a02349eafe1.png)
- Click "CHOOSE STORAGE" and select the SD card from the list.

![image060](https://user-images.githubusercontent.com/80317959/130037202-2712f860-457a-4e13-a194-310c9bde5f07.png)
- After selecting, the window will be reset. To write the operating system to a USB flash drive, "WRITE".

![image062](https://user-images.githubusercontent.com/80317959/130037245-2d7d4892-ad2d-4ba9-b9b7-3a805c124758.png)
- After recording and verifying the files, you will be able to get an SD card. Until this time, you can not remove the card!
2. Activation of the SSH protocol on the Raspberry PI.
- Insert the SD card into the computer.
- Open "Windows Explorer"
![image063](https://user-images.githubusercontent.com/80317959/130037470-93e5a7d9-c8c8-49ff-b880-6d53ba84cfd4.png)
![image066](https://user-images.githubusercontent.com/80317959/130037476-cadac61e-b1b4-48eb-9ea2-a68daea834b1.png)
- In the "Devices and disks" column, you will see a disk named "boot". Open it.

![image067](https://user-images.githubusercontent.com/80317959/130037922-34aafe94-851a-45a9-a305-ce9435dfa247.png)
Here are the important files for downloading the Raspberry PI operating system.
- Right-click on the white area and click "Create", select "Text Document".

![image069](https://user-images.githubusercontent.com/80317959/130037974-36c3c9c5-2ba9-4152-812a-0a930b25bf11.png)
- Name the document "ssh". Important: the file must not have any extension.
The contents of the file can also be left empty.

![image071](https://user-images.githubusercontent.com/80317959/130038044-5f948d15-eef6-4307-a058-a349b88d23d1.png)

If you do not display extensions (for example, the file "config.txt" does not have the extension ".txt", then use the following steps:
- Click the "View" button in the top menu of the explorer.

![image072](https://user-images.githubusercontent.com/80317959/130039251-2518f871-7e57-402d-9ecd-3987af256ce2.png)
- The following panel should open for you:

![image074](https://user-images.githubusercontent.com/80317959/130038473-b3867d52-a021-40e1-8a2d-0e764ce050e7.png)
- If you do not have a check mark in the "File name extensions" field, then put it.

- Remove the SD card from the computer and insert it into the Raspberry PI. Turn on the power of the Raspberry PI.
The system initialization process will begin, at this time, the yellow LED will blink actively.

- Wait 5-10 minutes for the system to be fully prepared. Subsequent launches will occur much faster.
After this period, you can proceed to the next steps.
3. Setting up the Raspberry PI camera.
- Connect the Raspberry PI to the computer using an Ethernet cable.
- Run the "Bitvise SSH Client" program. You will see the following window:

![image076](https://user-images.githubusercontent.com/80317959/130159295-83a713a2-face-42c9-a746-aadbc1ff434d.png)
- In the "Port" field, enter "22". In the "Host" field, enter "raspberrypi. local".

![image078](https://user-images.githubusercontent.com/80317959/130159339-ebf57c82-5935-452a-8115-950d2cbc8a4e.png)
- In the "Authentication" section, enter the word login "pi" in the "Login"field.
In the "Initial method" field, select the value "password".

![image080](https://user-images.githubusercontent.com/80317959/130159366-00e656bf-3bf0-44eb-8c2f-9e67c5411c45.png)
- Click the check mark in the "Store encrypted password in profile" field. The "Password" field will no longer be gray.
Enter the password "raspberry" there.

![image081](https://user-images.githubusercontent.com/80317959/130159413-d1fe3cc4-f436-4252-9fe4-7ab3afa2b22a.png)
- As a result, the top panel will look like this:

![image082](https://user-images.githubusercontent.com/80317959/130159463-acd2e5dc-0aa6-4d0e-8d27-d7a1de1ed958.png)
- At the bottom of the window, click the "Login" button. Wait until the Bitvise SSH Client connects to the Raspberry PI.

- If the following error appears in the logs after the connection expires
![image086](https://user-images.githubusercontent.com/80317959/130159719-affa7e3d-5172-47dc-bc34-515d0172f8ae.png), then change the values of the "Host" field to "raspberrypi".

- If the connection was successful, you will see a window. Click "Accept and Save".

![image088](https://user-images.githubusercontent.com/80317959/130159846-90bb0033-b5c3-47d4-b674-0ff50d583056.png)
- The panel will be updated on the left. Click on the next button ![image090](https://user-images.githubusercontent.com/80317959/130159918-f652285f-d1b9-4bfc-b56b-ca9628af0626.png).
You will see a window of the remote Raspberry PI terminal.
![image092](https://user-images.githubusercontent.com/80317959/130159980-04593e9d-f982-4c3a-8416-b69aa03b1b88.png)
Here you can write commands for the Raspberry PI.

- Connect your computer to the Internet, if you haven't already done so.
- Write the following commands in the terminal:

``sudo apt upgrade``

``sudo apt full-upgrade``
- After that, the Raspberry PI will be updated. This may take some time.
- Write the command in the terminal:

``sudo raspi-config``
- You will see the Raspberry settings window.
- Use the up and down arrows on the keyboard to move the red cursor to the "Interfacing Options" element.

![image094](https://user-images.githubusercontent.com/80317959/130160144-ac2261b7-9e09-404c-a0f0-0791a41ab375.png)
- Press "Enter". You will see the settings of the Raspberry PI interfaces.

![image096](https://user-images.githubusercontent.com/80317959/130160207-bc532b36-876c-4b98-b91f-c9030a170c29.png)
- Select "Camera" and press "Enter".

![image098](https://user-images.githubusercontent.com/80317959/130160246-bae943af-2137-4dc6-bf8f-3d23c7cff9b6.png)
- Press "Enter". So, you have turned on the camera on the Raspberry PI.
- Press "Esc" until the window becomes the original terminal again.
- Enter the command in the terminal:

``sudo reboot``
- The Raspberry PI will reboot and the camera will be able to work.

4. Configuring the server on Raspberry PI
- Repeat steps a-h of step 3.
- In the left menu, click on the button ![image100](https://user-images.githubusercontent.com/80317959/130160422-52ea7f28-95ef-4c31-840d-78a723dbb5bd.png)
You will see a window for transferring files to the Raspberry PI.
- In the "Remote files" part of the window, right-click on the white area and select "Create folder". Enter the name of the "robot" folder.

![image102](https://user-images.githubusercontent.com/80317959/130160445-cbcb99e0-de0d-4947-a3c5-3d8bbf4d8f48.png)
- Open the "robot" folder by double-clicking. It should be empty.
- Open the folder of the repository downloaded from GitHub. Select the 4 files shown:

![image104](https://user-images.githubusercontent.com/80317959/130160518-569ca432-42d9-4b6e-ae38-e81df7fdddcf.png)
And drag it to the Bitvise SFTP window, to the "Remote files" zone. They should be copied to the Raspberry PI and displayed in the "robot" folder.
- Open the terminal in the main window of the BItvise SSH Client.
- Write the command:

"sudo nano rc. local`
- The following window should open for you:

![image106](https://user-images.githubusercontent.com/80317959/130160617-f9d6d6a9-9dc9-47cd-94a9-158abd95a385.png)

-Before the line "_IP=$(hostname-I) || true", add the following line (you can move the cursor with the arrows on the keyboard):

``sudo modprobe bcm2835-v4l2``
- Everything together should look like this:

![image108](https://user-images.githubusercontent.com/80317959/130160661-f3ff7d62-8fa1-4c29-93a0-8c763eea3b03.png)
- Press "x" on the keyboard, then "y". The file will be saved.
- Restart the Raspberry PI.
5. PyBoard Firmware
- Connect the PyBoard to the computer with a micro-USB wire.
- Open Windows Explorer
- In the "Devices and disks" field, open the disk with the name "PYBFLASH".

![image110](https://user-images.githubusercontent.com/80317959/130160704-6e6b88f0-4072-4ce4-8b02-ac17029a8768.png)
- Open the downloaded repository from GitHub and copy 5 files from there.

![image112](https://user-images.githubusercontent.com/80317959/130160730-e903ea64-0eae-41f0-9247-c1e83f1fceb0.png)
- Copy them to the root of the disk "PYBFLASH".

![image113](https://user-images.githubusercontent.com/80317959/130160747-05ae1c7c-5b5f-4c59-951e-69a8deedf690.png)
- The red LED will light up on the PyBoard at this moment. Wait for it to turn off and disconnect the USB cable.
In case of early removal of the USB cable, all information will be erased from the PyBoard!
- PyBoard has been successfully stitched.
---
## Communication with the robot and launching programs
To communicate with the robot, the program "Robot Starter" is used, written by Yuri Glamazdin. You can find its start file in the GitHub repository folder.
Connecting the robot:
1. Connect to the robot's wifi network (the name may differ).

![image115](https://user-images.githubusercontent.com/80317959/130160857-b1fe5578-52d9-467c-9929-11ac50dff20d.png)

2. Open the GitHub repository folder. Run the file with the name "start_robot.py".

![image117](https://user-images.githubusercontent.com/80317959/130160876-59d59e76-c428-4675-98b9-14444dc7a12e.png)
- Load Start-select, load and run the program file.
- Start-download and run the already selected program file.
- Stop - stop the program.
- Raw-download and run the program file along the path on the computer "C:/Windows/System32/raw.py".
- Video-enable / disable the video.
- Connect to robot-select a robot and connect to it.
- When you click, a robot selection window appears:

![image120](https://user-images.githubusercontent.com/80317959/130161080-06dc16f7-3adc-47da-a9ed-eddbfb6d3def.png)

Many IP addresses are listed here. The IP of our robot is 192.168.4.1.
- To select a robot, click on its IP. After connecting, the following text is output to the console

![image122](https://user-images.githubusercontent.com/80317959/130161284-bc00bf8c-c7b0-46db-83f1-f2c2ecbbf2d0.png)

Otherwise – there will be no inscription.
- Console. Messages from the robot. All errors during program execution and text outputs (print) are output here.	
3. Start the program:
- Select the robot as shown in point 2. f.
- Click the "Load Start" button shown in point 2. a.
- In the window that opens, find the GitHub repository folder, select the file "wroracer_last_win.py". Click "Open".	
- ![image124](https://user-images.githubusercontent.com/80317959/130161366-c95fb988-52e0-43c4-be1e-80dfca4feae8.png)
- The program is running. Click on the button to start the ride.

---

# РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ
BR-2G 
![Рисунок1](https://user-images.githubusercontent.com/80317959/129823910-77be7fb0-0ab2-45dd-8bca-df48c1715f8c.png)
BlackRacers 
WRO 2021
---
## Обзор репозитория
1.	Фотографии команды: находятся в папке “Item number 1 - our photos”
-	Фото (`` Ours photo.jpeg ``)- официальное фото команды, а (`` ours funny photo.jpg ``)- забавное
2. Фотографии робота находятся в папке “Item number 2 - photographs of the robot from 6 sides”
-	Фотографии (`` Robot_…jpg `` ) показывают строение робота с разных сторон
3. Ссылка на видеоролик находится в папке “Item number 3 - Url the address of the YouTube video
-	Ссылка(`` Url the address of the YouTube video.md``)
4.	Схемы: находятся в папке “Item number 4 - schematic diagrams of electromechanical components.”
-	Электрическая схема представлена в файле: `` Schematic_BlackRacer.png``, схема проектировалась в программе EasyEda, файл: `` SCH_BlackRacer_team. Json``
-	 Кинетическая схема была составлена с использованием ГОСТ ‘а, файл: ``kinematic_scheme.jpg``
5.	3Д модели: они находятся в папке “Item number 5 - 3d models used in the robot”
-	`` Knopka``: модель выложена в двух файлах(stl и itp), модель проектировалась в  Autodesk Inventor 2020
-	`` kuzov_BlackRacer``: модель выложена в двух файлах(stl и itp), модель проектировалась в  Autodesk Inventor 2020
6.	Файлы в основном разделе:
-	`` RoboAPI.py``-модуль коммуникации с роботом
-	``start_robot.py``-файл запускающийся на главном компьютере 
-	`` README.md``-файл с руководством пользователя и обзором репозитория
-	`` main.py`` - программа на Pyboard, отвечает за работу главной программы
-	``module.py`` - программа на Pyboard, отвечающая за функции движения
	
---

# Устройство программы:
Код состоит из нескольких блоков. Отдельные участки программы выполняют разные действия: ищут стартовую линию, корректируют и управляют движением робота, нахождение финишной линии, объезд и защита от столкновения с банками, защита от врезания в борта поля.

## Звуковая индикация запуска

При запуске робот издаёт длинный звуковой сигнал. Это означает, что робот включился, но программа ещё не подгрузилась. После этого программа сама начинает запускаться. После её запуска издаются два коротких звуковых сингала. После этого робот готов к проезду. Для старта выполнения заданий и прохождения трассы необходимо нажать на кнопку, после выше перечисленных звуковых сигналов.

## Первый участок - это старт.

Старт состоит из нажатия на кнопку, по которой робот начинает движение, и проезда до линии поворота. Если линия оказалась синей, то робот будет ехать по часовой стрелке. Иначе - против часовой.

##Второй участок программы - это основной проезд и объезд препятствий на финальных заездах.

Для сохранения положения относительно бортика используется распознование положения крайней точки черного цвета на кадре по оси Y. Далее с помощью пропорционально-интегрально-дифференциального регулятора робот выравнивает положения относительно бортика. Положение крайней точки в кадре определяется в зависимости от направления, куда едет робот. Для объезда объектов используется нахождения их в цветовом диапазоне HSV. При нахождении объекта робот отъезжает назад и отворачивает от препядствия.

## Третий участок - это нахождения финиша и остановка.

После проезда определённого количества поворотов робот понимает, что он проехал три круга и останавливается в зоне старта.

## Защита от столкновения со стеной

Для защиты от столкновения и, в случае невозможности корректно отрегулировать пропорциально-интегрально-дифференциальным регулятором направление движения, используется кратковременный отъезд назад и отворот от стены в противоположную сторону. Таким образом, даже при слёте с необходимой траектории движения, робот сможет выравнить своё положение и вернуться к прохождению задания.

## Компьютерное зрение и дополнительные библиотеки

Для определения различных участков трассы мы исполользовали камеру и компьютерное зрение. В программе была использованна библиотека CV2 и различные библиотеки необходимые для её работы. Для точного выделения объектов на кардре мы использовали цветовую схему изображения HSV и нахождение пикселей в заданных цветовых пределах.

Также были использованы дополнительные библиотеки для корректной и безотказной работы программы. Полный список библиотек приведён ниже:

OpenCV 2 - компьютерное зрение
NumPy - работа с массивами, в которых храняться изображения, снятые с камеры благодаря библиотеке OpenCV.
Time - библиотека, позволяющая узнать системное время. Используется в программе робота для создания задержки во время поворотов.
RobotAPI - самописная библиотека Центра Развития Робототехники для соединения и коммуникации с роботом, а также выполнения программ.
JSON - обработка данных в формате JSON. Используется для хранения и быстрого доступа к сохранённым в памяти робота параметров диапазона цветов HSV.

---

## Настройка программного обеспечения
Для настройки использования робота BR-2G вам понадобится установить следующее программное обеспечение:
1. Все последующие программы были протестированы и настроены под операционную систему Windows 10, и руководство также описывает установку под это систему. Если у вас установлена другая система, пожалуйста, воспользуйтесь поисковой системой Google или её аналогами для самостоятельного поиска установки программ. Если у вас нету графической оболочки система (командная строка), то установка клиентских программ может существенно отличаться от руководства. Мы настоятельно рекомендуем использовать последние сборки систем не ниже Windows 10, в ином случае, ответственность за неправильную установку или неработоспособность компонентов робота будете нести вы.

2. Программа для коммуникации с устройствами по протоколу SSH и SFTP. Например, Bitvise SSH Client, которую можно скачать с официального сайта. 
	-	Для этого перейдите по ссылке https://www.bitvise.com/ssh-client-download и нажмите кнопку «Bitvise SSH Client 		Installer».
 
	![image002](https://user-images.githubusercontent.com/80317959/129824608-fe3af042-959d-4ccf-aaa3-9312ea026d93.png)
	-	Откройте скачанный установочный файл.
 
	![image003](https://user-images.githubusercontent.com/80317959/129824636-e8de3e8c-bb1c-483a-855b-0d9d3c0097fc.png)
	-	После открытия разрешите приложению вносить изменения на устройстве. Нажмите «Да».
	-	После разрешения, у вас появятся два окна: 

	![image005](https://user-images.githubusercontent.com/80317959/129824695-265f6b38-87fe-4b9e-ade9-dca456e5ce2c.png)
	
	В маленьком окне выставьте галочку в поле «I agree to accept all the terms of the License Agreement» и нажмите «Install».
  
	![image007](https://user-images.githubusercontent.com/80317959/129825008-e49fb9a8-92bf-45db-86e1-4af12a27a9df.png)
	-	В случае успешной установки у вас появится окно, сообщающее об этом. Нажмите "OK" 
	
	![image009](https://user-images.githubusercontent.com/80317959/129825065-348fbeca-04e7-4684-9839-575cc17a7070.png)

3. Загрузить репозиторий робота с сайта GitHub.
	-	Перейдите по ссылке https://github.com/EdVenty/blackRacers/archive/refs/heads/main.zip. У вас откроется окно браузера 		 с репозиторием робота.
	-	Нажмите на зелёную кнопку «Code». 
	
	![image011](https://user-images.githubusercontent.com/80317959/129826395-4ee6dedc-dc83-436f-965b-425b9c9f78ea.png)
	-	У вас откроется следующее окно: 
		
	![image013](https://user-images.githubusercontent.com/80317959/129826444-9871a02d-922c-4320-82cf-2d65a1e288a2.png)
	
	Нажмите на кнопку «Download ZIP» для загрузки архива репозитория.
	-	Репозиторий скачается в архив в формате «.zip». 
	
	![image014](https://user-images.githubusercontent.com/80317959/129826627-684fa183-e1f1-48c9-8475-d2be2f3f2759.png)
	-	Если у вас не установлен «WinRar» или другие архиваторы, то у вас откроется следующие окно проводника: 
	
	![image016](https://user-images.githubusercontent.com/80317959/129985270-b3985063-01fc-4f07-a192-b956ab9d7fde.png)
	-	Скопируйте единственную корневую папку и извлеките в любую другую папку на вашем диске.
	
	![image018](https://user-images.githubusercontent.com/80317959/129985324-43f1e20e-9be0-4e70-a4d2-710ae2fcd5f5.png)
	![image018](https://user-images.githubusercontent.com/80317959/129985341-140a5d90-bbbe-4e24-b57b-8a1d6e348ace.png)
	-	Репозиторий загружен на ваш компьютер.
4. Программа для коммуникации с роботом по протоколу UART, для загрузки прошивки в микроконтроллер PyBoard, напрмер, «PuTTY».
	-	Перейдите по ссылке https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html. У вас откроется окно загрузки установщика PuTTY. Найдите следующую область 			(надписи могут отличаться):  
	
	![image022](https://user-images.githubusercontent.com/80317959/129985851-20ef1c04-061d-4afa-99b1-0106ab5dd788.png)
	-	Нажмите на ссылку, справа от поля «64-bit x86», если у вас система 64 бита, иначе – «32-		bit x86». У вас должен скачаться следующий файл: 

	![image024](https://user-images.githubusercontent.com/80317959/129986069-605bf70e-d59b-412b-8215-d9bc005b6f69.png)
	-	Откройте его
	
	![image026](https://user-images.githubusercontent.com/80317959/129986296-8776bb72-eb84-4783-977d-6702f69d060e.png)
	-	Нажмите кнопку «Next», и у вас откроется следующее окно: 
	
	![image028](https://user-images.githubusercontent.com/80317959/130030272-3a698115-ee36-4511-a88e-f467bb842c21.png)
	-	Нажмите «Next». Покажется следующее:

	![image030](https://user-images.githubusercontent.com/80317959/130030407-2f390cc3-8b28-4c80-920c-4b3b338ecaab.png)
	-	Нажмите «Install». Приложение запросит права администратора, разрешите их предоставление нажатием кнопки «Да». Далее
		произойдет установка. 
	-	После успешной установки , появится следующее окно. Нажмите «Finish».

	![image032](https://user-images.githubusercontent.com/80317959/130030609-64e3354e-ea19-42e0-a4c4-2fbd59216a82.png)
	
5. Raspberry PI Imager.
	-	Загрузите установщик с официального сайта по ссылке: https://downloads.raspberrypi.org/imager/imager_latest.exe. 
		У вас должен скачаться следующий файл: 
		
	![image033](https://user-images.githubusercontent.com/80317959/130031606-22081287-5b88-4826-a3c2-456c6e7bc2a1.png)
	-	Откройте файл и разрешите установщику доступ к правам администратора, нажав «Да». 
		У вас должно открыться следующее окно. 
	
	![image035](https://user-images.githubusercontent.com/80317959/130031886-b7429d1f-504d-4a2c-b48a-a117bbfccf59.png)
	-	Нажмите «Install», и, после установки, откроется следующее окно. Нажмите «Finish».
	  
	![image037](https://user-images.githubusercontent.com/80317959/130032500-3600d9b7-3f30-4c25-b77d-f89b9b0f11ed.png)
6. Установка среды выполнения «Python».
	-	Перейдите по ссылке https://www.python.org/downloads/windows/ и найдите пункт «Python 3.7.0 – June 27, 2018».
	
	![image040](https://user-images.githubusercontent.com/80317959/130032611-b26346bb-3bce-4021-be20-45af27a90dd0.png)
	-	Нажмите на ссылку «Download Winfows executable installer». У вас скачается файл установщика.
	-	Откройте скачаный файл.
	
	![image042](https://user-images.githubusercontent.com/80317959/130032738-bdb4e622-3bc8-4060-bd38-4f25fdbef2d7.png)
	-	У вас откроется окно установщика. Нажмите галочку слева от поля «Add Python 3.7 to PATH».
	
	![image045](https://user-images.githubusercontent.com/80317959/130032849-ac41a10a-6b06-4485-9e5e-d3d9674d8831.png)
	-	Нажмите кнопку «Install Now». Ожидайте установки.
	
	![image048](https://user-images.githubusercontent.com/80317959/130032917-3e350ddb-30ba-40ab-9966-665bd0496228.png)
	-	После упешной установки у вас появится окно, сообщающее ою этом. Нажмите «Close».
	
	![image050](https://user-images.githubusercontent.com/80317959/130032976-06563953-6dff-4e86-8617-baa6b6f3ac91.png)
---
## Загрузка программного обеспечения на робота.
Далее, необходимо загрузить необходимые файлы и программы на робота. Для загрузки на робота вам понадобятся программы, установка которых показана выше, а также:
- USB-A (male) на micro-USB (male) провод (минимум 15 сантиметров).
- Ethernet кабель
- SD карта минимум на 8 гигабайт памяти.
- Компьютер с ethernet портом.

Ход установки:
1. Установите Raspbian OS Lite на SD карту.
	-	Вставьте SD карту в компьютер.
	-	Откройте Raspberry PI Imager. У вас должно появиться следующее окно: 
	
	![image052](https://user-images.githubusercontent.com/80317959/130036760-86111ffc-cba3-455e-b008-d119deb70e67.png)
	-	Нажмите кнопку «CHOOSE OS». У вас появится окно выбора операционной системы Raspberry PI. 
	
	![image054](https://user-images.githubusercontent.com/80317959/130036829-8c43f8da-4fbf-4732-8686-6d3b5e17c9b6.png)
	-	Нажмите «Raspberry PI OS (other)». У вас откроется следующее:
	
	![image056](https://user-images.githubusercontent.com/80317959/130036902-13bc52c9-aaa3-4b28-a84e-234d4cc7ec1c.png)
	-	Выберите «Raspberry PI OS Lite (32-bit)». Окно сбросится на начальное, а операционная система будет выбрана. 
	
	![image058](https://user-images.githubusercontent.com/80317959/130039118-d082de0d-5b57-4934-9ebf-8a02349eafe1.png)
	-	Нажмите «CHOOSE STORAGE» и выберите SD карту в списке. 
	
	![image060](https://user-images.githubusercontent.com/80317959/130037202-2712f860-457a-4e13-a194-310c9bde5f07.png)
	-	После выбора, окно сбросится. Для записи операционной системы на флешку «WRITE». 
	
	![image062](https://user-images.githubusercontent.com/80317959/130037245-2d7d4892-ad2d-4ba9-b9b7-3a805c124758.png)
	-	После записи и верификации файлов вы сможете достать SD карту. До этого времени, извлекать карту нельзя!
2. Активация SSH протокола на Raspberry PI.
	-	Вставьте SD карту в компьютер.
	-	Откройте «Проводник Windows» 
	![image063](https://user-images.githubusercontent.com/80317959/130037470-93e5a7d9-c8c8-49ff-b880-6d53ba84cfd4.png)
	![image066](https://user-images.githubusercontent.com/80317959/130037476-cadac61e-b1b4-48eb-9ea2-a68daea834b1.png)
	-	В графе «Устройства и диски» вы увидите диск, с названием «boot». Откройте его. 
	
	![image067](https://user-images.githubusercontent.com/80317959/130037922-34aafe94-851a-45a9-a305-ce9435dfa247.png)
	Здесь находятся важные файлы для загрузки операционной системы Raspberry PI.
	-	Нажмите правой кнопкой по белой области и нажмите «Создать», выберите «Текстовый документ». 
	
	![image069](https://user-images.githubusercontent.com/80317959/130037974-36c3c9c5-2ba9-4152-812a-0a930b25bf11.png)
	-	Назовите документ «ssh». Важно: файл не должен иметь никакого расширения. 
		Содержимое файла также можно оставить пустым.
		
	![image071](https://user-images.githubusercontent.com/80317959/130038044-5f948d15-eef6-4307-a058-a349b88d23d1.png)
	
	Если у вас не отображаются расширения (например, файл «config.txt» не имеет расширения «.txt», то используйте слудующие шаги:    
		-	Нажмите кнопку «Вид» в верхнем меню проводника. 
		
	![image072](https://user-images.githubusercontent.com/80317959/130039251-2518f871-7e57-402d-9ecd-3987af256ce2.png)
		-	У вас должна открыться следующая панель: 
		
	![image074](https://user-images.githubusercontent.com/80317959/130038473-b3867d52-a021-40e1-8a2d-0e764ce050e7.png)
		-	Если у вас не стоит галочка в поле «Расширения имен файлов», то поставьте её. 
	
	-	Извлеките SD карту из компьютера и вставьте в Raspberry PI. Включите питание Raspberry PI. 
		Начнётся процесс инициализации системы, в это время, жёлтый светодиод будет активно моргать.
		
	-	Подождите 5–10  минут для полной подготовки системы. Последующие запуски будут происходить намного быстрее. 
		После этого периода вы можете переходить в следующим шагам.
3.	Настройка камеры Raspberry PI.
	-	Подключите Raspberry PI к компьютеру, используя Ethernet кабель.
	-	Запустите программу «Bitvise SSH Client».  У вас откроется следующее окно:
		
	![image076](https://user-images.githubusercontent.com/80317959/130159295-83a713a2-face-42c9-a746-aadbc1ff434d.png)
	-	В поле «Port» введите «22». В поле «Host» введите «raspberrypi.local».
	
	![image078](https://user-images.githubusercontent.com/80317959/130159339-ebf57c82-5935-452a-8115-950d2cbc8a4e.png)
	-	В разделе «Authentication» в поле «Login» введите слово логин «pi». 
		В поле «Initial method» выберите значение «password». 
		
	![image080](https://user-images.githubusercontent.com/80317959/130159366-00e656bf-3bf0-44eb-8c2f-9e67c5411c45.png)
	-	Нажмите галочку в поле «Store enctypted password in profile». Поле «Password» перестанет быть серым. 
		Введите туда пароль «raspberry». 
		
	![image081](https://user-images.githubusercontent.com/80317959/130159413-d1fe3cc4-f436-4252-9fe4-7ab3afa2b22a.png)
	-	В итоге, верхняя панель будет выглядеть так: 
	
	![image082](https://user-images.githubusercontent.com/80317959/130159463-acd2e5dc-0aa6-4d0e-8d27-d7a1de1ed958.png)
	-	Внизу окна нажмте кнопку «Login». Ожидайте, пока Bitvise SSH Client не подключится к Raspberry PI.
	
	-	Если по истечении подключения в логах появляется следующая ошибка 
	![image086](https://user-images.githubusercontent.com/80317959/130159719-affa7e3d-5172-47dc-bc34-515d0172f8ae.png), то измените значения поля «Host» на «raspberrypi».
	
	-	Если подключение было успешным, у вас появится окно. Нажмите «Accept and Save». 
	
	![image088](https://user-images.githubusercontent.com/80317959/130159846-90bb0033-b5c3-47d4-b674-0ff50d583056.png)
	- 	Слева обновится панель. Нажмите на следующую кнопку ![image090](https://user-images.githubusercontent.com/80317959/130159918-f652285f-d1b9-4bfc-b56b-ca9628af0626.png). 
		У вас откроется окно удалённого терминала Raspberry PI. 
		![image092](https://user-images.githubusercontent.com/80317959/130159980-04593e9d-f982-4c3a-8416-b69aa03b1b88.png)
		Здесь вы можете писать команды для Raspberry PI.

	-	Подключите ваш компьютер к интернету, если ещё этого не сделали.
	-	Пропишите следующие команды в терминале:

		``sudo apt upgrade``
		
		``sudo apt full-upgrade``
	-	После этого произойдет обновление Raspberry PI. Это может занять время.
	-	Пропишите команду в терминале:
	
		``sudo raspi-config``
	-	У вас откроется окно настроек Raspberry.	
	-	Стрелками вверх и вниз на клавиатуре переместите красный курсор на элемент «Interfacing Options». 
	
	![image094](https://user-images.githubusercontent.com/80317959/130160144-ac2261b7-9e09-404c-a0f0-0791a41ab375.png)
	-	Нажмите «Enter». У вас откроются настройки интерфейсов Raspberry PI. 
	
	![image096](https://user-images.githubusercontent.com/80317959/130160207-bc532b36-876c-4b98-b91f-c9030a170c29.png)
	-	Выберите пункт «Camera» и нажмите «Enter».
	
	![image098](https://user-images.githubusercontent.com/80317959/130160246-bae943af-2137-4dc6-bf8f-3d23c7cff9b6.png)
	-	Нажмите «Enter». Таким образом, вы включили камеру на Raspberry PI.
	-	Нажмимайте «Esc» до тех пор, пока окно опять не станет исходным терминалом.
	-	Введите команду в терминал:

		``sudo reboot``
	-	Raspberry PI перезагрузится, и камера сможет работать.

4. Настройка сервера на Raspberry PI
	-	Повторите шаги a-h пункта 3.
	-	В левом меню нажмите на кнопку ![image100](https://user-images.githubusercontent.com/80317959/130160422-52ea7f28-95ef-4c31-840d-78a723dbb5bd.png)
		У вас откроется окно передачи файлов на Raspberry PI.
	-	В части окна «Remote files» нажмите на белую область правой кнопкой мыши и выберите «Create folder». Введите название папки «robot». 
	
	![image102](https://user-images.githubusercontent.com/80317959/130160445-cbcb99e0-de0d-4947-a3c5-3d8bbf4d8f48.png)
	-	Откройте папку «robot» двойным щелчком. Она дожна быть пустая.
	-	Откройте папку репизитория, скаченного с GitHub. Выделите 4 показанных файла:
	
	![image104](https://user-images.githubusercontent.com/80317959/130160518-569ca432-42d9-4b6e-ae38-e81df7fdddcf.png)
	И перетащите в окно Bitvise SFTP, в зону «Remote files». Они должны скопироваться на Raspberry PI и отображаться в папке «robot». 
	-	Откройте терминал в главном окне BItvise SSH Client. 
	-	Пропишите команду:
	
		``sudo nano rc.local``
	-	У вас должно открыться следующее окно: 
	
	![image106](https://user-images.githubusercontent.com/80317959/130160617-f9d6d6a9-9dc9-47cd-94a9-158abd95a385.png)

	-	Перед строчкой «_IP=$(hostname -I) || true» добавьте следующую строчку (перемещать курсор можо стрелками на клавиатуре):

		``sudo modprobe bcm2835-v4l2``
	-	Всё вместе должно выглядеть следующим образом: 
	
	![image108](https://user-images.githubusercontent.com/80317959/130160661-f3ff7d62-8fa1-4c29-93a0-8c763eea3b03.png)
	-	Нажмите на клавиатуре «x», затем «y». Файл сохранится. 
	-	Перезагрузите Raspberry PI.
5. Прошивка PyBoard
	-	Подключите PyBoard к компьютеру проводом micro-USB. 
	-	Откройте проводник Windows
	-	В поле «Устройства и диски» откройте диск с названием «PYBFLASH». 
	
	![image110](https://user-images.githubusercontent.com/80317959/130160704-6e6b88f0-4072-4ce4-8b02-ac17029a8768.png)
	-	Откройте скачаный репозиторий с GitHub и скопируйте оттуда 5 файлов. 
	
	![image112](https://user-images.githubusercontent.com/80317959/130160730-e903ea64-0eae-41f0-9247-c1e83f1fceb0.png)
	-	Скопируйте их в корень диска «PYBFLASH».
	
	![image113](https://user-images.githubusercontent.com/80317959/130160747-05ae1c7c-5b5f-4c59-951e-69a8deedf690.png)
	-	На PyBoard в этот момент загорится красный светодиод. Дождитесь его отключения и отключите USB кабель. 
		В случае досрочного извлечения USB кабеля, вся информация с PyBoard сотрётся!
	-	PyBoard успешно прошит.
---
## Связь с роботом и запуск программ
Для связи с роботом используется программа «Robot Starter», написанная Юрием Гламаздином. Её стартовый файл вы можете найти в папке репозитория GitHub. 
Подключение робота:
1.	Подключитесь к wifi сети робота (название может отличаться). 

![image115](https://user-images.githubusercontent.com/80317959/130160857-b1fe5578-52d9-467c-9929-11ac50dff20d.png)

2.	Откройте папку репозитория GitHub. Запустите файл с названием «start_robot.py». 

![image117](https://user-images.githubusercontent.com/80317959/130160876-59d59e76-c428-4675-98b9-14444dc7a12e.png)
-	Load Start - выбрать, загрузить и запустить файл программы.
-	Start - загрузить и запустить уже выбранный файл программы.
-	Stop - остановить программу.
-	Raw - загрузить и запустить файл программы по пути на компьютере «C:/Windows/System32/raw.py».
-	Video - включить/выключить видео.
-	Connect to robot - выбрать робота и подключиться к нему.
			-	При нажатии появляется окно выбора робота: 

![image120](https://user-images.githubusercontent.com/80317959/130161080-06dc16f7-3adc-47da-a9ed-eddbfb6d3def.png)

Здесь перечислены множество IP адресов. IP нашего робота – 192.168.4.1.

-	Для выбора робота нажмите на его IP. После подключения, выведется следующий текст в консоль

	![image122](https://user-images.githubusercontent.com/80317959/130161284-bc00bf8c-c7b0-46db-83f1-f2c2ecbbf2d0.png)
	
	В ином случае – надписи не будет.
-	Консоль. Сообщения с робота. Сюда выводятся все ошибки во время выполнения программы и выводы текста (print).	
3.	Запуск программы:
-	Выберите робота, как показано в пункте 2.f.
-	Нажмите кнопку «Load Start», показанную в пункте 2.a.
-	В открывшемся окне найдите папку репозитория GitHub, выберите файл «wroracer_last_win.py». Нажмите «Открыть».	

![image124](https://user-images.githubusercontent.com/80317959/130161366-c95fb988-52e0-43c4-be1e-80dfca4feae8.png)
-	Программа запущена. Нажмите на кнопку для начала езды.
