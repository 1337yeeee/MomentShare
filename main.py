from RequestHandler import *
from Message import *
import ResponseManager as RM


def getToken(tokenPath):
	with open(tokenPath, 'r', encoding='utf-8') as tpF:
		token = str(tpF.readline)
		token = token.replace('\n', '').replace('\r', '').replace(' ', '')

	return token


def main():
	new_offset = None
	tokenPath = input("Enter path to your token: ")
	token = getToken(tokenPath)

	rh = RequestHandler(token)

	while True:

		update_raw = rh.get(new_offset)

		try:
			update_raw['result'][0]['message']
		except IndexError:
			continue

		update = update_raw['result'][0]

		# RM.handler(update['message']) # написать шутку которая решает что делать дальше
		RM.handler(Message(update['message']), rh)

if __name__ == '__main':
	main()
