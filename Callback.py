#

class Callback:

	def __init__(self, update):
		""" If update contains a 'callback_query'. For easier work with the update

		:param update: update from Telegram API UPDATE['result'][0]['callback_query']
		"""
		self.callback = update
		self.data = self.callback['data'].split('*')
		self.chat_id = self.callback['from']['id']
		self.username = self.callback['from']['username']
		self.message_id = self.callback['message']['message_id']
		try:
			self.text = self.callback['message']['text']
		except KeyError:
			pass
