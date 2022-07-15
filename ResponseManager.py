
# нужно понять, как вытягивать файлы с серверов телеграм

class Handler:

	def __init__(self, message, rh):
		self.message = message
		self.rh = rh
		self.handler()

	def handler(self):
		# ================
		# try:
		# 	if message['photo?']:
		# 		deal_with_photo_func(message)
		# except IndexError:
		# 	pass
		#
		# try:
		# 	if message['voice_message?']:
		# 		deal_with_voice_func(message)
		# except IndexError:
		# 	pass
		#
		# try:
		# 	if message['command']:
		# 		deal_with_command_func(message)
		# except IndexError:
		# 	pass
		# ==================

		if self.message.type == 'command':
			self.deal_with_command_func()
		elif self.message.type == 'text':
			self.deal_with_text_func()
		elif self.message.type == 'photo':
			self.deal_with_photo_func()
		elif self.message.type == 'contact':
			self.deal_with_contact_func()

		return None

	def deal_with_command_func(self):
		if self.message.text == '/start':
			self.start()

	def start(self):

		text = 'Hello {}\nRead this:\n1) invite friend\n2) delete friend\n\
3) send picture to a certain friend\n4) delete my picture'

		self.rh.send(self.message.chat_id, text)
