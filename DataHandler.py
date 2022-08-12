import sqlite3
import time
import random


def create_id():
	choose_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
	id_ = ''
	for i in range(10):
		id_ += choose_list[int((random.random() + time.time())*1000) % len(choose_list)]
	return id_


def confirm_id():
	existing_ids = ()

	db = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" SELECT id FROM pictures """)
		gotten = cursor.fetchall()
		if gotten is not None:
			existing_ids = [i[0] for i in gotten]
	except sqlite3.Error as e:
		print('An error occurred in confirm_id\n', e)
	finally:
		if db:
			db.close()

	id_ = create_id()
	while id_ in existing_ids:
		id_ = create_id()

	return id_


def create_main_database():
	""" create the database if it wasn't created earlier

	:return: None
	"""
	db = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.executescript(""" CREATE TABLE IF NOT EXISTS users(
								 id INTEGER NOT NULL PRIMARY KEY,
								 username TEXT UNIQUE,
								 friends TEXT);

								 CREATE TABLE IF NOT EXISTS pictures(
								 id TEXT NOT NULL PRIMARY KEY,
								 file_id TEXT NOT NULL,
								 user_id INTEGER NOT NULL,
								 date INTEGER NOT NULL);
								 
								 CREATE TABLE IF NOT EXISTS pic_message(
								 pic_id TEXT NOT NULL,
								 chat_id INTEGER NOT NULL,
								 message_id INTEGER NOT NULL);
								 """)

	except sqlite3.Error as e:
		print('An error occurred in create_main_database()\n', e)
	finally:
		if db:
			db.close()


def add_user_to_usersTable(user_id: int, username: str):
	""" Add new user to the database

	:param user_id: the user's id to be added
	:param username: the username to be added
	:return: None
	"""
	db = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" INSERT OR IGNORE INTO users (id, username, friends) VALUES(?, ?, '') """,
		               (user_id, username))
		db.commit()
	except sqlite3.Error as e:
		print('An error occurred in add_user_to_usersTable()\n', e)
	finally:
		if db:
			db.close()


def add_picture_to_pictureTable(user_id: int, file_id: str):
	""" Add new picture to the database

	:param user_id: the user's id to whom the picture belongs
	:param file_id: the picture's id
	:return: id of the picture in pictures TABLE
	"""
	pic_id = ''
	db = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		pic_id = confirm_id()
		cursor.execute(""" INSERT OR IGNORE INTO pictures (id, file_id, user_id, date) VALUES(?, ?, ?, ?) """,
		               (pic_id, file_id, user_id, int(time.time())))
		db.commit()
	except sqlite3.Error as e:
		print('An error occurred in add_picture_to_pictureTable()\n', e)
	finally:
		if db:
			db.close()

	return pic_id


def add_message_to_picture(pic_id: str, chat_id: int, message_id: int):
	""" Add messages of pictures that was sent

	:param pic_id: id of the picture from pictures TABLE
	:param chat_id: the chat id where the message was sent
	:param message_id: the message id that was sent
	"""
	db = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" INSERT OR IGNORE INTO pic_message (pic_id, chat_id, message_id) VALUES(?, ?, ?) """,
		               (pic_id, chat_id, message_id))
		db.commit()
	except sqlite3.Error as e:
		print('An error occurred in add_message_to_picture()\n', e)
	finally:
		if db:
			db.close()


def delete_picture(pic_id: str):
	""" Delete a picture from tables pictures and message_pic

	:param pic_id: id of the picture from pictures TABLE
	:return: list of tuples (recipient_id, message_id)
	"""
	db = None
	messages = []
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" SELECT chat_id, message_id FROM pic_message WHERE pic_id = ? """, (pic_id,))
		gotten = cursor.fetchall()
		if gotten is not None:
			messages = gotten
		cursor.execute(""" DELETE FROM pic_message WHERE pic_id = ? """, (pic_id,))
		cursor.execute(""" DELETE FROM pictures WHERE id = ? """, (pic_id,))
		db.commit()
	except sqlite3.Error as e:
		print('An error occurred in delete_picture()\n', e)
	finally:
		if db:
			db.close()

	return messages


def get_users_pictures(user_id: int):
	""" Get pictures of the user

	:param user_id: the user's id
	:return: list of tuples: (id, file_id)
	"""
	# TODO проверить!
	db = None
	pictures = []
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" SELECT id, file_id FROM pictures WHERE user_id = ? """, (user_id,))
		gotten = cursor.fetchall()
		if gotten is not None:
			pictures = list(set([x for x in gotten]))
	except sqlite3.Error as e:
		print('An error occurred in get_users_pictures()\n', e)
	finally:
		if db:
			db.close()

	return pictures


def get_users_friedList(user_id: int):
	""" Use it to get list of the user's friends

	:param user_id: the user's id whose list is needed to be got
	:return: list of user ids
	"""
	db = None
	friends = []
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" SELECT friends FROM users WHERE id = ? """, (user_id,))
		gotten = cursor.fetchone()
		if gotten is not None:
			friends = (gotten[0]).split(' ')
			while '' in friends:
				friends.remove('')
	except sqlite3.Error as e:
		print('An error occurred in get_users_friedList()\n', e)
	finally:
		if db:
			db.close()
		
	return friends


def get_user_id(username: str):
	""" Use it to get user's id by their username

	:param username: the username whose id is to be returned
	:return: int (user_id) or None if the one not found
	"""
	db = None
	user_id = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" SELECT id FROM users WHERE username = ? """, (username,))
		gotten = cursor.fetchone()
		if gotten is not None:
			user_id = gotten[0]
	except sqlite3.Error as e:
		print('An error occurred in get_user_id()\n', e)
	finally:
		if db:
			db.close()

	return user_id


def get_username(user_id: int):
	""" Use it to get username by their id

	:param user_id: the user's id whose username is to be returned
	:return: string (username) or None if the one not found
	"""
	db = None
	username = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" SELECT username FROM users WHERE id = ? """, (user_id,))
		gotten = cursor.fetchone()
		if gotten is not None:
			username = gotten[0]
	except sqlite3.Error as e:
		print('An error occurred in get_username()\n', e)
	finally:
		if db:
			db.close()
		
	return username


def add_friend(user1_id: int, user2_id: int):
	""" Use it to add friend to the user's friend list

	:param user2_id: the user's id to be added
	:param user1_id: the user's id to be added
	"""
	db = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" SELECT friends FROM users WHERE id = ? """, (user1_id,))
		gotten = cursor.fetchone()
		if gotten is not None:
			friends_1 = (gotten[0]).split(' ')
		cursor.execute(""" SELECT friends FROM users WHERE id = ? """, (user2_id,))
		gotten = cursor.fetchone()
		if gotten is not None:
			friends_2 = (gotten[0]).split(' ')
		# TODO: ограничить список друзей численно
		# 1
		friends_s1 = ''
		for friend in friends_1:
			friends_s1 += friend + ' '
		friends_s1 += str(user2_id)
		cursor.execute(""" UPDATE users SET friends = ? WHERE id = ? """, (friends_s1, user1_id))
		# 2
		friends_s2 = ''
		for friend in friends_2:
			friends_s2 += friend + ' '
		friends_s2 += str(user1_id)
		cursor.execute(""" UPDATE users SET friends = ? WHERE id = ? """, (friends_s2, user2_id))
		db.commit()
	except sqlite3.Error as e:
		print('An error occurred in add_friend()\n', e)
	finally:
		if db:
			db.close()


def delete_friend(user_id: int, friends_id: int):
	""" Use it to delete friend from the users list of friends

	:param user_id: the user's id from whom friend list to delete friend
	:param friends_id: the friend's id to be deleted
	:return: the message: weather friend was in the list weather they were not
	"""
	db = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		# 1
		cursor.execute(""" SELECT friends FROM users WHERE id = ? """, (user_id,))
		gotten = cursor.fetchone()
		if gotten is not None:
			friends = (gotten[0]).split(' ')
			while '' in friends:
				friends.remove('')
		if str(friends_id) in friends:
			friends.remove(str(friends_id))
		else: return 1
		friends_s = ''
		for friend in friends:
			friends_s += friend + ' '
		cursor.execute(""" UPDATE users SET friends = ? WHERE id = ? """, (friends_s, user_id))

		# 2
		cursor.execute(""" SELECT friends FROM users WHERE id = ? """, (friends_id,))
		gotten = cursor.fetchone()
		if gotten is not None:
			friends = (gotten[0]).split(' ')
			while '' in friends:
				friends.remove('')
		if str(user_id) in friends:
			friends.remove(str(user_id))
		else:
			return 1
		friends_s = ''
		for friend in friends:
			friends_s += friend + ' '
		cursor.execute(""" UPDATE users SET friends = ? WHERE id = ? """, (friends_s, friends_id))
		db.commit()
	except sqlite3.Error as e:
		print('An error occurred in delete_friend()\n', e)
	finally:
		if db:
			db.close()

	return 0


def get_pictures_of_user(user_id: int):
	""" Use it to get the pictures of the user

	:param user_id: the user's id whose pictures will be returned
	:return: list of pictures (pictures = (file_id, date, message_id) or None if there is not any
	"""
	pictures = None
	db = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" SELECT file_id, data, message_id FROM pictures WHERE id = ? """, (user_id,))
		pictures = cursor.fetchall()
	except sqlite3.Error as e:
		print('An error occurred in get_pictures_of_user()\n', e)
	finally:
		if db:
			db.close()

	return pictures

# db = None
# try:
# 	db = sqlite3.connect('testdb.db')
# 	cursor = db.cursor()
# 	cursor.execute("""  """)
# 	db.commit()
# except sqlite3.Error as e:
# 	print('An error occurred\n', e)
# finally:
# 	if db:
# 		db.close()
#

# TODO добавить id в таблицу картинок: слишком длинный file_id
