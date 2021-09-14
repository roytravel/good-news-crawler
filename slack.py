import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class Slack(object):
    def __init__(self):
        client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

    def send(self):
        try:
            response = client.chat_postMessage(channel='#good-news', text="[*] Slack bot test")
            assert response["message"]["text"] == "[*] Slack bot test"

        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
