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
		:param extra: extra parameters like reply_markup
		extra[0] is for a parameter and extra[1] is for additional data
		:return: optional. returns a request response in json
		"""
		method = 'sendMessage'
		params = {'chat_id': chat_id, 'text': text}
		if extra is not None:
			params[extra[0]] = json.dumps(extra[1])
		resp = r.post(self.url + method, params)
		return resp.json()

	def delete(self, chat_id: int, message_id: int):
		""" delete message by its id
		:param chat_id: chat id to delete message from
		:param message_id: the id of the message to be deleted
		:return: optional. returns a request response in json
		"""
		method = 'deleteMessage'
		params = {'chat_id': chat_id, 'message_id': message_id}
		resp = r.post(self.url + method, params)
		return resp.json()

	def sendPhoto(self, chat_id: int, file_id: str, caption: str = '', extra: list = None):
		""" send photo by its id
		:param chat_id: chat that should get the photo
		:param file_id: the id of the photo to be sent
		:param caption: Optional. photo caption
		:param extra: extra parameters like reply_markup
		:return: Optional. returns a request response in json
		"""
		method = 'sendPhoto'
		params = {'chat_id': chat_id, 'photo': file_id, 'caption': caption}
		if extra is not None:
			params[extra[0]] = json.dumps(extra[1])
		resp = r.post(self.url + method, params)
		return resp.json()

	def editMessage(self, chat_id: int, message_id: int, text: str, reply_markup=None):
		""" edit message by its id
		:param chat_id: chat where message was sent
		:param message_id: the id oh the message to be edited
		:param text: the text that will replace previous one
		:param reply_markup: reply markup to be passed
		:return: Optional. returns a request response in json
		"""
		method = 'editMessageText'
		params = {'chat_id': chat_id, 'message_id': message_id, 'text': text}
		if reply_markup is not None:
			params['reply_markup'] = json.dumps(reply_markup)
		resp = r.post(self.url + method, params)
		return resp.json()
