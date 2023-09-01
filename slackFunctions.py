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
import re
import os

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

# Converts slack mentions using user ID to bold HTML display name
def mentionToName(message: str, slackClient):
    mentionPatern = r"<@(\w+)>"
    mentionMatches = re.findall(mentionPatern, message)
    for mention in mentionMatches:
        userResponse = slackClient.users_info(user = mention)
        if userResponse["ok"] == False or userResponse["user"]["is_bot"]:
            replacementText = ""
        else:
            replacementText = f'*{getUsername(userResponse["user"])}*'
        message = message.replace(f"<@{mention}>", replacementText)
    return message

# Encodes the image in base 64 and returns image tags in link tags
def imageToHtml(image, slackClient, botToken: str):
    response = requests.get(image["thumb_80"], headers = {"Authorization" : f"Bearer {botToken}"})
    if response.status_code != 200 or "image" not in response.headers.get("content-type"):
        logging.error("image error")
        return None
    encodedImage = base64.b64encode(response.content)
    return f'<a href = "{image["url_private"]}"><img src="data:{response.headers.get("content-type")};base64, {encodedImage.decode()}" alt="{image["name"]}" /><a/>'

    # response = slackClient.files_sharedPublicURL(token = os.environ.get("SLACK_USER_TOKEN"), file  = image["id"]) # Setting image public does not work on free trial
    # return f'<img src="{response["file"]["permalink_public"]}" alt="{response["file"]["name"]}">'
    
# Encodes the image in base 64 and returns the url
def imageToUrl(image, slackClient, botToken: str):
    response = requests.get(image["thumb_80"], headers = {"Authorization" : f"Bearer {botToken}"})
    if response.status_code != 200 or "image" not in response.headers.get("content-type"):
        logging.error("image error")
        return None
    encodedImage = base64.b64encode(response.content)
    return f'data:{response.headers.get("content-type")};base64,{encodedImage.decode()}'

# Retuns a fully formated message including avatar and images
def slackMessageToHtml(message, slackClient, slackBotToken):
    user = slackClient.users_info(user = message["user"])["user"]
    avatar = f'<img src = "{user["profile"]["image_48"]}" style = "border-radius: 50%" alt = "User Avatar">'
    text = f"<p><strong>{getUsername(user)}</strong></p>"
    text += slackTextToHtml(message, slackClient, slackBotToken)
    return text

# Convert iamges in 
def slackMessageToImageRun(message, slackClient, slackBotToken):
    images = ""
    if "files" in message:
            for file in message["files"]:
                if "image" in file["mimetype"]:
                    if images:
                        images += ", "
                    images += f"""{{
                        "type": "Image",
                        "url": "{imageToUrl(file, slackClient, slackBotToken)}",
                        "altText": "{file["name"]}",
                        "selectAction": {{
                            "type": "Action.OpenUrl",
                            "url": "{file["url_private"]}"
                        }}
                        }}"""
    return images

# Convert slack formating to HTML
def slackTextToHtml(message, slackClient, slackBotToken):
    text = message['text']
    text = mentionToName(message = text, slackClient = slackClient) # Mentions and emoticons must be converted before HTML
    text = emoji_data_python.replace_colons(text)
    text = slackdown.render(text) # Convert markdown to HTML
    if "files" in message:
            for file in message["files"]:
                if "image" in file["mimetype"]:
                    text += imageToHtml(file, slackClient, slackBotToken)
    return text

# Converts a slack message to connector card section. Includes formating and user details.
def messageToSection(message, slackClient, slackBotToken: str):
    messageSection = pymsteams.cardsection()
    user = slackClient.users_info(user = message["user"])["user"]
    messageSection.activityTitle(getUsername(user))
    messageSection.activityImage(user["profile"]["image_192"])
    sectionText = slackTextToHtml(message, slackClient, slackBotToken)
    messageSection.text(sectionText)
    return messageSection