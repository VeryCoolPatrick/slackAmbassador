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

slackApp = slack_bolt.App(token = os.environ.get("SLACK_BOT_TOKEN"), signing_secret = os.environ.get("SLACK_SIGNING_SECRET"))
channelId = getSlackChannelId(slackApp.client, SLACK_CHANNEL)
botId = slackApp.client.auth_test()["user_id"]

# teamsMessage = {
#     "type": "AdaptiveCard",
#     "body": [
#         {
#             "type": "TextBlock",
#             "size": "Medium",
#             "weight": "Bolder",
#             "text": "Publish Adaptive Card Schema"
#         },
#         {
#             "type": "ColumnSet",
#             "columns": [
#                 {
#                     "type": "Column",
#                     "width": "auto",
#                     "items": [
#                         {
#                             "type": "Image",
#                             "style": "Person",
#                             "url": "https://pbs.twimg.com/profile_images/3647943215/d7f12830b3c17a5a9e4afcc370e3a37e_400x400.jpeg",
#                             "size": "Small"
#                         }
#                     ]
#                 },
#                 {
#                     "type": "Column",
#                     "items": [
#                         {
#                             "type": "TextBlock",
#                             "weight": "Bolder",
#                             "text": "Matt Hidinger",
#                             "wrap": True
#                         }
#                     ],
#                     "width": "stretch"
#                 }
#             ]
#         },
#         {
#             "type": "RichTextBlock",
#             "inlines": [
#                 {
#                     "type": "TextRun",
#                     "text": "New RichTextBlock"
#                 }
#             ]
#         }
#     ],
#     "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
#     "version": "1.4"
# }

# teamsMessage = {
#    "type":"message",
#    "attachments":[
#       {
#          "contentType":"application/vnd.microsoft.card.adaptive",
#          "content":{
#             "$schema":"http://adaptivecards.io/schemas/adaptive-card.json",
#             "type":"AdaptiveCard",
#             "version":"1.2",
#             "body":[
#                 {
#                 "type": "TextBlock",
#                 "text": "<at>Outgoing test webhook</at> For Samples and Templates, see [https://adaptivecards.io/samples](https://adaptivecards.io/samples)"
#                 }
#             ],
#             "msteams": {
#                 "entities": [
#                     {
#                         "type": "mention",
#                         "text": "<at>Outgoing test webhook</at>",
#                         "mentioned": {
#                           "id": "28:22e50a9b-80cc-4eab-a092-ce64796d28d7",
#                           "name": "Outgoing test webhook"
#                         }
#                       }
#                 ]
#             }
#          }
#       }
#    ]
# }

card = {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "Image",
                            "style": "person",
                            "url": "https://pbs.twimg.com/profile_images/3647943215/d7f12830b3c17a5a9e4afcc370e3a37e_400x400.jpeg",
                            "size": "small"
                        }
                    ],
                    "width": "auto"
                },
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "TextBlock",
                            "weight": "bolder",
                            "text": "Patrick",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "spacing": "None",
                            "text": "Posted from Slack",
                            "isSubtle": True,
                            "wrap": True
                        }
                    ],
                    "width": "stretch"
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "Hello Teams",
            "wrap": True
        }
    ],
    "actions": [
        {
            "type": "Action.OpenUrl",
            "title": "View on Slack",
            "url": "google.com"
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.0"
}

teamsMessage = {
   "user": "patrick",
   "profilePicture": "https://pbs.twimg.com/profile_images/3647943215/d7f12830b3c17a5a9e4afcc370e3a37e_400x400.jpeg",
   "card": card
}


# with open("threadsList.txt", "r") as threadsList:
#             for threadTs in threadsList:
#                teamsMessage = pymsteams.connectorcard(os.environ.get("TEAMS_HOOK"))
#                teamsMessage.addLinkButton("Click here to view on slack", f"https://slack.com/app_redirect?channel={channelId}")
#                teamsMessage.summary("Slack Ambassador Bot")
#                for reply in slackApp.client.conversations_replies(channel = channelId, ts = threadTs)["messages"]:
#                     if reply["user"] == botId:
#                         continue
#                     teamsMessage.addSection(messageToSection(slackApp.client, reply, os.environ.get("SLACK_BOT_TOKEN")))
#                print("\n\n----------\n\n",str(JSON).replace("\'", "\""), "\n\n----------\n\n")
#                response = requests.post(
#                   "https://prod-215.westeurope.logic.azure.com:443/workflows/ef2faf827e3b44b28917a23c50bee4be/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=0yNApd23MNwv179GRRpbH4PHGL6mggFi3qHBNA5a9sQ",
#                   json= JSON,
#                   headers={"Content-Type": "application/json"},
#                   timeout=60,
#                )
#                print(response)
#                time.sleep(0.5) # Teams limited to 4 requests per second


# response = requests.post(
#             "https://prod-215.westeurope.logic.azure.com:443/workflows/ef2faf827e3b44b28917a23c50bee4be/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=0yNApd23MNwv179GRRpbH4PHGL6mggFi3qHBNA5a9sQ",
#             # json= {"type": "object", "properties": teamsMessage},
#             json= teamsMessage,
#             headers={"Content-Type": "application/json"},
#             timeout=60,
#         )
# print(response)
# print(response.headers["messageId"])

# response = requests.post(
#             "https://prod-159.westeurope.logic.azure.com:443/workflows/ab5cda3903a441c6afaba039d0eaa0e1/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=YDfcuDU7h74P2gckhV4-t2df4e7VUwqVt9FwQeMquTw",
#             # json= {"type": "object", "properties": teamsMessage},
#             json= {"user" : "patrick", "message" : "hello teams"},
#             headers={"Content-Type": "application/json"},
#             timeout=60,
#         )
# print(response)
# print(response.headers["messageId"])

response = requests.post(
            os.environ.get("TEAMS_HOOK"),
            json = card,
            headers = {"type": "message"},
            timeout = 60,
        )
print(response)