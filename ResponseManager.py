from RequestHandler import RequestHandler
from functools import partial
from Callback import Callback
from Message import Message
import DataHandler as Data
from Const import VERSION


class Handler:
	"""
	Think of "the user" as the person who sends requests
	and "the friend" as the person who receives messages from "the user"
	and who can accept or reject requests from "the user"
	"""

	def __init__(self, message, rh: RequestHandler, do_this=None):
		""" The message type depends on the external response. The message type also determines which functions will be executed. For example, some functions only accept callback_query
		rh: RequestHandler is used to send requests to Telegram API
		do_this: Some actions require additional user action, such as selecting the photo they want to delete

		:param message: the object of the Message or Callback classes
		:param rh: the object of the RequestHandler class
		:param do_this: the function to call before dealing with message as Message
		"""
		self.rh = rh
		self.message = message
		self.do_this = do_this

	def handler(self):
		""" The main method of the class

		:return: action method for do_this or None
		"""
		Handler.get_rid_of_expired(self.rh)

		if type(self.message) == Callback:
			return self.deal_with_callback()
		elif self.do_this is not None:
			return self.do_this(self)
		elif type(self.message) == Message:
			return self.deal_with_message()

		return None

	def deal_with_command_func(self):
		""" If message is a command

		:return: None
		"""
		if self.message.command == '/start':
			self.start()
		elif self.message.command == '/menu':
			self.menu_func()
		elif self.message.command == '/add':
			self.invite_friend()
		return None

	def deal_with_photo_func(self):
		""" If message contains a photo. Sends photo to all your friends

		:return: None
		"""
		pic_id = Data.add_picture_to_pictureTable(self.message.chat_id, self.message.photo_id)
		Data.add_message_to_picture(pic_id, self.message.chat_id, self.message.message_id)

		friends = Data.get_users_friedList(self.message.chat_id)

		for friend in friends:
			resp = self.rh.sendPhoto(friend, self.message.photo_id,
			                         f'{self.message.username} делится с Вами фотографией')
			Data.add_message_to_picture(pic_id, friend, resp['result']['message_id'])
			Data.add_pic_user(pic_id, friend, self.message.chat_id)

	def deal_with_message(self):
		""" If message is an object of Message class

		:return: None
		"""
		if self.message.is_command:
			self.deal_with_command_func()
		elif self.message.is_photo:
			self.deal_with_photo_func()
		elif self.message.is_mention:
			self.invite_friend()

		return None

	def deal_with_callback(self):
		""" If message is an object of Callback class

		:return: action method for do_this or None
		"""
		if self.message.data[0] == 'invitation':
			Handler.invite_accept(self.message.chat_id, int(self.message.data[1]), self.rh, self.message.message_id)
		elif self.message.data[0] == 'decline_inv':
			Handler.invite_decline(self.message.chat_id, int(self.message.data[1]), self.rh, self.message.message_id)
		elif self.message.data[0] == 'delete_friend':
			self.delete_friend()
		elif self.message.data[0] == 'pic_certain':
			return self.await_photo()
		elif self.message.data[0] == 'delete_picture':
			self.delete_picture()
		elif self.message.data[0] == 'friends':
			self.menu_friends()
		elif self.message.data[0] == 'picture':
			self.menu_pictures()
		elif self.message.data[0] == 'menu':
			self.menu_func()
		elif self.message.data[0] == 'addfriend':
			self.invite_friend_func()
		elif self.message.data[0] == 'seefriend':
			self.show_all_friends()
		elif self.message.data[0] == 'delfriend':
			self.delete_friend_func()
		elif self.message.data[0] == 'seepictur':
			self.show_all_pictures_func()
		elif self.message.data[0] == 'delpictur':
			return self.delete_picture_func()
		elif self.message.data[0] == 'sendpicto':
			self.send_picture_certain_func()
		elif self.message.data[0] == 'show_pics_set' or \
			 self.message.data[0] == 'show_pics_get':
			self.show_all_pictures()

		return None

	def menu_func(self):
		""" Sends a menu to Telegram user

		:return: None
		"""
		text = 'menu text'
		keyboard = {'inline_keyboard': [
			[{'text': 'Друзья', 'callback_data': 'friends'}],
			[{'text': 'Фото', 'callback_data': 'picture'}]
		]}
		extra = ['reply_markup', keyboard]
		if isinstance(self.message, Message):
			message_id = Data.get_menu_message(self.message.chat_id)
			if message_id != 0:
				self.rh.delete(self.message.chat_id, message_id)
				Data.delete_menu_message(self.message.chat_id)
			resp = self.rh.send(self.message.chat_id, text, extra)
			Data.add_menu_message(self.message.chat_id, resp['result']['message_id'])
		elif isinstance(self.message, Callback):
			self.rh.editMessage(self.message.chat_id, self.message.message_id, text, keyboard)

	def menu_friends(self):
		""" Updates the menu with friends submenu

		:return: None
		"""
		text = 'friends menu text'
		keyboard = {'inline_keyboard': [
			[{'text': 'Добавить друга', 'callback_data': 'addfriend'}],
			[{'text': 'Посмотреть друзей', 'callback_data': 'seefriend'}],
			[{'text': 'Удалить друга', 'callback_data': 'delfriend'}],
			[{'text': '<- Меню', 'callback_data': 'menu'}]
		]}
		self.rh.editMessage(self.message.chat_id, self.message.message_id, text, keyboard)

	def menu_pictures(self):
		""" Updates the menu with pictures submenu

		:return: None
		"""
		text = 'Pictures menu text'
		keyboard = {'inline_keyboard': [
			[{'text': 'Посмотреть все фото', 'callback_data': 'seepictur'}],
			[{'text': 'Удалить фото', 'callback_data': 'delpictur'}],
			[{'text': 'Отправить фото другу', 'callback_data': 'sendpicto'}],
			[{'text': '<- Меню', 'callback_data': 'menu'}]
		]}
		self.rh.editMessage(self.message.chat_id, self.message.message_id, text, keyboard)

	@staticmethod
	def get_rid_of_expired(rh: RequestHandler):
		""" Deletes messages with pictures that have expired

		:param rh: RequestHandler object
		:return: None
		"""
		messages = Data.get_expired_pictures()

		for message in messages:
			rh.delete(message['chat_id'], message['message_id'])
			Data.delete_pic_message(message['chat_id'], message['message_id'])

	def start(self):
		""" Method of '/start' command. Sends an instruction

		:return: None
		"""
		text = f'Здравствуй {self.message.name}!' \
		       f'Отправь команду /menu для того, чтобы увидеть возможности бота\n' \
		       f'------------\nversion: {VERSION}'

		Data.add_user_to_usersTable(self.message.chat_id, self.message.username)

		self.rh.send(self.message.chat_id, text)

	def invite_friend_func(self):
		""" Method of '/add' command. Sends an instruction

		:return: None
		"""
		text = 'Напишите username друга, которого желаете добавить\n' + \
		       'Note that your friend should start this bot to be in your friend list'

		self.rh.send(self.message.chat_id, text)

	def invite_friend(self):
		""" Sends an invitation to the friend.
		Will send the message to the user if:
		- the friend hasn't started the bot
		- the friend is already in the user's friend list
		- the friend and the user are the same person
		Otherwise, sends the message to the friend with accepting request

		:return: None
		"""
		if Data.get_user_id(self.message.mention) is None:
			text = 'The user you want to invite hasn\'t started the bot yet'
			self.rh.send(self.message.chat_id, text)
			return None

		if self.message.mention == self.message.username:
			text = 'Вы не можете добавить себя к себе же в друзья'
			self.rh.send(self.message.chat_id, text)
			return None

		user_id = Data.get_user_id(self.message.mention)

		if Handler.is_friend(user_id, self.message.chat_id):
			text = f'{self.message.mention.replace("@","")} is already in your friend list'
			self.rh.send(self.message.chat_id, text)
			return None

		text = '{} хочет добавить вас в друзья.\n'.format('@' + self.message.username)
		keyboard = {'inline_keyboard': [[
			{'text': 'Accept', 'callback_data': f'invitation*{self.message.chat_id}'},
			{'text': 'Decline', 'callback_data': f'decline_inv*{self.message.chat_id}'}
		]]}
		extra = ['reply_markup', keyboard]
		self.rh.send(user_id, text, extra)

		text = 'Приглашение для {} отправленно'.format(self.message.mention)
		self.rh.send(self.message.chat_id, text)

		return None

	def show_all_friends(self):
		""" Sends message with the usernames and number of friends

		:return: None
		"""
		friends = Data.get_users_friedList(self.message.chat_id)

		if len(friends) == 0:
			text = 'У вас пока нет друзей 🥲'
		else:
			text = f'Ваш список друзей ({len(friends)})\n'
			for friend in friends:
				text += f'{Data.get_username(friend)}\n'

		self.rh.send(self.message.chat_id, text)

	def delete_friend_func(self):
		""" Sends a message with buttons that contain usernames of the friends and callback_data to delete them

		:return: None
		"""
		friends = Data.get_users_friedList(self.message.chat_id)

		text = 'Выберите друга, которого желаете удалить из друзей'
		keyboard = {'inline_keyboard': []}

		for friend in friends:
			keyboard['inline_keyboard'].append([
				{'text': f'{Data.get_username(friend)}',
				 'callback_data': f'delete_friend*{friend}'}
			])

		extra = ['reply_markup', keyboard]
		self.rh.send(self.message.chat_id, text, extra)

	def delete_friend(self):
		""" Deletes the user and the friend from their friends lists. Sends messages to both of them.
		Deletes message that was sent by Handler.delete_friend_func()

		:return: None
		"""
		user1_name = Data.get_username(self.message.chat_id)
		user2_name = Data.get_username(self.message.chat_id)

		Data.delete_friend(self.message.chat_id, int(self.message.data[1]))

		friends1 = Data.get_users_friedList(self.message.chat_id)
		friends2 = Data.get_users_friedList(int(self.message.data[1]))

		if str(int(self.message.data[1])) not in friends1 and str(self.message.chat_id) not in friends2:
			self.rh.send(self.message.chat_id, f'{user2_name} was deleted from your friend list')
			self.rh.send(int(self.message.data[1]), f'{user1_name} deleted you from theirs friend list')
			self.rh.delete(self.message.chat_id, self.message.message_id)

	def show_all_pictures_func(self):
		""" Method of 'seepictur' callback of picture submenu.
		Sends message with choice commands:
		from whom the photos were received or to whom the photos were sent

		:return: None
		"""
		friends = Data.get_users_friedList(self.message.chat_id)

		text = 'Выберите, от кого желаете увидеть все фото'
		keyboard = {'inline_keyboard': [
			[
				{'text': 'Я отправил',
				 'callback_data': f'show_pics_set*{self.message.chat_id}'},
				{'text': 'Я получил',
				 'callback_data': f'show_pics_get*{self.message.chat_id}'}
			]
		]}

		for friend in friends:
			keyboard['inline_keyboard'].append([
				{'text': f'Отправил {Data.get_username(friend)}',
				 'callback_data': f'show_pics_set*{friend}'},
				{'text': f'Получил {Data.get_username(friend)}',
				 'callback_data': f'show_pics_get*{friend}'}
			])

		extra = ['reply_markup', keyboard]
		self.rh.send(self.message.chat_id, text, extra)

	def show_all_pictures(self):
		""" Deals with Callback.
		Sends the pictures that:\n
		- were sent to the user by someone\n
		- were sent to someone by the user\n
		- were received by the user\n
		- were sent by the user

		:return: None
		"""
		if not isinstance(self.message, Callback):
			return None

		pictures_users = []
		if int(self.message.data[1]) == self.message.chat_id:
			if self.message.data[0] == 'show_pics_set':
				pictures_users = Data.get_picture_by_user_only_set(self.message.chat_id)
			elif self.message.data[0] == 'show_pics_get':
				pictures_users = Data.get_picture_by_user_only_get(self.message.chat_id)
		elif self.message.data[0] == 'show_pics_set':
			pictures_users = Data.get_picture_by_user(self.message.chat_id, int(self.message.data[1]))
		elif self.message.data[0] == 'show_pics_get':
			pictures_users = Data.get_picture_by_user(int(self.message.data[1]), self.message.chat_id)

		if len(pictures_users) == 0:
			text = 'Фото не найдены'
			self.rh.send(self.message.chat_id, text)
			return None

		for pic_user in pictures_users:
			pic_id = pic_user['pic_id']
			picture = Data.get_picture(pic_id)
			file_id = picture['file_id']
			message_id = Data.get_message_id_from_pic_message(pic_id, self.message.chat_id)
			if message_id:
				self.rh.delete(self.message.chat_id, message_id)
				Data.delete_pic_message(self.message.chat_id, message_id)
			date = picture['date']
			username_set = Data.get_username(pic_user['user_set_id'])
			username_get = Data.get_username(pic_user['user_get_id'])
			resp = self.rh.sendPhoto(self.message.chat_id, file_id, f'@{username_set} sent photo to @{username_get}\n'
			                                                        f'on _{date}_')
			Data.add_message_to_picture(pic_id, self.message.chat_id, resp['result']['message_id'])

	def send_picture_certain_func(self):
		""" Sends message with buttons that contain usernames of the friends and callback_data who to send the picture

		:return: None
		"""
		friends = Data.get_users_friedList(self.message.chat_id)

		text = 'Выберите друга, которому желаете отправить фото'
		keyboard = {'inline_keyboard': []}

		for friend in friends:
			keyboard['inline_keyboard'].append([
				{'text': f'{Data.get_username(friend)}',
				 'callback_data': f'pic_certain*{friend}'}
			])

		extra = ['reply_markup', keyboard]
		self.rh.send(self.message.chat_id, text, extra)

		return None

	@staticmethod
	def send_picture_certain(self, callback):
		""" Sends a picture to the certain friend, whose id is in the callback.

		:param self: previous object of Handler class
		:param callback: received callback
		:return: None
		"""
		if type(self.message) != Message:
			return None
		if not self.message.is_photo:
			return None

		caption = f'@{self.message.username} отправил тебе фото'

		pic_id = Data.add_picture_to_pictureTable(self.message.chat_id, self.message.photo_id)
		Data.add_pic_user(pic_id, int(callback.data[1]), self.message.chat_id)

		resp = self.rh.sendPhoto(int(callback.data[1]), self.message.photo_id, caption)
		Data.add_message_to_picture(pic_id, int(callback.data[1]), resp['result']['message_id'])
		Data.add_message_to_picture(pic_id, self.message.chat_id, self.message.message_id)

		return None

	def await_photo(self):
		""" Sends an instruction to the user after they chose the friend who will receive the photo

		:return: Handler.send_picture_certain method with callback=self.message
		"""
		self.rh.delete(self.message.chat_id, self.message.message_id)

		text = f'Вы выбрали @{Data.get_username(int(self.message.data[1]))}.' \
		       f'\nОтправьте фото, которое должен получить ваш друг'
		self.rh.send(self.message.chat_id, text)

		return partial(Handler.send_picture_certain, callback=self.message)

	def delete_picture_func(self):
		""" Sends messages that contain a picture and a button
		that contains callback_data to delete the picture and
		the picture's id

		:return: Handler.return_messages method with the messages that were sent to be deleted after selecting
		"""
		pictures = Data.get_users_pictures(self.message.chat_id)

		messages_tobe_deleted = []
		for pic_id, file_id in pictures:
			keyboard = {'inline_keyboard': [
				[{'text': 'Delete',
				 'callback_data': f'delete_picture*{pic_id}'}]
			]}

			extra = ['reply_markup', keyboard]
			resp = self.rh.sendPhoto(self.message.chat_id, file_id, extra=extra)
			messages_tobe_deleted.append(resp['result']['message_id'])

		resp = self.rh.send(self.message.chat_id, 'Выберите фото, которое желаете удалить')
		messages_tobe_deleted.append(resp['result']['message_id'])
		if len(pictures) == 0:
			resp = self.rh.send(self.message.chat_id, 'Нет фото')
			messages_tobe_deleted.append(resp['result']['message_id'])

		return partial(Handler.return_messages, messages=messages_tobe_deleted)

	def delete_picture(self):
		""" Deletes messages that were used to select the photo.
		And deletes the picture from database and from every user that has received it

		:return: None
		"""
		messages = None
		if isinstance(self.do_this, partial):
			if self.do_this.func == Handler.return_messages:
				messages = self.do_this()

		if messages is not None:
			for msg in messages:
				self.rh.delete(self.message.chat_id, msg)

		messages = Data.delete_picture(self.message.data[1])
		for msg in messages:
			self.rh.delete(msg[0], msg[1])

	@staticmethod
	def return_messages(messages: list[int]):
		""" Static method to remember messages

		:param messages: the messages to return
		:return: list of the messages ids
		"""
		return messages

	@staticmethod
	def invite_accept(user1_id: int, user2_id: int, rh: RequestHandler, message_id: int):
		""" Sends messages to the user and the friend that they have been added to each other's friend lists

		:param user1_id: the user's id
		:param user2_id: the friend's id
		:param rh: RequestHandler object
		:param message_id: the id of the invitation message
		:return: None
		"""
		user1_name = Data.get_username(user1_id)
		user2_name = Data.get_username(user2_id)

		Data.add_friend(user1_id, user2_id)

		friends1 = Data.get_users_friedList(user1_id)
		friends2 = Data.get_users_friedList(user2_id)

		if user2_id in friends1 and user1_id in friends2:
			rh.send(user1_id, f'{user2_name} was added ✅ to your friends list')
			rh.send(user2_id, f'{user1_name} was added ✅ to your friends list')
			rh.delete(user1_id, message_id)

	@staticmethod
	def invite_decline(user1_id: int, user2_id: int, rh: RequestHandler, message_id: int):
		""" Sends messages to:\n
		- the user: the_friend_username declined your request\n
		- the friend: You declined request from the_user_username

		:param user1_id: the user's id
		:param user2_id: the friend's id
		:param rh: RequestHandler object
		:param message_id: the id of the invitation message
		:return:
		"""
		user1_name = Data.get_username(user1_id)
		user2_name = Data.get_username(user2_id)

		rh.send(user1_id, f'You declined ❌ the friend request from {user2_name}')
		rh.send(user2_id, f'{user1_name} declined ❌ your request')
		rh.delete(user1_id, message_id)

	@staticmethod
	def is_friend(user1_id: int, user2_id: int):
		""" Checks if user1 and user2 are friends

		:param user1_id: user id
		:param user2_id: user id
		:return: True if user1 is friend of user2
		False if user1 is not friend of user2
		"""
		friends1 = Data.get_users_friedList(user1_id)
		friends2 = Data.get_users_friedList(user2_id)

		return user2_id in friends1 and user1_id in friends2
