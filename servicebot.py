#!/bin/python3
# token xoxb-142932977728-Yo1NrFsOWXvtDaEeA15geJYj
import time
import os
import sys
import re
import sqlite3
from slackclient import SlackClient
slack_token = "{paste slack token here}"
sc = SlackClient(slack_token)
PRETTY_NAME = "{name your bot...but pretty}"
BOT_NAME = "{name your bot}"
ACCEPTED_COMMAND = (("ack", "note", "list", "handoff"))
SCRIPT_DIR = os.getcwd()


def get_bot_id(BOT_NAME="{name your bot}"):
    if __name__ == "__main__":
        api_call = sc.api_call("users.list")
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('name') == BOT_NAME:
                    BOT_ID = user.get('id')
                    return BOT_ID
            else:
                print("could not find bot user with the name " + BOT_NAME)
                sys.exit()


BOT_ID = get_bot_id()
AT_BOT = "<@" + BOT_ID + ">"


def inc_ack(real_inc):
    print("I just acked something")


def inc_note(real_inc):
    print("I just noted something")


def inc_list():
    response = "Here is the list of currently open Incients:"
    conn = sqlite3.connect(SCRIPT_DIR + "/incident.db")  # INC
    c = conn3.cursor()
    for row in c.execute('SELECT * FROM INCS'):
        print(row[6] + " " + row[0] + " " + row[1] + " " + row[5] + " " + row[3])

    conn.commit()
    c.close()
    conn.close()
    sc.api_call("chat.postMessage", channel=channel,
                text=response, as_user=True)


def inc_handoff():
    print("I just made a handoff")


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Something is wrong."
    if command.startswith(ACCEPTED_COMMAND):
        response = "acknowledged"
        print(command)
        real_command = command.split(' ', 2)
        if len(real_command) >= 2:
            try:
                real_inc = real_command[1].upper()
                print(real_inc)
            except NameError:
                print("No Incident Number Provided")

        if real_command[0] == 'ack':
            inc_ack(real_inc)
        if real_command[0] == 'note':
            inc_note(real_inc)
        if real_command[0] == 'list':
            inc_list()
        if real_command[0] == 'handoff':
            inc_handoff()
    else:
        sc.api_call("chat.postMessage", channel=channel,
                    text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if sc.rtm_connect():
        print(PRETTY_NAME + " is connected and running!")
        while True:
            command, channel = parse_slack_output(sc.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
