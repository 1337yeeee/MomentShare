from Const import VERSION, tokenPath
from RequestHandler import RequestHandler
import DataHandler as Data
import ResponseManager
from Callback import *
from Message import *


def getToken():
	""" Extract the token from file

	:return: Telegram Bot token
	"""
	while True:
		try:
			with open(tokenPath, 'r', encoding='utf-8') as tpF:
				token = str(tpF.readline())
				token = token.replace('\n', '').replace('\r', '').replace(' ', '')
			break
		except FileNotFoundError:
			print('wrong')

	return token


def clear_updates(rh):
	""" Clears updates that were stored before application was started

	:param rh: RequestHandler object
	"""
	new_offset = None

	update_raw = rh.get(new_offset, 1)

	while len(update_raw['result']) != 0:
		new_offset = update_raw['result'][0]['update_id'] + 1
		update_raw = rh.get(new_offset, 1)


def main():
	Data.create_main_database()

	new_offset = None  # later new_offset = update['update_id'] + 1
	task_list = {}  # contains {chat_id: method} for ResponseManager.do_this

	token = getToken()

	rh = RequestHandler(token)
	clear_updates(rh)

	while True:

		update_raw = rh.get(new_offset)
		update = {}

		try:
			update = update_raw['result'][0]
			message = Message(update['message'])
			chat_id = update['message']['chat']['id']
		except IndexError:
			continue
		except KeyError:
			try:
				message = Callback(update['callback_query'])
				chat_id = message.chat_id
			except KeyError as e:
				print(e)
				continue

		if chat_id not in task_list and chat_id is not None:
			task_list[chat_id] = None

		if chat_id is not None:
			resp_manager = ResponseManager.Handler(message, rh, task_list[chat_id])
			task_list[chat_id] = resp_manager.handler()
		else:
			ResponseManager.Handler(message, rh)

		new_offset = update['update_id'] + 1

if __name__ == '__main__':
	print('version {}\ndoing time'.format(VERSION))
	main()
