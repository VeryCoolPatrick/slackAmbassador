import time
import datetime
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import pymsteams
import slackdown
import emoji_data_python
import requests
import base64

def getSlackChannelId(slackClient: WebClient, channelName: str):
    try:
        for conversation in slackClient.conversations_list():
            for channel in conversation["channels"]:
                if channel["name"] == channelName:
                    return channel["id"]
        raise SlackApiError("Channel not found!")
    except SlackApiError as e:
        logging.exception(e)

# Returns a list of slack messages from newest to oldest. Does not include replies.
def getActiveThreads(slackClient: WebClient, channelId: str, oldestInhours: int = 24):
    try:
        minTime = datetime.datetime.now() 
        minTime -= datetime.timedelta(hours = oldestInhours)
        minTime = time.mktime(minTime.timetuple()) # Time must be given as unix timestamp
        activeThreadTs = []
        for message in slackClient.conversations_history(channel = channelId, oldest = minTime)["messages"]:
            if "thread_ts" in message:
                activeThreadTs.append(message["thread_ts"])
        threadList = []
        for ts in activeThreadTs:
            threadList.append(slackClient.conversations_replies(channel = channelId, ts = ts)["messages"])
        return threadList
    except SlackApiError as e:
        logging.exception(e)

# Return the username displayed on slack profile
def getUsername(user):
    if user["profile"]["display_name"]:
        return user["profile"]["display_name"]
    return user["name"]

# Encodes the image in base 64 and returns image tags in link tags
def imageToHtml(image, botToken: str):
    response = requests.get(image["thumb_80"], headers = {"Authorization" : f"Bearer {botToken}"})
    if response.status_code != 200 or "image" not in response.headers.get("content-type"):
        logging.error("image error")
        return None
    encodedImage = base64.b64encode(response.content)
    return f'<a href = "{image["url_private"]}"><img src="data:{response.headers.get("content-type")};base64, {encodedImage.decode()}" alt="{image["name"]}" /><a/>'

# Converts a slack message to connector card section. Includes formating and user details.
def messageToSection(slackClient, message, botToken: str):
    messageSection = pymsteams.cardsection()
    user = slackClient.users_info(user = message["user"])["user"]
    messageSection.activityTitle(getUsername(user))
    messageSection.activityImage(user["profile"]["image_192"])
    sectionText = emoji_data_python.replace_colons(message['text']) # Emoticons must be converted before HTML
    sectionText = slackdown.render(sectionText) # Convert markdown to HTML
    if "files" in message:
            for file in message["files"]:
                if "image" in file["mimetype"]:
                    sectionText += imageToHtml(file, botToken) # Image added as HTML to text section as image section is broken in teams
    messageSection.text(sectionText)
    return messageSection