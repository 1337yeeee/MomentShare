#

class Message:

	def __init__(self, message):
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
		offset = self.message['entities'][index]['offset']
		length = self.message['entities'][index]['length']

		return self.text[offset:length]

	@staticmethod
	def is_message(update):
		keys = update.keys()
		if 'message' in keys:
			return True
		else:
			return False
