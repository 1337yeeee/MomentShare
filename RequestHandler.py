import requests as r
import json


class RequestHandler:

	def __init__(self, token: str):
		""" Handles requests
		:param token: telegram bot token
		"""
		self.token = token
		self.url = 'https://api.telegram.org/bot' + self.token + '/'

	def get(self, offset: int = None, timeout=30):
		""" get update from Telegram API server
		:param offset: update id to get exact update
		:param timeout: time to wait till update pop up
		:return: a request response in json
		"""
		method = 'getUpdates'
		params = {'timeout': timeout, 'offset': offset}
		resp = r.get(self.url + method, params)
		return resp.json()

	def send(self, chat_id: int, text: str, extra: list = None):
		""" send message to user
		:param chat_id: id to send to the text
		:param text: the text to send to
		:param extra: extra parameters like reply_markup.
		extra[0] is for a parameter and extra[1] is for additional data
		:return: optional. returns a request response
		"""
		method = 'sendMessage'
		params = {'chat_id': chat_id, 'text': text}
		if extra is not None:
			params[extra[0]] = json.dumps(extra[1])
		resp = r.post(self.url + method, params)
		return resp

