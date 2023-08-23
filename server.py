from config import *
import os
from dotenv import load_dotenv
import logging
from slackFunctions import *
from flask import Flask, request
from flask_apscheduler import APScheduler
import slack_bolt
from slack_bolt.adapter.socket_mode import SocketModeHandler
import pymsteams
import msteams_verify

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

flaskApp = Flask("__name__")
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(flaskApp)
scheduler.start()

slackApp = slack_bolt.App(token = os.environ.get("SLACK_BOT_TOKEN"), signing_secret = os.environ.get("SLACK_SIGNING_SECRET"))
channelId = getSlackChannelId(slackApp.client, SLACK_CHANNEL)

# On command every message from the specified period of time (24h default) and its replies are posted to teams
@slackApp.command("/test")
def testCommand(body, ack):
    activeThreads = getActiveThreads(slackApp.client, channelId, OLDEST_THREAD_HOURS)
    ack() # Must acknowledge within 3? second of slash command
    for thread in reversed(activeThreads): # Reverse to send oldest message first
        teamsMessage = pymsteams.connectorcard(os.environ.get("TEAMS_HOOK"))
        teamsMessage.addLinkButton("Click here to view on slack", f"https://slack.com/app_redirect?channel={channelId}")
        teamsMessage.summary("Slack Ambassador Bot")
        for reply in thread:
            teamsMessage.addSection(messageToSection(slackApp.client, reply, os.environ.get("SLACK_BOT_TOKEN")))
        teamsMessage.send()
        time.sleep(0.5) # Teams limited to 4 requests per second

@slackApp.command("/teams")
def testCommand2(body, ack):
    ack() # Must acknowledge within 3? second of slash command
    print(body)
    # message = body["event"]
    # teamsMessage = pymsteams.connectorcard(os.environ.get("TEAMS_HOOK"))
    # teamsMessage.addLinkButton("Click here to view on slack", f"https://slack.com/app_redirect?channel={channelId}")
    # teamsMessage.summary("Slack Ambassador Bot")
    # teamsMessage.addSection(messageToSection(slackApp.client, message, os.environ.get("SLACK_BOT_TOKEN")))
    # teamsMessage.send()

# For every message on slack it is imediatly copied to teams
@slackApp.event("app_mention")
def messageEvent(body, say):
    message = body["event"]
    logging.info('======================')
    logging.info(message)
    logging.info('======================')
    say("Teams can see this thread, say hi!", thread_ts = message["ts"])
    teamsMessage = pymsteams.connectorcard(os.environ.get("TEAMS_HOOK"))
    # teamsMessage.addLinkButton("Click here to view on slack", f"https://slack.com/app_redirect?channel={channelId}")
    teamsMessage.summary("Slack Ambassador Bot")
    teamsMessage.addSection(messageToSection(slackApp.client, message, os.environ.get("SLACK_BOT_TOKEN")))
    teamsMessage.send()

@flaskApp.route("/", methods = ["POST"])
@msteams_verify.verify_hmac(os.environ.get("TEAMS_OUTGOING_TOKEN"))
def teamsMessage():
    data = request.data
    logging.info(data)
    return {'type' : 'message', 'text' : 'This is a reply'}

@scheduler.task('cron', day = "*", hour = 18)
def scheduleTest():
    logging.info("scheduled log")

if __name__ == "__main__":
    SocketModeHandler(slackApp, os.environ["SLACK_SOCKET_TOKEN"]).connect()
    flaskApp.run(debug = True)