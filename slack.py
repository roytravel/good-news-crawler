import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class Slack(object):
    def __init__(self):
        self.client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

    def send(self, url, title, time):
        try:
            response = self.client.chat_postMessage(channel='#good-news', text="{} ({})\n{}".format(url, time, title))
            #assert response["message"]["text"] == "{} ({})\n{}".format(url, time, title)

        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
