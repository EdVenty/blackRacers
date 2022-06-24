# BlackRacers | WRO 2022 Future Engineers

Contacts:

- Andrew Danilchenko - email: <edventyh@gmail.com> discord: Edventy#6866
- Matvey Korabeynikov - email: <korrabeynikov@mail.ru>

----

## Repository Overview

1. 3D models: they are located in the folder "3D модели”

- `Servo_1`: the model is laid out in two files(stl and itp), the model was designed in Autodesk Inventor 2020
- `place`: the model is laid out in two files(stl and itp), the model was designed in Autodesk Inventor 2020
- `camera`: the model is laid out in two files(stl and itp), the model was designed in Autodesk Inventor 2020
- `korpus`: the model is laid out in two files(stl and itp), the model was designed in Autodesk Inventor 2020

2. Team photos: are located in the “Фото команды” folder
	- Photo (``Our photo.jpg``)- the official photo of the team, and (``our funny photo.jpg``) - funny
3. Robot documentation is located in the "Другое":
	- `documentation.md` - description of the process of preparing the robot for races
5. The robot's photos are located in the folder "photo”
	- Photos (` Robot_...jpg `) show the structure of the robot from different sides
6. Diagrams: located in the folder "Схемы"
	- The electrical diagram is presented in the file: ``Schematic_BlackRacer.pdf``, the scheme was designed in the EasyEDA program, the file: ``SCH_BlackRacer.json``
	- Kinetic diagram compiled using industry standards, file:``kinematic_scheme.jpg``
7. Control software: located in the folder "Программы":

- `RoboAPI.py` - module of communication with the robot.
- `InetConnection.py`- server creation file on Raspberry Pi.
- `start_robot.py` - program for convenient loading of code and viewing data from the robot.
- `demon_bootloader.py` - launches the file `demon_starter.py`.
- `demon_starter.py` - starts the server on Raspberry Pi 4B.
- `GPIORobot.py` - library for controlling raspberry pi gpio pins.
- `storage.py` - library for storing values in permanent memory.
- `regulators.py` - library with PID regulator.

----

## Url the YouTube video

[Our video on YouTube](https://youtu.be/alzKjLmoak8)

----

# Introduction

Programs: `final.py` or `qualification.py`, `demon_starter.py` and `demon_bootloader.py`, loaded on Raspberry pi 4B. They read the picture from the camera, process it and controls electric components.

Programs `start_robot.py` and `InetConnection.py` are running on the computer to communicate with the robot.

# Program arrangement

The code consists of several blocks. Separate sections of the program perform different actions: looking for the starting line, adjusting and controlling the movement of the robot, finding the finish line, bypassing and protecting against collisions with banks, protecting against crashing into the sides of the field.

## Sound indication of start

When starting up, the robot emits a long beep. This means that the robot has turned on, but the program has not yet loaded. After that, the program itself starts to run. After its launch, two short sound signals are released. The robot is then ready to drive. To start performing tasks and passing the route, you must press the button after the above-mentioned sound signals.

## The first leg is the start

The start consists of pressing the button on which the robot starts moving and driving to the turn line. If the line turns out to be blue, then the robot will move clockwise. Otherwise - counterclockwise.

## The second section of the program is the main pass and avoidance of obstacles in the final heats

To maintain the position relative to the rim, the position of the extremely 1 black point on the frame along the Y axis is used. Further, using the proportional-integral-differential controller, the robot aligns the positions relative to the rim. The position of the extreme point in the frame is determined depending on the direction the robot is going. To go around objects, it is used to find them in the HSV color range. When an object is found, the robot drives back and turns away from the obstacle.

## The third section is finding the finish line and stopping

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

----

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
- Open the downloaded repository from GitHub and copy 2 files from there.

![maib](https://user-images.githubusercontent.com/80317959/134554257-ed86f474-6791-48a0-8b8f-524a76d5f5b1.png)
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
- In the window that opens, find the GitHub repository folder, select the file "wroracer_last_win.py" or "wroracer.py". Click "Open".	
- ![image124](https://user-images.githubusercontent.com/80317959/130161366-c95fb988-52e0-43c4-be1e-80dfca4feae8.png)
- The program is running. Click on the button to start the ride.

---
