########################################################################################################
# This script converts slacks proprietary markdown into text runs for a rich text block in
# a microsoft adaptive card. The JSON is returned as a string so it can be easily sent and
# added with a power aitomate flow. This code is partialy fictional but probably not worth using.
# Adaptive cards are just not good at holding a convered message and so plain HTML is preferable.
########################################################################################################

import slackdown
import emoji_data_python
import re
import slackFunctions as sf
from copy import copy
import json

slackdown.LIST_DELIMITERS.clear() # Stops lists being converted

def format(message: str, slackClient):
    message = sf.mentionToName(message = message, slackClient = slackClient) # Mentions and emoticons must be converted before HTML
    message = emoji_data_python.replace_colons(message)
    message = slackdown.render(message) # Convert to HTML first as it is easier to parse than markdown.
    tagRegex = r"<(.+?)>"
    block = []
    runText = ""
    currentRun = {
        "type" : "TextRun",
        "text" : ""
    }
    message = message[3:]
    while message:
        nextTag = re.search(tagRegex, message)
        currentRun["text"] += message[:nextTag.start()]
        if nextTag.group()  == "<br />":
            currentRun["text"] += "\n"
            message = message[nextTag.end():]
            continue
        block.append(copy(currentRun))
        match nextTag.group(): # Yes pyhon has switch statements with V3.10, I'm shocked too
            case "<p>": # Newlines # <p> should not be reachable as is skipped over
                message = message[nextTag.end():]
                continue
            case "</p>":
                if block:
                    block[-1]["text"] += " \n"
                else:
                    block.append({
                        "type" : "TextRun",
                        "text" : "\n"
                    })
                currentRun = {
                    "type" : "TextRun",
                    "text" : ""
                }
                # i = nextTag.end() + 3 # The 3 is to skip over the next <p> tag
                message = message[nextTag.end() + 3:]
                continue
            case "<b>": # Bold
                currentRun["weight"] = "bolder"
            case "</b>":
                del currentRun["weight"]
            case "<i>": # Italic
                currentRun["italic"] = True
            case "</i>":
                del currentRun["italic"]
            case "<s>": # Strike through
                currentRun["strikethrough"] = True
            case "</s>":
                del currentRun["strikethrough"]
            case "<blockquote>":
                pass
            case "</blockquote>":
                pass
            case _: # Should not be reachable as all '>' are sent by slack as unicode
                currentRun["text"] += message[nextTag.start():nextTag.end()]
                message = message[nextTag.end():]
                continue

        currentRun["text"] = ""
        message = message[nextTag.end():]
    return json.dumps(block)



import os
import slack_bolt
from dotenv import load_dotenv
load_dotenv()

slackApp = slack_bolt.App(token = os.environ.get("SLACK_BOT_TOKEN"), signing_secret = os.environ.get("SLACK_SIGNING_SECRET"))

sampleText = """a*nnoying _overl*apping fo_rmatti~ng annoy_ing overlapp_ing forma~tting

<https://slack-ambassador.glitch.me/teams>

*bold* _italic_ ~slash~

`code`

<https://slack-ambassador.glitch.me/teams|formatted link>

```code
block```
1. list
2. list
3. list
• bullet
• bullet
• bullet
<@U05LD4RV98X>
<@U05N29QP3JS>
:eyes::smiling_face_with_3_hearts::face_with_diagonal_mouth:

&gt; indented
&gt; text """

print(sampleText)
print("===================")
print(format(sampleText, slackApp.client))
