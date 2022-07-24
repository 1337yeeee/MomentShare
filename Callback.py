#

class Callback:

	def __init__(self, update):
		self.callback = update['callback_query']
		self.data = self.callback['data']
		self.chat_id = self.callback['from']['id']
		self.username = self.callback['from']['username']
		self.message_id = self.callback['message']['message_id']
		self.text = self.callback['message']['text']
