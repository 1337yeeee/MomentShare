from Message import Message
from RequestHandler import RequestHandler
import DataHandler as Data


class Handler:

	def __init__(self, message: Message, rh: RequestHandler, do_this=None):
		self.message = message
		self.rh = rh
		if do_this is None:
			self.do_this = self.handler()
		else:
			self.do_this = do_this
			self.do_this(self)

	def handler(self):
		if self.message.is_command:
			return Handler.deal_with_command_func

		return None

	@staticmethod
	def deal_with_command_func(self):
		if self.message.text == '/start':
			return self.start()

	def start(self):

		text = 'Hello {}\nRead this:\n1) invite friend\n'.format(self.message.name) +\
		       '2) delete friend\n3) send picture to a certain friend\n4) delete my picture'

		Data.add_user_to_usersTable(self.message.chat_id, self.message.username)

		self.rh.send(self.message.chat_id, text)
		return Handler.choose_after_start

	@staticmethod
	def choose_after_start(self):
		do_this = None

		if self.message.text == '1':
			self.invite_friend_func()
		elif self.message.text == '2':
			self.delete_friend_func()
		elif self.message.text == '3':
			self.send_picture_certain_func()
		elif self.message.text == '4':
			self.delete_picture_func()

		return do_this

	def invite_friend_func(self):

		text = 'Напишите username друга, которого желаете добавить\n' +\
		       'Note that your friend should start this bot to be in your friend list'

		self.rh.send(self.message.chat_id, text)

		return Handler.invite_friend

	@staticmethod
	def invite_friend(self):
		if Data.get_user_id(self.message.mention) is not None:
			text = '{} хочет добавить вас в друзья.\n'.format('@'+self.message.username) +\
				   '1. Accept / 2. Deny'
			user_id = Data.get_user_id(self.message.mention)

			self.rh.send(user_id, text)

			text = 'Приглашение для {} отправленно'.format(self.message.mention)

		return None

	def delete_friend_func(self):
		pass

	def send_picture_certain_func(self):
		pass

	def delete_picture_func(self):
		pass
