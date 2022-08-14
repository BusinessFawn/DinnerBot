import json
import os

import urllib3

from constants import DinnerBotEventName
from dinner_table import DinnerTable

dinner_table = DinnerTable()
http = urllib3.PoolManager()
slack_url = os.getenv('WEBHOOK_URL')


def lambda_handler(event, context):
	event_name = event['event_name']

	if event_name == DinnerBotEventName.SUGGEST:
		text_template = get_suggestions(event)
	else:
		raise NotImplementedError("No valid event name")
	body = {
		"text": text_template
	}
	encoded_data = json.dumps(body)
	print(encoded_data)
	r = http.request(
		'POST', slack_url, body=encoded_data,
		headers={'Content-type': 'application/json'}
	)
	print(r.status)
	print(r.data)
	return json.dumps({"status": "Success"})


def get_suggestions(event):
	suggestions = [pretty_print(i['ResName']) for i in dinner_table.get_suggestions()]

	return 'It is time to pick food for tonight! We could have ' + ' or '.join(suggestions) + '!'


def pretty_print(res_name: str) -> str:
	rtn_str = ''
	for c in range(len(res_name)):
		new_char = res_name[c]
		if res_name[c].isupper() and c != 0:
			new_char = f' {res_name[c]}'
		rtn_str = rtn_str + new_char
	return rtn_str


if __name__ == '__main__':
	lambda_handler({'event_name': DinnerBotEventName.SUGGEST}, {})
