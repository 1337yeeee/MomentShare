# MomentShare
Telegram bot for sharing pictures

## Подготовка
Создание файла Const.py для определения следующих констант:
- **VERSION** - версия проекта
- **tokenPath** - путь к файлу, который содержит токен бота, такой как `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`
- **databasePath** - путь к базе данных. Саму базу данных создает функция `DataHandler.create_main_database()`
- **maximumFriends** - ограничение на количество друзей одного пользователя
- **expirationTime** - ограничение на существование отправленных и полученных фотографий в чатах

## Запуск
Для запуска бота используйте комманду![image](https://user-images.githubusercontent.com/45238097/209676199-05dee03b-c63e-43dd-b771-cfbbff99f59b.png)

`python main.py`

После запуска, вызываются следующие функции:

`Data.create_main_database()`, где Data ~ `DataHandler`

`token = getToken()`

`rh = RequestHandler(token)`

`clear_updates(rh)`

Затем запускается главный цикл, в котором обновления получаются GET запросом через `RequestHandler`, определяется тип обновления: `Callback` или `Message`.

Логику выполняет `ResponseManager`

<hr>

### DataHandler
Модуль, который отвечает за работу с базой данных с помощью библиотеки `sqlite3`

Функция `create_main_database()` создает базу данных с таблицами `users` `pictures` `pic_message` `menu_message` `pic_user`

Остальные функции выполняют `SELECT`, `INSERT`, 'UPDATE' и `DELETE` запросы

### RequestHandler
Модуль, который отвечает за отправку HTTP запросов на сервер Telegram API с помощью библиотеки `requests`

Методы класса `RequestHandler` посылают запросы со следующими методами:
- `get` - 'getUpdates'
- `send` - 'sendMessage'
- `delete` - 'deleteMessage'
- `sendPhoto` - 'sendPhoto'
- `editMessage` - 'editMessageText'

### ResponseManager
Модуль, который отвечает за логику бота

В зависимости от типа и содержания обновления, которые было получено от сервера Telegram, выполняет соответствующие функции.


## Примеры работы бота

Сообщение после старта бота

![image](https://user-images.githubusercontent.com/45238097/209675313-40c89746-d9d1-42c9-af64-59f14a9d3c2d.png)


Меню бота, вызванное коммандой `/menu`

![image](https://user-images.githubusercontent.com/45238097/209675937-5e6a548b-1441-4005-b26e-0398dacc9553.png)


Подменю, связанное с друзьями

![image](https://user-images.githubusercontent.com/45238097/209676092-107be904-cec3-4832-9407-8db37344567e.png)


Подменю, связанное с фотографиями

![image](https://user-images.githubusercontent.com/45238097/209676112-eaec5307-5b39-471c-8c72-8d96aa6b87b7.png)


