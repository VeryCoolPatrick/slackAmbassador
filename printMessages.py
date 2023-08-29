#############################################################################################
# This script is just to print the json of recent slack messages for debugging
#############################################################################################

import os
import logging
from slackFunctions import *
from flask import Flask, request, Response
from config import *
from dotenv import load_dotenv
import slack_bolt
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

slackApp = slack_bolt.App(token = os.environ.get("SLACK_BOT_TOKEN"), signing_secret = os.environ.get("SLACK_SIGNING_SECRET"))
minTime = datetime.datetime.now() 
minTime -= datetime.timedelta(hours = 24)
minTime = time.mktime(minTime.timetuple()) # Time must be given as unix timestamp
for message in slackApp.client.conversations_history(channel = getSlackChannelId(slackApp.client, SLACK_CHANNEL), oldest = minTime)["messages"][0:3]:
    sectionText = message['text']
    sectionText = mentionToName(message = sectionText, slackClient = slackApp.client) # Mentions and emoticons must be converted before HTML
    sectionText = emoji_data_python.replace_colons(sectionText)
    sectionText = slackdown.render(sectionText) # Convert markdown to HTML
    if "files" in message:
            for file in message["files"]:
                if "image" in file["mimetype"]:
                    sectionText += imageToHtml(file, os.environ.get("SLACK_BOT_TOKEN")) # Image added as HTML to text section as image section is broken in teams
    print(sectionText)
    # print(message, "\n-----------------------------")
    # print(slackApp.client.users_info(user = message["user"]), "\n======================")
    # print(message['text'], "\n-----------------------------")
    # sectionText = emoji_data_python.replace_colons(message['text']) # Emoticons must be converted before HTML
    # print(sectionText, "\n-----------------------------")
    # sectionText = slackdown.render(sectionText)
    # print(sectionText, "\n===============================")