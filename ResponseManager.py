from RequestHandler import RequestHandler
from functools import partial
from Callback import Callback
from Message import Message
import DataHandler as Data
from Const import VERSION


class Handler:

	def __init__(self, message, rh: RequestHandler, do_this=None):
		self.rh = rh
		self.message = message
		self.do_this = do_this

	def handler(self):
		# TODO проверить!
		Handler.get_rid_of_expired(self.rh)

		if type(self.message) == Callback:
			return self.deal_with_callback()
		elif self.do_this is not None:
			return self.do_this(self)
		elif type(self.message) == Message:
			return self.deal_with_message()

		return None

	def deal_with_command_func(self):
		if self.message.command == '/start':
			self.start()
		elif self.message.command == '/menu':
			self.menu_func()
		elif self.message.command == '/add':  # TODO добавить команду боту
			self.invite_friend()
		return None

	def deal_with_photo_func(self):
		pic_id = Data.add_picture_to_pictureTable(self.message.chat_id, self.message.photo_id)
		Data.add_message_to_picture(pic_id, self.message.chat_id, self.message.message_id)

		friends = Data.get_users_friedList(self.message.chat_id)

		for friend in friends:
			resp = self.rh.sendPhoto(friend, self.message.photo_id,
			                         f'{self.message.username} делится с Вами фотографией')
			Data.add_message_to_picture(pic_id, friend, resp['result']['message_id'])
			Data.add_pic_user(pic_id, friend, self.message.chat_id)

	def deal_with_message(self):
		if self.message.is_command:
			self.deal_with_command_func()
		elif self.message.is_photo:
			self.deal_with_photo_func()
		elif self.message.is_mention:
			self.invite_friend()

		return None

	def deal_with_callback(self):
		if self.message.data[0] == 'invitation':
			Handler.invite_accept(self.message.chat_id, int(self.message.data[1]), self.rh, self.message.message_id)
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
			self.show_all_pictures()
		elif self.message.data[0] == 'delpictur':  # TODO
			return self.delete_picture_func()
		elif self.message.data[0] == 'sendpicto':
			self.send_picture_certain_func()

		return None

	def menu_func(self):
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
		text = 'friends menu text'
		keyboard = {'inline_keyboard': [
			[{'text': 'Добавить друга', 'callback_data': 'addfriend'}],
			[{'text': 'Посмотреть друзей', 'callback_data': 'seefriend'}],
			[{'text': 'Удалить друга', 'callback_data': 'delfriend'}],
			[{'text': '<- Меню', 'callback_data': 'menu'}]
		]}
		self.rh.editMessage(self.message.chat_id, self.message.message_id, text, keyboard)

	def menu_pictures(self):
		text = 'friends menu text'
		keyboard = {'inline_keyboard': [
			[{'text': '/see_pictures', 'callback_data': 'seepictur'}],
			[{'text': '/delete_picture', 'callback_data': 'delpictur'}],
			[{'text': '/send_certain', 'callback_data': 'sendpicto'}],
			[{'text': '<- Меню', 'callback_data': 'menu'}]
		]}
		self.rh.editMessage(self.message.chat_id, self.message.message_id, text, keyboard)

	@staticmethod
	def get_rid_of_expired(rh: RequestHandler):
		messages = Data.get_expired_pictures()

		for message in messages:
			rh.delete(message['chat_id'], message['message_id'])
			Data.delete_pic_message(message['chat_id'], message['message_id'])

	def start(self):
		text = f'Здравствуй {self.message.name}!' \
		       f'Отправь команду /menu для того, чтобы увидеть возможности бота\n' \
		       f'------------\nversion: {VERSION}'

		Data.add_user_to_usersTable(self.message.chat_id, self.message.username)

		self.rh.send(self.message.chat_id, text)

	def invite_friend_func(self):
		text = 'Напишите username друга, которого желаете добавить\n' + \
		       'Note that your friend should start this bot to be in your friend list'

		self.rh.send(self.message.chat_id, text)

	def invite_friend(self):
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
			{'text': 'Accept', 'callback_data': f'invitation*{self.message.chat_id}'}
		]]}
		extra = ['reply_markup', keyboard]
		self.rh.send(user_id, text, extra)

		text = 'Приглашение для {} отправленно'.format(self.message.mention)
		self.rh.send(self.message.chat_id, text)

		return None

	def show_all_friends(self):
		friends = Data.get_users_friedList(self.message.chat_id)

		if len(friends) == 0:
			text = 'У вас пока нет друзей 🥲'
		else:
			text = f'Ваш список друзей ({len(friends)})\n'
			for friend in friends:
				text += f'{Data.get_username(friend)}\n'

		self.rh.send(self.message.chat_id, text)

	def delete_friend_func(self):
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
		user1_name = Data.get_username(self.message.chat_id)
		user2_name = Data.get_username(self.message.chat_id)

		Data.delete_friend(self.message.chat_id, int(self.message.data[1]))

		friends1 = Data.get_users_friedList(self.message.chat_id)
		friends2 = Data.get_users_friedList(int(self.message.data[1]))

		if str(int(self.message.data[1])) not in friends1 and str(self.message.chat_id) not in friends2:
			self.rh.send(self.message.chat_id, f'{user2_name} was deleted from your friend list')
			self.rh.send(int(self.message.data[1]), f'{user1_name} deleted you from theirs friend list')
			self.rh.delete(self.message.chat_id, self.message.message_id)

	def show_all_pictures_func(self):  # TODO доделать
		friends = Data.get_users_friedList(self.message.chat_id)

		text = 'Выберите, от кого желаете увидеть все фото'
		keyboard = {'inline_keyboard': [
			[
				{'text': 'Свои',
				 'callback_data': f'delete_friend*{friend}'}
			]
		]}

		for friend in friends:
			keyboard['inline_keyboard'].append([
				{'text': f'{Data.get_username(friend)}',
				 'callback_data': f'delete_friend*{friend}'}
			])

		extra = ['reply_markup', keyboard]
		self.rh.send(self.message.chat_id, text, extra)

	# функция отправляет все фото, которые отправил этот пользователь.
	# TODO нужно сделать функцию(ии), которая будет отправлять все фото определенного пользователя или всех пользователей
	def show_all_pictures(self):
		pictures = Data.get_users_pictures(self.message.chat_id)

		if len(pictures) == 0:
			text = 'Вы не отправляли фото'
			self.rh.send(self.message.chat_id, text)
			return None

		for pic_id, file_id in pictures:
			message_id = Data.get_message_id_from_pic_message(pic_id, self.message.chat_id)
			self.rh.delete(self.message.chat_id, message_id)
			Data.delete_pic_message(self.message.chat_id, message_id)
			date = Data.get_picture(pic_id)['date']
			resp = self.rh.sendPhoto(self.message.chat_id, file_id, f'_{date}_')
			Data.add_message_to_picture(pic_id, self.message.chat_id, resp['result']['message_id'])

	def _show_all_pictures_(self):  # TODO
		pic_ids = Data.get_picture_by_user(self.message.chat_id)

		if len(pic_ids) == 0:
			text = 'Фото не найдены'
			self.rh.send(self.message.chat_id, text)
			return None

		for pic_id in pic_ids:
			picture = Data.get_picture(pic_id)
			file_id = picture['file_id']
			message_id = Data.get_message_id_from_pic_message(pic_id, self.message.chat_id)
			self.rh.delete(self.message.chat_id, message_id)
			Data.delete_pic_message(self.message.chat_id, message_id)
			date = Data.get_picture(pic_id)['date']
			username = Data.get_username(picture['user_id'])
			resp = self.rh.sendPhoto(self.message.chat_id, file_id, f'@{username} sent photo\non _{date}_')
			Data.add_message_to_picture(pic_id, self.message.chat_id, resp['result']['message_id'])

	def send_picture_certain_func(self):
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
	def send_picture_certain(self, callback):  # TODO: check this
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
		self.rh.delete(self.message.chat_id, self.message.message_id)

		text = f'Вы выбрали @{Data.get_username(int(self.message.data[1]))}.' \
		       f'\nОтправьте фото, которое должен получить ваш друг'
		self.rh.send(self.message.chat_id, text)

		return partial(Handler.send_picture_certain, callback=self.message)

	def delete_picture_func(self):
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

		return partial(Handler.return_messages, messages=messages_tobe_deleted)

	def delete_picture(self):
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
		return messages

	@staticmethod
	def invite_accept(user1_id: int, user2_id: int, rh: RequestHandler, message_id: int):
		user1_name = Data.get_username(user1_id)
		user2_name = Data.get_username(user2_id)

		Data.add_friend(user1_id, user2_id)

		friends1 = Data.get_users_friedList(user1_id)
		friends2 = Data.get_users_friedList(user2_id)

		if str(user2_id) in friends1 and str(user1_id) in friends2:
			rh.send(user1_id, f'{user2_name} was added to your friends list')
			rh.send(user2_id, f'{user1_name} was added to your friends list')
			rh.delete(user1_id, message_id)

	@staticmethod
	def is_friend(user1_id: int, user2_id: int):
		friends1 = Data.get_users_friedList(user1_id)
		friends2 = Data.get_users_friedList(user2_id)

		return str(user2_id) in friends1 and str(user1_id) in friends2
