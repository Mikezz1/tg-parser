#! pip install -qq telethon
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import date, datetime
import json
import yaml
import os
import nest_asyncio
import datetime as dt
import pandas as pd
nest_asyncio.apply()


# Load  config & start tg client
with open('config.yaml', 'r') as f:
	config = yaml.safe_load(f)
channels = config['channels']
client = TelegramClient('anon', config['api_id'], config['api_hash'])

# Utils
class DateTimeEncoder(json.JSONEncoder):
	"""
	https://stackoverflow.com/questions/12122007/python-json-encoder-to-support-datetime
	"""
	def default(self, o):
		if isinstance(o, datetime):
			return o.isoformat()
		if isinstance(o, bytes):
			return list(o)
		return json.JSONEncoder.default(self, o)

def process_json(config):
	out_path=config['output_path']
	columns = ['channel_url','date','message','views','forwards']
	print(1)
	df = pd.read_json(f'{out_path}/data.json')[columns]
	print(2)
	df.to_csv(f'{out_path}/data.csv')
	print(3)


async def dump_all_messages(channel, url, config):
	"""
	Function to load all messages from the channel with specified constraints
	Props to: https://proglib.io/p/pishem-prostoy-grabber-dlya-telegram-chatov-na-python-2019-11-06?comment=adcb82e8-bf47-4f29-b540-53df499a57c5,
				https://stackoverflow.com/questions/60507633/how-to-get-messages-of-the-public-channels-from-telegram
	"""
	offset_msg = config['offset_msg']    # номер записи, с которой начинается считывание
	limit_msg = config['limit_msg']   # максимальное число записей, передаваемых за один раз
	offset_date = None
	if isinstance(config['offset_date'], str):
		offset_date = dt.datetime.strptime(config['offset_date'], '%Y-%m-%d')
		  
	data = []   # список всех сообщений
	total_messages = 0
	total_count_limit = config['msg_limit']  

	while True:
		request = await client(GetHistoryRequest(
			peer=channel,
			offset_id=offset_msg,
			offset_date=offset_date,
			add_offset=0,
			limit=limit_msg,
			max_id=0,
			min_id=0,
			hash=0))
  
		if not request.messages:
			break

		messages = request.messages
		for message in messages:
			message_dict = message.to_dict()
			message_dict['channel_url'] = url
			data.append(message_dict)
   
		offset_msg = messages[len(messages) - 1].id
		total_messages = len(data)
		if total_count_limit != 0 and total_messages >= total_count_limit:
			break
	return data



async def main(config):
	data = []
	out_path=config['output_path']
	me = await client.get_me()
	for url in channels:
		print(f'Parsing {url}')
		channel = await client.get_entity(url)
		data += await dump_all_messages(channel, url, config)
	
	with open(f'{out_path}/data.json', 'w', encoding='utf8') as file:
		json.dump(data, file, ensure_ascii=False, cls=DateTimeEncoder)
   
   
# Run the script
if __name__ == '__main__':
	with client:
		client.loop.run_until_complete(main(config))
	process_json(config)