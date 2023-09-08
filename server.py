from config import *
import os
from dotenv import load_dotenv
import logging
import slackFunctions as sf
# import slackdownToRichText as richText
from flask import Flask, request
# from flask_apscheduler import APScheduler
import slack_bolt
# from slack_bolt.adapter.socket_mode import SocketModeHandler
from slackeventsapi import SlackEventAdapter
import pymsteams
import msteams_verify
import time
import requests
import re
import json

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

flaskApp = Flask("__name__")
slackEventAdapter = SlackEventAdapter(os.environ.get("SLACK_SIGNING_SECRET"), "/slack/", flaskApp)
# scheduler = APScheduler()
# scheduler.api_enabled = True
# scheduler.init_app(flaskApp)
# scheduler.start()

slackApp = slack_bolt.App(token = os.environ.get("SLACK_BOT_TOKEN"), signing_secret = os.environ.get("SLACK_SIGNING_SECRET"))
channelId = sf.getSlackChannelId(slackApp.client, SLACK_CHANNEL)
botId = slackApp.client.auth_test()["user_id"]


# # On command every message from the specified period of time (24h default) and its replies are posted to teams
# @slackApp.command("/test")
# def testCommand(body, ack):
#     ack() # Must acknowledge within 3? second of slash command
#     activeThreads = sf.getActiveThreads(slackApp.client, channelId, OLDEST_THREAD_HOURS)
#     for thread in reversed(activeThreads): # Reverse to send oldest message first
#         message = pymsteams.connectorcard(os.environ.get("TEAMS_HOOK"))
#         message.addLinkButton("Click here to view on slack", f"https://slack.com/app_redirect?channel={channelId}")
#         message.summary("Slack Ambassador Bot")
#         for reply in thread:
#             message.addSection(sf.messageToSection(slackApp.client, reply, os.environ.get("SLACK_BOT_TOKEN")))
#         message.send()
#         time.sleep(0.25) # Teams limited to 4 requests per second

# @slackApp.command("/teams")
# def testCommand2(body, ack):
#     ack() # Must acknowledge within 3? second of slash command
#     print(body)
#     # message = body["event"]
#     # teamsMessage = pymsteams.connectorcard(os.environ.get("TEAMS_HOOK"))
#     # teamsMessage.addLinkButton("Click here to view on slack", f"https://slack.com/app_redirect?channel={channelId}")
#     # teamsMessage.summary("Slack Ambassador Bot")
#     # teamsMessage.addSection(messageToSection(slackApp.client, message, os.environ.get("SLACK_BOT_TOKEN")))
#     # teamsMessage.send()
    

# When the bot is mentioned a reply is given containing the id of the message forwarded to teams
# @slackApp.event("app_mention")
# def mentionEvent(body, ack, say):
@slackEventAdapter.on("app_mention")
def mentionEvent(eventData):
    message = eventData["event"]
    if "thread_ts" in message:
        if message["ts"] != message["thread_ts"]:
            return
        thread = slackApp.client.conversations_replies(channel = channelId, ts = message["thread_ts"])["messages"]
        cancel = False
        for reply in thread:
            if reply["user"] == botId:
                cancel = True
                break
        if(cancel):
            return
    # user = slackApp.client.users_info(user = message["user"])["user"]
    # text = message["text"]
    # text = sf.mentionToName(text, slackApp.client)
    # text = sf.emoji_data_python.replace_colons(text)
    # text = richText.format(text, slackApp.client)
    text = sf.slackMessageToHtml(message, slackApp.client, os.environ.get("SLACK_BOT_TOKEN"), channelId)
    response = requests.post(
            os.environ.get("TEAMS_FLOW_URL"),
            json = {
                # "userName" : sf.getUsername(user),
                # "avatar" : user["profile"]["image_192"],
                "message" : text,
                # "images" : sf.slackMessageToImageRun(message, slackApp.client, os.environ.get("SLACK_BOT_TOKEN")),
                "threadId" : "" # Empty string denotes this message is the head of thread
            },
            headers = {"Content-Type": "application/json"},
            timeout=60
        )
    slackApp.client.chat_postMessage(text = f"Teams can see this thread, say hi!\n`{response.headers['messageId']}`", thread_ts = message["ts"], channel = channelId)
    # say(f"Teams can see this thread, say hi!\n`{response.headers['messageId']}`", thread_ts = message["ts"])

    # with open("threadsList.txt", "a+") as threadsList: # Adds ts to be sent on schedule
    #     threadsList.seek(0)
    #     if message["ts"] in threadsList.read():
    #             return
    #     threadsList.write(message["ts"])
    #     threadsList.write("\n")
    #     say("Teams will see this thread, say hi!", thread_ts = message["ts"])
    return 

# If a slack message is a reply to one forwarded to teams the reply is also sent to teams
# @slackApp.message()
@slackEventAdapter.on("message")
def messageEvent(eventData):
    message = eventData["event"]
    if ("thread_ts" not in message) or( message["ts"] == message["thread_ts"]) or (message["user"] == botId):
        return {"ok" : True}
    thread = slackApp.client.conversations_replies(channel = channelId, ts = message["thread_ts"])["messages"]
    if f"<@{botId}>" not in thread[0]["text"]:
        return {"ok" : True}
    for reply in thread:
        if reply["user"] != botId:
            continue
        teamsMessageId = re.search(r"`(\w+)`", reply["text"]).group()[1:-1]
        break

    text = sf.slackMessageToHtml(message, slackApp.client, os.environ.get("SLACK_BOT_TOKEN"), channelId)
    requests.post(
            os.environ.get("TEAMS_FLOW_URL"),
            json=  {
                # "userName" : sf.getUsername(user),
                # "avatar" : user["profile"]["image_192"],
                "message" : text,
                # "images" : sf.slackMessageToImageRun(message, slackApp.client, os.environ.get("SLACK_BOT_TOKEN")),
                "threadId" : teamsMessageId
            },
            headers = {"Content-Type": "application/json"},
            timeout=60,
        )
    return {"ok" : True}


@flaskApp.route("/teams/", methods = ["POST"])
@msteams_verify.verify_hmac(os.environ.get("TEAMS_OUTGOING_TOKEN"))
def teamsMessage():
    data = request.data
    logging.info(data)
    return {'type' : 'message', 'text' : 'This is a reply'}

# # @scheduler.task('cron', day = "*", hour = 18) # Sheduled every day at 18:00
# @scheduler.task('cron', day = "*", hour = "*", minute = "*", second = "30") # Sheduled every minute
# def scheduledPosts():
#     if os.path.exists("threadsList.txt"):
#         with open("threadsList.txt", "r") as threadsList:
#             for threadTs in threadsList:
#                 teamsMessage = pymsteams.connectorcard(os.environ.get("TEAMS_HOOK"))
#                 teamsMessage.addLinkButton("Click here to view on slack", f"https://slack.com/app_redirect?channel={channelId}")
#                 teamsMessage.summary("Slack Ambassador Bot")
#                 for reply in slackApp.client.conversations_replies(channel = channelId, ts = threadTs)["messages"]:
#                     if reply["user"] == botId:
#                         continue
#                     teamsMessage.addSection(messageToSection(slackApp.client, reply, os.environ.get("SLACK_BOT_TOKEN")))
#                 teamsMessage.send()
#                 time.sleep(0.5) # Teams limited to 4 requests per second
#         os.remove("threadsList.txt")

# @flaskApp.route("/slack/", methods = ["POST"])
@slackEventAdapter.on("url_verification")
def challengeResponse():
    if request.json["type"] == "url_verification":
        return {"challenge" : request.json["challenge"]}

if __name__ == "__main__":
    # SocketModeHandler(slackApp, os.environ["SLACK_SOCKET_TOKEN"]).start()
    # SocketModeHandler(slackApp, os.environ["SLACK_SOCKET_TOKEN"]).connect()
    flaskApp.run(use_reloader=False, debug=True) # Reloader causes schedual to run events more than once