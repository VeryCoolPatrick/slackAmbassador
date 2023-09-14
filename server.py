########################################################################################################
# This script starts a flask server to communicate with slack and teams.
# It uses the slack bolt APIs and the slack event adapter to make events like mentions more convenient.
# Communication with ms teams is done through simple http requests.
# Webhooks and keys are stored as environmental variables in .env .
# config.py stores any insecure configuration but this is hardly used and could probably be removed.
########################################################################################################

import os
from dotenv import load_dotenv
import logging
import slackFunctions as sf
from flask import Flask, request
import slack_bolt
from slackeventsapi import SlackEventAdapter
import msteams_verify
import requests
import re

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

flaskApp = Flask("__name__")
slackEventAdapter = SlackEventAdapter(os.environ.get("SLACK_SIGNING_SECRET"), "/slack/", flaskApp)

slackApp = slack_bolt.App(token = os.environ.get("SLACK_BOT_TOKEN"), signing_secret = os.environ.get("SLACK_SIGNING_SECRET"))
channelId = sf.getSlackChannelId(slackApp.client, os.environ.get("SLACK_CHANNEL"))
botId = slackApp.client.auth_test()["user_id"]

# When the bot is mentioned a reply is given containing the id of the message forwarded to teams
@slackEventAdapter.on("app_mention")
def mentionEvent(eventData):
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
    slackApp.client.chat_postMessage(text = f"Teams can see this thread, say hi!\n`{response.json()['messageId']}`", thread_ts = message["ts"], channel = channelId)
    return 

# If a slack message is a reply to one forwarded to teams the reply is also sent to teams
@slackEventAdapter.on("message")
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
    return

# This response to an MS Teams outgoing webhook
@flaskApp.route("/teams/", methods = ["POST"])
@msteams_verify.verify_hmac(os.environ.get("TEAMS_OUTGOING_TOKEN"))
def teamsMessage():
    data = request.data
    logging.info(data)
    return {'type' : 'message', 'text' : 'This is a reply'}

# Verification for slack that this URL is valid
@slackEventAdapter.on("url_verification")
def challengeResponse(eventData):
    if request.json["type"] == "url_verification":
        return {"challenge" : request.json["challenge"]}

if __name__ == "__main__":
    flaskApp.run(debug=True)