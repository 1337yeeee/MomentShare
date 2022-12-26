#

class Message:

	def __init__(self, message):
		""" If update contains a 'message'. For easier work with the update

		:param message: update from Telegram API UPDATE['result'][0]['message']
		"""
		self.message = message
		self.message_id = message['message_id']
		self.name = message['chat']['first_name']
		self.chat_id = message['chat']['id']
		self.username = message['from']['username']  # TODO не у всех есть username
		self.text = ''
		self.is_command = False
		self.is_mention = False
		self.is_hashtag = False
		self.is_photo = False
		self.command = ''
		self.mention = ''
		self.hashtag = ''
		self.photo_id = ''

		try: self.text = message['text']
		except KeyError: self.text = None

		try:
			if message['photo']:
				self.is_photo = True
				self.photo_id = message['photo'][-1]['file_id']
		except KeyError:
			pass

		try:
			for i in range(len(message['entities'])):
				if message['entities'][i]['type'] == 'bot_command':
					self.is_command = True
					self.command = self.get_from_text(i)

				elif message['entities'][i]['type'] == 'mention':
					self.is_mention = True
					self.mention = self.get_from_text(i).replace('@', '')
				elif message['entities'][i]['type'] == 'hashtag':
					self.is_hashtag = True
					self.hashtag = self.get_from_text(i)
		except KeyError:
			pass

	def get_from_text(self, index):
		""" Telegram sends information about where in the text of the message are
		'bot_command', 'mention', 'hashtag' etc.

		:param index: index of message['entities'] - that is a list
		:return: the 'bot_command' or the 'mention', or the 'hashtag' etc.
		"""
		offset = self.message['entities'][index]['offset']
		length = self.message['entities'][index]['length']

		return self.text[offset:length]
