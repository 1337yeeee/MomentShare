from RequestHandler import RequestHandler
from Message import Message
import DataHandler as Data
from Const import VERSION


class Handler:

	def __init__(self, message, rh: RequestHandler, do_this=None):
		self.rh = rh
		self.message = message
		if type(message) == Message:
			self.do_this = do_this
		else:
			self.chat_id = message['from']['id']
			self.data = message['data'].split('*')
			self.deal_with_callback()
			self.do_this = do_this

	def handler(self):
		if self.do_this is not None:
			return self.do_this(self)
		elif type(self.message) == Message:
			if self.message.is_command:
				return Handler.deal_with_command_func(self)

		return None

	@staticmethod
	def deal_with_command_func(self):
		if self.message.text == '/start':
			return self.start()

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
		if Data.get_user_id(self.message.mention) is not None:
			text = '{} хочет добавить вас в друзья.\n'.format('@'+self.message.username)
			user_id = Data.get_user_id(self.message.mention)
			keyboard = {'inline_keyboard': [[
				{'text': 'Accept', 'callback_data': f'invitation*{self.message.chat_id}'}
			]]}
			extra = ['reply_markup', keyboard]
			self.rh.send(user_id, text, extra)

			text = 'Приглашение для {} отправленно'.format(self.message.mention)
			self.rh.send(self.message.chat_id, text)

			return None

		return None

	def delete_friend_func(self):
		pass

	def send_picture_certain_func(self):
		pass

	def delete_picture_func(self):
		pass

	def deal_with_callback(self):
		if self.data[0] == 'invitation':
			Handler.invite_accept(self.chat_id, int(self.data[1]), self.rh)

	@staticmethod
	def invite_accept(user1_id: int, user2_id: int, rh: RequestHandler):
		# добавить друга, отправить всем, что он добавлен
		user1_name = Data.get_username(user1_id)
		user2_name = Data.get_username(user2_id)

		Data.add_friend(user1_id, user2_id)

		friends1 = Data.get_users_friedList(user1_id)
		friends2 = Data.get_users_friedList(user2_id)

		print(str(user2_id) in friends1)
		print(str(user1_id) in friends2)

		if str(user2_id) in friends1 and str(user1_id) in friends2:
			rh.send(user1_id, f'{user2_name} was added to your friends list')
			rh.send(user2_id, f'{user1_name} was added to your friends list')

# TODO: проверить друзья ли пользователи (уже) до добавления в список друзей
