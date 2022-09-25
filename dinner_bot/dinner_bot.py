import json
import os
import urllib.parse
from random import randint

import urllib3

from constants import DinnerBotEventName
from dinner_table import DinnerTable

dinner_table = DinnerTable()
http = urllib3.PoolManager()
slack_url = os.getenv('WEBHOOK_URL')
secret_path = os.getenv('SECRET_PATH')


def lambda_handler(event, context):
	secret = event['params']['path']['secret']
	if secret != secret_path:
		raise Exception("That isn't going to work!")
	print(event)
	event_name = event['event_name']

	if event_name == DinnerBotEventName.SUGGEST:
		text_template = get_suggestions(event)
		body = {
			"text": text_template
		}
		encoded_data = json.dumps(body)
		http.request(
			'POST', slack_url, body=encoded_data,
			headers={'Content-type': 'application/json'}
		)
	elif event_name == DinnerBotEventName.RECORD:
		prepared_name = extract_res_name(event)
		try:
			dinner_table.record(prepared_name)
		except Exception as e:
			return {'status': 'Failed', 'reason': str(e)}

	elif event_name == DinnerBotEventName.ADD:
		try:
			res_name, menu = extract_res_info(event)

			if 'donjulio' in res_name.lower():
				return {'status': 'Failure', 'reason': 'Get that mess out of here!'}

			dinner_table.add(res_name, menu)
		except Exception as e:
			return {'status': 'Failed', 'reason': str(e)}
	elif event_name == DinnerBotEventName.MENU:
		db_style_name = extract_res_name(event)
		try:
			res = dinner_table.get_res(db_style_name)
		except Exception as e:
			return {'status': 'Failed', 'reason': str(e)}
		pretty_name = pretty_print(db_style_name)
		return {'status': 'Success', pretty_name: res['Menu']}
	elif event_name == DinnerBotEventName.LIST:
		formatted_suggestions = [pretty_print(i['ResName']) for i in dinner_table.get_suggestions()]
		return {'status': 'Success', 'restaurants': formatted_suggestions}

	else:
		raise NotImplementedError("No valid event name")

	return {"status": "Success"}


def get_suggestions(event):
	formatted_suggestions = [pretty_print(i['ResName']) for i in dinner_table.get_suggestions()]
	suggestions = []
	for i in range(5):
		my_int = randint(0, len(formatted_suggestions) - 1)
		suggestions.append(formatted_suggestions.pop(my_int))

	return 'It is time to pick food for tonight! We could have ' + ' or '.join(suggestions) + '!'


def pretty_print(res_name: str) -> str:
	rtn_str = ''
	for c in range(len(res_name)):
		new_char = res_name[c]
		if res_name[c].isupper() and c != 0:
			new_char = f' {res_name[c]}'
		rtn_str = rtn_str + new_char
	return rtn_str


def parse_params(event):
	body_params = event['body'].split('&')
	body = {i[0]: i[1] for i in [item.split('=') for item in body_params]}
	return body['text'].replace('+', ' ')


def extract_res_info(event):
	res_info = parse_params(event).split(',')
	if len(res_info) < 2:
		raise ValueError("No menu added for this restaurant")
	prepared_name = capitalize_name(res_info[0])
	return prepared_name, res_info[1]


def extract_res_name(event):
	res_name = parse_params(event)
	prepared_name = capitalize_name(res_name)
	return prepared_name


def capitalize_name(res_name: str) -> str:
	escaped_res_name = urllib.parse.unquote(res_name).title()
	print(escaped_res_name)
	return escaped_res_name.replace(' ', '')


if __name__ == '__main__':
	upvote_dict = {'params': {'path': {'secret': secret_path}, 'querystring': {}, 'header': {}},
				   'event_name': 'RECORD'}

	print(lambda_handler(upvote_dict, {}))
# lambda_handler({'event_name': DinnerBotEventName.SUGGEST}, {})
