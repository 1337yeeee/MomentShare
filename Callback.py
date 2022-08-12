#

class Callback:

	def __init__(self, update):
		self.callback = update
		self.data = self.callback['data'].split('*')
		self.chat_id = self.callback['from']['id']
		self.username = self.callback['from']['username']
		self.message_id = self.callback['message']['message_id']
		try:
			self.text = self.callback['message']['text']
		except KeyError:
			pass
