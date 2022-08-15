import os
from datetime import datetime
import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer


class DinnerTable:
	def __init__(self):
		self.deserializer = TypeDeserializer()
		self.serializer = TypeSerializer()
		if os.getenv('LOACL'):
			self.session = boto3.Session(profile_name='default')
		self.name = os.getenv('DINNER_TABLE_NAME')
		self.dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
		self.resource = boto3.resource('dynamodb')

	def get_suggestions(self):
		res = self.dynamodb_client.scan(TableName=self.name)
		return [self._deserialize(item) for item in res['Items']]

	def record(self, res_name):
		res_list = self.get_res(res_name)
		if not res_list:
			raise Exception("Res not found!")
		res = res_list[0]
		votes = res.get('Votes', 0)
		votes += 1
		res['Votes'] = votes
		res['LastVote'] = int(datetime.utcnow().timestamp())
		self.dynamodb_client.put_item(TableName=self.name, Item=self._serialize(res))

	def add(self, res_name, dist):
		res_list = self.get_res(res_name)
		if res_list:
			raise Exception("Found existing!")

		self.dynamodb_client.put_item(TableName=self.name,
									  Item=self._serialize({"ResName": res_name, "Distance": str(dist)}))

	def get_res(self, res_name):
		res = self.dynamodb_client.query(
			TableName=self.name,
			KeyConditionExpression='ResName = :val1',
			ExpressionAttributeValues={':val1': {'S': res_name}}
		)
		return [self._deserialize(item) for item in res['Items']]


	def _serialize(self, raw_data):
		result = {}
		for key, val in raw_data.items():
			result[key] = self.serializer.serialize(val)
		return result

	def _deserialize(self, raw_data):
		result = {}
		if not raw_data:
			return result

		for key, val in raw_data.items():
			result[key] = self.deserializer.deserialize(val)

		return result
