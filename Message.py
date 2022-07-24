#

class Message:

	def __init__(self, update):
		self.message_id = None
		self.data = None
		self.callback = None
		self.message = None
		self.name = None
		self.chat_id = None
		self.username = None
		self.text = ''
		self.is_command = False
		self.is_mention = False
		self.is_hashtag = False
		self.is_photo = False
		self.command = ''
		self.mention = ''
		self.hashtag = ''
		self.photo_id = ''

		update_type = ''
		try:
			if update['message']:
				update_type = 'message'
		except KeyError:
			try:
				if update['callback_query']:
					update_type = 'callback'
			except KeyError as e:
				print('an error occurred in Message constructor\n', e)
				print(update)

		if update_type == 'message':
			self.message_constructor(update)
		elif update_type == 'callback':
			self.callback_constructor(update)

	def message_constructor(self, update):
		self.message = update['message']
		self.name = self.message['chat']['first_name']
		self.chat_id = self.message['chat']['id']
		self.username = self.message['from']['username']
		self.message_id = self.message['message_id']

		try:
			self.text = self.message['text']
		except KeyError:
			self.text = None

		try:
			if self.message['photo']:
				self.is_photo = True
				self.photo_id = self.message['photo'][0][3]['file_id']
		except KeyError:
			pass

		try:
			for i in range(len(self.message['entities'])):
				if self.message['entities'][i]['type'] == 'bot_command':
					self.is_command = True
					self.command = self.get_from_text(i)

				elif self.message['entities'][i]['type'] == 'mention':
					self.is_mention = True
					self.mention = self.get_from_text(i).replace('@', '')
				elif self.message['entities'][i]['type'] == 'hashtag':
					self.is_hashtag = True
					self.hashtag = self.get_from_text(i)
		except KeyError:
			pass

	def callback_constructor(self, update):
		self.callback = update['callback_query']
		self.data = self.callback['data']
		self.chat_id = self.callback['from']['id']
		self.username = self.callback['from']['username']
		self.message_id = self.callback['message']['message_id']
		self.text = self.callback['message']['text']

	def get_from_text(self, index):
		offset = self.message['entities'][index]['offset']
		length = self.message['entities'][index]['length']

		return self.text[offset:length]
