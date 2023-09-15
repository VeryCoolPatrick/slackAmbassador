########################################################################################################
# This is a first draft of the an AWS lambda function. It is completely untested.
# The code is largely reused from server.py
########################################################################################################

import slack_bolt
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
import os
import logging
import slackFunctions as sf
import requests
import re

# from dotenv import load_dotenv # I don't think these are needed for environmental variables
# load_dotenv()

SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

slackApp = slack_bolt.App(token = os.environ.get("SLACK_BOT_TOKEN"), signing_secret = os.environ.get("SLACK_SIGNING_SECRET"), process_before_response = True)
channelId = sf.getSlackChannelId(slackApp.client, os.environ.get("SLACK_CHANNEL"))
botId = slackApp.client.auth_test()["user_id"]

# When the bot is mentioned a reply is given containing the id of the message forwarded to teams
@slackApp.event("app_mention")
def mentionEvent(eventData, say):
    message = eventData["event"]
    if "thread_ts" in message: 
        if message["ts"] != message["thread_ts"]: # Check that the message is not a reply
            return
        thread = slackApp.client.conversations_replies(channel = channelId, ts = message["thread_ts"])["messages"]
        for reply in thread:
            if reply["user"] == botId: # Check that the bot hasn't already responded
                return
    text = sf.slackMessageToHtml(message, slackApp.client, os.environ.get("SLACK_BOT_TOKEN"), channelId)
    response = requests.post(
            os.environ.get("TEAMS_FLOW_URL"),
            json = {
                "message" : text,
                "threadId" : "" # Empty string denotes this message is the head of thread
            },
            headers = {"Content-Type": "application/json"},
            timeout=60
        )
    say(f"Teams can see this thread, say hi!\n`{response.json()['messageId']}`")
    # slackApp.client.chat_postMessage(text = f"Teams can see this thread, say hi!\n`{response.json()['messageId']}`", thread_ts = message["ts"], channel = channelId)

# If a slack message is a reply to one forwarded to teams the reply is also sent to teams
@slackApp.event("message")
def messageEvent(eventData):
    message = eventData["event"]
    if ("thread_ts" not in message) or( message["ts"] == message["thread_ts"]) or (message["user"] == botId):  # If message is not a reply or the poster is this bot, do nothing
        return
    thread = slackApp.client.conversations_replies(channel = channelId, ts = message["thread_ts"])["messages"]
    if f"<@{botId}>" not in thread[0]["text"]: # Check that the original post called the bot
        return
    for reply in thread:
        if reply["user"] != botId: # Find the message the bot sent
            continue
        teamsMessageId = re.search(r"`(\w+)`", reply["text"]).group()[1:-1] # Get the teams ID from the bot message
        break

    text = sf.slackMessageToHtml(message, slackApp.client, os.environ.get("SLACK_BOT_TOKEN"), channelId)
    requests.post(
            os.environ.get("TEAMS_FLOW_URL"),
            json=  {
                "message" : text,
                "threadId" : teamsMessageId
            },
            headers = {"Content-Type": "application/json"},
            timeout=60,
        )

def handler(event, context):
    slackHandler = SlackRequestHandler(app = slackApp)
    return slackHandler.handle(event, context)