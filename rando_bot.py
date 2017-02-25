import os
import time
import settings
from slackclient import SlackClient
from random import getrandbits
import humanize

AT_BOT = "<@{}>".format(settings.BOT_ID)

from faker import Factory
fake = Factory.create()
fake_jp = Factory.create('jp_JP')

command_list = {
    'flip coin': 'Heads' if not not getrandbits(1) else 'Tails',
    'lorem': fake.sentence(),
    'name': fake.name(),
    'chick': fake.name_female(),
    'dude': fake.name_male(),
    'weeb name': fake_jp.name(),
    'color': fake.safe_hex_color(),
    'company name': fake.company(),
    'mission statement': fake.catch_phrase(),
    'buzzword': fake.bs(),
    'deadline': humanize.naturaldate(fake.date_time_this_year(before_now=False, after_now=True, tzinfo=None)),
    'crunchtime': humanize.naturaltime(fake.date_time_this_year(before_now=False, after_now=True, tzinfo=None)),
    'domain': fake.domain_name(),
    'email': fake.email(),
    'username': fake.user_name(),
    'password': fake.password(),
    'job title': fake.job(),
}

slack_client = SlackClient(settings.SLACK_BOT_TOKEN)

def handle_command(command, channel):
    command = command.strip(' \t\n\r')

    response = "available commands: {}".format(", ".join(command_list.keys()))
    if command in command_list:
        response = command_list[command]
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        print("Rando ready to serve")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                print("[{}], {}".format(command, channel))
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Rando cannot connect to slack (invalid token/bot id)")
