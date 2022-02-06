# tgparser - Load messages from Telegram channels
Scipt to simply load messages from multiple tg channels
### Setup:
- Go to https://my.telegram.org/apps and register app with your number. Copy `api_id` and `api_hash`. 
- Fill `api_id` and `api_hash` in `config.yaml` 
- Add channel urls to  `channels` in `comfig.yaml`
- Speccify max number of messages to load with `msg_limit`, `offset_date` in format of "2021-01-01" or `offset_msg` to set offset
### Run:
```
pip install -r requirements.txt
python3 run main.py
```
Then you will need to enter your telegram credentials.
