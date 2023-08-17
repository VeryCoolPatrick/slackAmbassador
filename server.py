import os
from slackFunctions import *
from config import *
from dotenv import load_dotenv
import slack_bolt
from slack_bolt.adapter.socket_mode import SocketModeHandler
import pymsteams

load_dotenv()

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

# For every message on slack it is imediatly copied to teams
@slackApp.event("message")
def messageEvent(body, logger):
    message = body["event"]
    teamsMessage = pymsteams.connectorcard(os.environ.get("TEAMS_HOOK"))
    teamsMessage.addLinkButton("Click here to view on slack", f"https://slack.com/app_redirect?channel={channelId}")
    teamsMessage.summary("Slack Ambassador Bot")
    teamsMessage.addSection(messageToSection(slackApp.client, message, os.environ.get("SLACK_BOT_TOKEN")))
    teamsMessage.send()

if __name__ == "__main__":
    SocketModeHandler(slackApp, os.environ["SLACK_SOCKET_TOKEN"]).start()