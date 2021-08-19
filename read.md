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
-	`` Kozhux_right_BlackRacer`` : модель выложена в двух файлах(stl и itp), модель проектировалась в  Autodesk Inventor 2020
6.	В папке “Program” находится весь код, используемый на роботе и на главном компьютере
-	`` wro.py ``-программа используемая в симуляторе для первичной настройки алгоритмов
-	`` wroracer ``-программа запускающаяся на роботе и управляющая его действиями
-	`` regulators.py ``-модуль регулятора движения робота
-	`` RoboAPI.py``-модуль коммуникации с роботом
-	`` wroracer_last_win.py `` -программа которая использовалась на региональных соревнованиях
-	`` start_robot.py ``-файл запускающийся на главном компьютере 
-	`` InetConnection.py``-файл создания сервера на Raspberry Pi
7.	Файлы в основном разделе:
-	`` wroracer``-программа запускающаяся на роботе и управляющая его действиями
-	``wroracer_last_win.py``-программа, которая использовалась на региональных соревнованиях
-	``start_robot.py``-файл запускающийся на главном компьютере 
-	`` README.md``-файл с руководством пользователя и обзором репозитория
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
	
	![image058](https://user-images.githubusercontent.com/80317959/130039118-d082de0d-5b57-4934-9ebf-8a02349eafe1.png)![image074](https://user-images.githubusercontent.com/80317959/130039159-99f6369f-0d41-457e-9f4a-761b0ef2f462.png)

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

