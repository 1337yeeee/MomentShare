import requests as r


class RequestHandler:
	""" Handles requests
		token = telegram bot token
	"""

	def __init__(self, token):
		self.token = token
		self.url = 'https://api.telegram.org/bot' + self.token

	def get(self, offset=None, timeout=30):
		method = 'getUpdates'
		params = {timeout, offset}
		resp = r.get(self.url + method, params)
		return resp.json()

	def send(self, chat_id, text):
		method = 'sendMessage'
		params = {'chat_id': chat_id, 'text': text}
		resp = r.post(self.url + method, params)
		return resp

