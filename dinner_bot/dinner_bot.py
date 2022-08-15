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
	event_name = event['event_name']

	if event_name == DinnerBotEventName.SUGGEST:
		text_template = get_suggestions(event)
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
	elif event_name == DinnerBotEventName.RECORD:
		prepared_name = extract_res_name(event)
		try:
			dinner_table.record(prepared_name)
		except Exception as e:
			return {'status': 'Failed', 'msg': e}

	elif event_name == DinnerBotEventName.ADD:
		dinner_table.add(extract_res_name(event), 1)
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


def extract_res_name(event):
	body_params = event['body'].split('&')
	print(body_params)
	body = {i[0]: i[1] for i in [item.split('=') for item in body_params]}
	res_name = body['text']
	prepared_name = capitalize_name(res_name)
	return prepared_name


def capitalize_name(res_name: str) -> str:
	return urllib.parse.unquote(res_name).title().replace(' ', '')


if __name__ == '__main__':
	upvote_dict = {'params': {'path': {'secret': secret_path}, 'querystring': {}, 'header':
		{'Accept': 'application/json,*/*', 'Accept-Encoding': 'gzip,deflate',
		 'Content-Type': 'application/x-www-form-urlencoded', 'Host': 'l2pmhjm02g.execute-api.us-east-1.amazonaws.com',
		 'User-Agent': 'Slackbot 1.0 (+https://api.slack.com/robots)',
		 'X-Amzn-Trace-Id': 'Root=1-62f975d2-748e4756756ba4c57ffef1c9', 'X-Forwarded-For': '3.239.114.176',
		 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https', 'X-Slack-Request-Timestamp': '1660515794',
		 'X-Slack-Signature': 'v0=b22170b3062f34b87252d1459b9f3737dd1d1e3af543f1c182a0a7e3213e0e9e'}},
				   'body': 'token=nPFTWyM3M22ntvMVAp2TdhEk&team_id=TL24XMDJP&team_domain=mixed-feelings&channel_id=C03TLFH28N7&channel_name=johns-channel&user_id=UL76E8UMP&user_name=konderla.john&command=%2Fdb_record&text=mellow mushroom&api_app_id=A03TP2E8R7W&is_enterprise_install=false&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FTL24XMDJP%2F3932210732822%2Fia7FhbX7nx4QEVE62y1MZB7n&trigger_id=3938823935058.682167727635.1027454cb4e022bee844502b88eae2a2',
				   'event_name': 'UPVOTE'}

	print(lambda_handler(upvote_dict, {}))
# lambda_handler({'event_name': DinnerBotEventName.SUGGEST}, {})
