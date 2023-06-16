import time
from datetime import datetime
from imessage_reader import fetch_data
import subprocess
import os

PASSWORD = os.environ.get('PASSWORD')
MY_NAME = os.environ.get('YOUR_NAME')
global messages


def update_fd():
    global messages

    while True:
        messages = sorted(fetch_data.FetchData().get_messages(), key=sort_key, reverse=True)
        print("Updated messages")
        print(messages)
        time.sleep(5)


def sort_key(item):
    return datetime.strptime(item[2], '%Y-%m-%d %H:%M:%S')


def send_ios_message(phone_number, message):
    applescript = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{phone_number}" of targetService
        send "{message}" to targetBuddy
    end tell
    '''
    try:
        subprocess.run(['osascript', '-e', applescript])
    except Exception as e:
        print(f"Error sending message to {phone_number}: {e}")
