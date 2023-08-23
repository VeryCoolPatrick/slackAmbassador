import logging
import pymsteams
import requests
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

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

teamsMessage = {
   "type":"message",
   "attachments":[
      {
         "contentType":"application/vnd.microsoft.card.adaptive",
         "content":{
            "$schema":"http://adaptivecards.io/schemas/adaptive-card.json",
            "type":"AdaptiveCard",
            "version":"1.2",
            "body":[
                {
                "type": "TextBlock",
                "text": "<at>Outgoing test webhook</at> For Samples and Templates, see [https://adaptivecards.io/samples](https://adaptivecards.io/samples)"
                }
            ],
            "msteams": {
                "entities": [
                    {
                        "type": "mention",
                        "text": "<at>Outgoing test webhook</at>",
                        "mentioned": {
                          "id": "28:22e50a9b-80cc-4eab-a092-ce64796d28d7",
                          "name": "Outgoing test webhook"
                        }
                      }
                ]
            }
         }
      }
   ]
}

response = requests.post(
            os.environ.get("TEAMS_HOOK"),
            json=teamsMessage,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
print(response)