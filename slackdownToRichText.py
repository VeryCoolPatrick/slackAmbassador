#############################################################################################
# This script converts slacks proprietary markdown into text runs for a rich text block in
# a microsoft adaptive card.
#############################################################################################

import slackdown
import emoji_data_python
import re
import slackFunctions as sf

def format(message: str, slackClient):
    message = sf.mentionToName(message = message, slackClient = slackClient) # Mentions and emoticons must be converted before HTML
    message = emoji_data_python.replace_colons(message)
    message = slackdown.render(message) # Convert to HTML first as it is easier to parse than markdown.

    tagRegex = r"<(.+)>"

    match 45:
        case 45:
            print("fourty five")
        case 21:
            print("twenty one")


    # i = 3 # Skip the first <p>
    # while i != -1:
    #     nextTag = re.search(tagRegex, 3)

    return message



import os
import slack_bolt
from dotenv import load_dotenv
load_dotenv()

slackApp = slack_bolt.App(token = os.environ.get("SLACK_BOT_TOKEN"), signing_secret = os.environ.get("SLACK_SIGNING_SECRET"))

sampleText = """<https://slack-ambassador.glitch.me/teams>

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
:eyes::smiling_face_with_3_hearts::face_with_diagonal_mouth:"""

print(sampleText)
print("===================")
print(format(sampleText, slackApp.client))