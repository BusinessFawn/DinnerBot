import os

import boto3
from boto3.dynamodb.types import TypeDeserializer


class DinnerTable:
	def __init__(self):
		self.deserializer = TypeDeserializer()
		if os.getenv('LOACL'):
			self.session = boto3.Session(profile_name='default')
		self.name = os.getenv('DINNER_TABLE_NAME')
		self.dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
		self.resource = boto3.resource('dynamodb')

	def get_suggestions(self):
		res = self.dynamodb_client.scan(TableName=self.name)
		return [self._deserialize(item) for item in res['Items']]

	def _deserialize(self, raw_data):
		result = {}
		if not raw_data:
			return result

		for key, val in raw_data.items():
			result[key] = self.deserializer.deserialize(val)

		return result
