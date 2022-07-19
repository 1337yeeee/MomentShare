from RequestHandler import *
from Message import *
import ResponseManager as RM
import DataHandler as Data


def getToken():
	while True:
		try:
			tokenPath = 'token.info'
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

		try:
			update_raw['result'][0]['message']
		except IndexError:
			continue

		update = update_raw['result'][0]

		resp_manager = RM.Handler(Message(update['message']), rh)

		new_offset = update['update_id'] + 1

if __name__ == '__main__':
	main()
