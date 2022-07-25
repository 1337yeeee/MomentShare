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
		if type(message) == Message:
			self.do_this = do_this
		elif type(message) == Callback:
			self.chat_id = message.chat_id
			self.data = message.data
			self.do_this = do_this

	def handler(self):
		if self.do_this is not None:
			return self.do_this(self)
		elif type(self.message) == Message:
			if self.message.is_command:
				return Handler.deal_with_command_func(self)
			elif self.message.is_photo:
				self.deal_with_photo_func()
		elif type(self.message) == Callback:
			return self.deal_with_callback()
		# if self.do_this is not None:
		# 	return self.do_this(self)

		return None

	@staticmethod
	def deal_with_command_func(self):
		if self.message.text == '/start':
			return self.start()

	def deal_with_photo_func(self):
		Data.add_picture_to_pictureTable(self.message.chat_id, self.message.photo_id)

		friends = Data.get_users_friedList(self.message.chat_id)

		for friend in friends:
			self.rh.sendPhoto(int(friend), self.message.photo_id, f'{self.message.username} делится с Вами фотографией')

	def deal_with_callback(self):
		if self.data[0] == 'invitation':
			Handler.invite_accept(self.chat_id, int(self.data[1]), self.rh, self.message.message_id)
		elif self.data[0] == 'delete_friend':
			Handler.delete_friend(self.chat_id, int(self.data[1]), self.rh, self.message.message_id)
		elif self.data[0] == 'pic_certain':
			return self.await_photo()

		return None

	def start(self):

		text = 'Hello {}\nRead this:\n1) invite friend\n'.format(self.message.name) + \
		       '2) delete friend\n3) send picture to a certain friend\n4) delete my picture' + \
		       '\n------------\nversion: {}'.format(VERSION)

		Data.add_user_to_usersTable(self.message.chat_id, self.message.username)

		self.rh.send(self.message.chat_id, text)
		return Handler.choose_after_start

	@staticmethod
	def choose_after_start(self):
		do_this = None

		if self.message.text == '1':
			do_this = self.invite_friend_func()
		elif self.message.text == '2':
			do_this = self.delete_friend_func()
		elif self.message.text == '3':
			do_this = self.send_picture_certain_func()
		elif self.message.text == '4':
			do_this = self.delete_picture_func()

		return do_this

	def invite_friend_func(self):
		text = 'Напишите username друга, которого желаете добавить\n' +\
		       'Note that your friend should start this bot to be in your friend list'

		self.rh.send(self.message.chat_id, text)

		return Handler.invite_friend

	@staticmethod
	def invite_friend(self):
		if Data.get_user_id(self.message.mention) is None:
			return None

		if self.message.mention == self.message.username:
			self.rh.send(self.message.chat_id, 'Вы не можете добавить себя к себе же в друзья')
			return None

		user_id = Data.get_user_id(self.message.mention)

		if Handler.is_friend(user_id, self.message.chat_id):
			return None

		text = '{} хочет добавить вас в друзья.\n'.format('@'+self.message.username)
		keyboard = {'inline_keyboard': [[
			{'text': 'Accept', 'callback_data': f'invitation*{self.message.chat_id}'}
		]]}
		extra = ['reply_markup', keyboard]
		self.rh.send(user_id, text, extra)

		text = 'Приглашение для {} отправленно'.format(self.message.mention)
		self.rh.send(self.message.chat_id, text)

		return None

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

		return None

	@staticmethod
	def delete_friend(chat_id: int, user_id: int, rh: RequestHandler, message_id: int):
		user1_name = Data.get_username(chat_id)
		user2_name = Data.get_username(user_id)

		Data.delete_friend(chat_id, user_id)

		friends1 = Data.get_users_friedList(chat_id)
		friends2 = Data.get_users_friedList(user_id)

		if str(user_id) not in friends1 and str(chat_id) not in friends2:
			rh.send(chat_id, f'{user2_name} was deleted from your friend list')
			rh.send(user_id, f'{user1_name} deleted you from theirs friend list')
			rh.delete(chat_id, message_id)

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
	def send_picture_certain(self, callback):
		caption = f'@{self.message.username} отправил тебе фото'

		Data.add_picture_to_pictureTable(self.message.chat_id, self.message.photo_id)

		self.rh.sendPhoto(int(callback.data[1]), self.message.photo_id, caption)

		return None

	def await_photo(self):
		return partial(Handler.send_picture_certain, callback=self.message)

	def delete_picture_func(self):
		pass

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
