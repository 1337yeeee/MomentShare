import sqlite3


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
								 file_id TEXT NOT NULL PRIMARY KEY,
								 user_id INTEGER NOT NULL,
								 FOREIGN KEY (user_id)
								    REFERENCES users (user_id)) """)
	except sqlite3.Error as e:
		print('An error occurred\n', e)
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
		print('An error occurred\n', e)
	finally:
		if db:
			db.close()


def add_picture_to_pictureTable(user_id: int, file_id: str):
	""" Add new picture to the database
	this table is connected to the user table with the username

	:param user_id: the user's id to whom the picture belongs
	:param file_id: the picture's id
	:return: None
	"""
	db = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" INSERT OR IGNORE INTO pictures (file_id, user_id) VALUES(?, ?) """,
		               (file_id, user_id))
		db.commit()
	except sqlite3.Error as e:
		print('An error occurred\n', e)
	finally:
		if db:
			db.close()


def get_users_friedList(user_id: int):
	""" Use it to get list of the user's friends

	:param user_id: the user's id whose list is needed to be got
	:return: list of user ids
	"""
	db = None
	friends = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" SELECT friends FROM users WHERE user_id = ? """, (user_id,))
		friends = (cursor.fetchone()[0]).split(' ')
	except sqlite3.Error as e:
		print('An error occurred\n', e)
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
		if cursor.fetchone() is not None:
			user_id = cursor.fetchone()[0]
	except sqlite3.Error as e:
		print('An error occurred\n', e)
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
		cursor.execute(""" SELECT username FROM users WHERE user_id = ? """, (user_id,))
		if cursor.fetchone() is not None:
			username = cursor.fetchone()[0]
	except sqlite3.Error as e:
		print('An error occurred\n', e)
	finally:
		if db:
			db.close()
		
	return username


def add_friend(user_id: int, friends_id: int):
	""" Use it to add friend to the user's friend list

	:param user_id: the user's id to whom friend to be added
	:param friends_id: the friend's id who is to be added
	:return: the message: weather the friend is added weather they are not
	"""
	db = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" SELECT friends FROM users WHERE user_id = ? """, (user_id,))
		friends = (cursor.fetchone()[0]).split(' ')
		if len(friends) < 10:
			friends.append(friends_id)
		else:
			return '{} wasn\'t added to your friends list'.format(get_username(friends_id))
		friends_s = ''
		for friend in friends:
			friends_s += friend + ' '
		cursor.execute(""" UPDATE users SET friends = ? WHERE user_id = ? """, (friends, ))
		db.commit()
	except sqlite3.Error as e:
		print('An error occurred\n', e)
	finally:
		if db:
			db.close()
		
	return '{} was added to your friends list'.format(get_username(friends_id))


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
		cursor.execute(""" SELECT friends FROM users WHERE user_id = ? """, (user_id,))
		friends = (cursor.fetchone()[0]).split(' ')
		if friends_id in friends:
			friends.remove(friends_id)
		else: '{} wasn\'t in your friends list'.format(get_username(friends_id))
		friends_s = ''
		for friend in friends:
			friends_s += friend + ' '
		cursor.execute(""" UPDATE users SET friends = ? WHERE user_id = ? """, (friends,))
		db.commit()
	except sqlite3.Error as e:
		print('An error occurred\n', e)
	finally:
		if db:
			db.close()
		
	return '{} was deleted from your friends list'.format(get_username(friends_id))


def get_pictures_of_user(user_id: int):
	""" Use it to get the pictures of the user

	:param user_id: the user's id whose pictures will be returned
	:return: list of pictures (pictures are in tuples) or None if there is not any
	"""
	pictures = None
	db = None
	try:
		db = sqlite3.connect('testdb.db')
		cursor = db.cursor()
		cursor.execute(""" SELECT file_id FROM pictures WHERE user_id = ? """, (user_id,))
		pictures = cursor.fetchall()
	except sqlite3.Error as e:
		print('An error occurred\n', e)
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
