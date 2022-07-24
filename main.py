from RequestHandler import *
from Message import *
import ResponseManager
import DataHandler as Data
from Const import VERSION, tokenPath


def getToken():
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
	new_offset = None

	update_raw = rh.get(new_offset, 1)

	while len(update_raw['result']) != 0:
		new_offset = update_raw['result'][0]['update_id'] + 1
		update_raw = rh.get(new_offset, 1)


def main():
	Data.create_main_database()

	new_offset = None
	task_list = {}

	token = getToken()

	rh = RequestHandler(token)
	clear_updates(rh)

	while True:

		update_raw = rh.get(new_offset)
		chat_id = None
		update = {}

		try:
			update = update_raw['result'][0]
			message = Message(update['message'])
			chat_id = update['message']['chat']['id']

		except IndexError:
			continue
		except KeyError:
			try:
				message = update['callback_query']
			except KeyError:
				continue

		# update = update_raw['result'][0]
		# chat_id = update['message']['chat']['id']

		if chat_id not in task_list:
			task_list[chat_id] = None
		# resp_manager = ResponseManager.Handler(Message(update['message']), rh, task_list[chat_id])
		resp_manager = ResponseManager.Handler(message, rh, task_list[chat_id])
		task_list[chat_id] = resp_manager.handler()

		new_offset = update['update_id'] + 1

if __name__ == '__main__':
	print('version {}\ndoing time'.format(VERSION))
	main()


# TODO проверять callback_query по message_id
