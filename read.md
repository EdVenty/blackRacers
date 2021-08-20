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
	
## Связь с роботом и запуск программ
Для связи с роботом используется программа «Robot Starter», написанная Юрием Гламаздином. Её стартовый файл вы можете найти в папке репозитория GitHub. 
Подключение робота:
-	Подключитесь к wifi сети робота (название может отличаться). 

![image115](https://user-images.githubusercontent.com/80317959/130160857-b1fe5578-52d9-467c-9929-11ac50dff20d.png)
-	Откройте папку репозитория GitHub. Запустите файл с названием «start_robot.py». 

![image117](https://user-images.githubusercontent.com/80317959/130160876-59d59e76-c428-4675-98b9-14444dc7a12e.png)
	-	Load Start - выбрать, загрузить и запустить файл программы.
	-	Start - загрузить и запустить уже выбранный файл программы.
	-	Stop - остановить программу.
	-	Raw - загрузить и запустить файл программы по пути на компьютере «C:/Windows/System32/raw.py».
	-	Video - включить/выключить видео.
	-	Connect to robot - выбрать робота и подключиться к нему.
			i. При нажатии появляется окно выбора робота: 

![image120](https://user-images.githubusercontent.com/80317959/130161080-06dc16f7-3adc-47da-a9ed-eddbfb6d3def.png)
			Здесь перечислены множество IP адресов. IP нашего робота – 192.168.4.1.
