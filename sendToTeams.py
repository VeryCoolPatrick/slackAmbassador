from config import *
import os
from dotenv import load_dotenv
import logging
from slackFunctions import *
from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
import slack_bolt
from slack_bolt.adapter.socket_mode import SocketModeHandler
import pymsteams
import msteams_verify

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

# slackApp = slack_bolt.App(token = os.environ.get("SLACK_BOT_TOKEN"), signing_secret = os.environ.get("SLACK_SIGNING_SECRET"))
# channelId = getSlackChannelId(slackApp.client, SLACK_CHANNEL)
# botId = slackApp.client.auth_test()["user_id"]

# response = requests.post(
#             os.environ.get("TEAMS_FLOW_URL"),
#             json=  {"threadId" : "", "message" : '<p> 👀🥰🫤</p><p><b>bold</b> <i>italic</i> <s>strike</s></p><p><a href="https://slack-ambassador.glitch.me/teams" target="blank">https://slack-ambassador.glitch.me/teams</a></p><a href = "https://files.slack.com/files-pri/T05LLV3KN0N-F05MU2YM7HC/1280px-sunflower_from_silesia2.jpg"><img src="data:image/jpeg;base64, /9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCABQAFADASIAAhEBAxEB/8QAHAAAAQQDAQAAAAAAAAAAAAAABgIEBQcAAQMI/8QAMhAAAgECBQMDAgQGAwAAAAAAAQIDBBEABRIhMQYTQSJRYTJxFEKBoRUjUmKRsQczov/EABsBAAICAwEAAAAAAAAAAAAAAAQGBQcAAgMB/8QAMREAAQMDAgQDBwQDAAAAAAAAAQIDEQAEIQUSMUFRgQZhcRMUMpGh0fAVIrHBQoLh/9oADAMBAAIRAxEAPwAYvhN8avtjr2HWeGKovT93SQ8qkDS3DfK/Iw7qWE8aXACa5X5wknBh0blvbzavo8ypx3k0AxtuCvqvv5BHnDfO+kJcvzKtghm1QDQaPX9U2sEhb+4sQT5NvfC6PFNim8ctHVBO0JIVOFBQHD03DtngDR/6a8WkuJEzOOYift/VC18JviRly/s5GtZNdZZHOlTsVQNp3Hyb/wCBh3D0/UnLYjJGqVtWyvTxubNo4F/YsTsPi+2DXNcsmkla1gAL2f7CJ7CcnlB8p5JsnlEJAyRu7f8AagicJJwuaOSGWSKZGjlRirowsVI5BxxJF7XF8SqVBQkULEVhwg4UcIONqypeKgrZaN6uKjqJKVCQ0yRkqCObn4wUUOXSVnRbQSE1tM0MlRSWQiWjmClmTzeNwORtfxviyMi6VyvJy8+WNUwiRQJF/FGaJiOCb+R4IsbHAzW01HldbOMol7cVXeTTGQFjlFwwUHgEHjj1bYqHUPHSb9RRbCNigpJIjhxBgkgjjKTCkyCIJBZrTSNuV8xB/PvwNNIJZ6SmymqdVZ+0tyT9S6VIB88Hn59xh91HB/F8soqukY64ASAfI43+QwH+TjOoq+MU8pdhLTzIjpIBurgAgH2uCd/n4OIHJsyaSnkSncNH3CA7EBRcWIJPn4+MJe1byvbpTBn6HlTGlsBAk0ulkXOMwR5NPYVf5gcatSFbEEHn2+++H9ZmEL5yplTW8h0odVu2PpU/7wHSV9Pksj66wSFyCUgRmCBiWW59jY2+4wwhz2meqlq2qGWOIX9aEaSOAxF7bEn2xInTnV5AO0DHetZbnjmpjP8AI45M0p2p63vvOz/iRo0lAgF5B/aRsL73tzfEZ1DVU2qOgy+CKKnp9pGVBqeTzdrXNuOeb4OYfwtLFT1AmgqFZhPNJGb90qLrGP7Q1tvNhfEdmnQtBDRuKKuqnr2KlTUFFiBJ3FgCTyfm/F8NOieJGUraRqSyA2AlOMEkkblRj9qYAnlJ41B32mrCVG3T8Zk+nQepyflVeHCTgxboSqWplibMqQLEt5HZGQR+Tq1W0gDknArXQwwVUkdNVJVxLsJkRlVvewbe3z5xYdjrFnqCim1XujJgKgdyAJ8pml560dYALgifMUa9LZFWJWsIc+paOSIhmjiWSoVrf1abLb9dsWBWSOi/g88igngcAxVDKVV/cEkXVvZvtf3FQ1fUma1SqaysE+gbGSGMn9SFBP64Iem886uirlpaejpq2KFNRppKdEVVNjq7oItyPfnjFceIvDupPq95unWpAPMI+pSmeXxExPGp6wvmEjY2lR+v3/iuXVOS1cVfThKiRstGpTIGKyIo9Qjb2N+DxvzuMMJKykhiiheMR0liqRqguzAflUn1G97m+LCrKOHqzK5aebL4aLMguoCkqRK6W2B06Rcb7gb284pLqGLNunsyaPOqFFmfeOZNRSU8XBPgD8pAO/64g9LcDyfZLwpPpnzBBIPaph2VZFSOY0UVXLFI9JFVVRurComtIo2JBKkfT6bbkAbX3w1qYMsEQjrsqEI1Ad5ks/Bvd0Aa3F/n4vgclzp9LkRQh9OgMI77X4I3uBckePNr3win6gqYVHa0M4+qVbo0g+FDW23vf354GJ9LSowaFKiDkUU5DVQ0ddFJQ1HehDXeIzFg4BI31WUMCbj3v8HFq5fURs4loZzCVUmWomfVKWPIUDcc+Nzcb+MUvl/UdQJWm70La7GSOSIMXOkgnkAg2A3APODjpvqKN1McLJGioLdiMtJcDlEJBNrHcG4Hg4idVsy6nfGR+dKJYe/xotzijoKvJzRVytSwdzWGeoZZpG+YEv541kWJud8cKHpTp2so5memliS+kTLI2pW9rlrX/t3OItKtWIhoTOxI3IVac/Isbt/rCkn6op8wjXKsorJgQNMrBron9KyEAR/fzgOwVfke72twWwJV8ewefEj88pry7bYQC44ie0n+6AsSuVZ09C6ncMgsDpDBh7EHETjEQtIGvZACDfzi1/FNs09YErEqBG3rJMEDrInHflSro7ikXAA4GZ/PWrMyjOqPNO0Muy6qOZupk7N+3TRBQSW+oseOBYEm18azaroMxoIoupIKXNoIm7qCoTS632srKQQPgk/tgWyjO6XLstzMMZXrKiMQRiMWXSfqLN7fA5JF9gbtck6orcmz3+JoomiKCKekaxSeK9yu/B9j4I9rjFcW3hW/uCpxCCgJyCqQSegnOeExHU0yvatbMjaTuPln8/mhLqHpKoC1GZUUaUOXvMkdHSyOzuy29T3P5VsLk8s1hwbM6zoXP6OKeaqggWOOmgq7iXeSOWQxqQLeGG6m1h+/pvpTq3pnP84SjpKR4qx4CyPPEoLi4ujcjXtfzsOfGH2d9qkzefP4Y5ql6EikqkSxAh062sPJDMrH7eN8APa1e2Tgt7hnaqOfE5gfPrWyC29lBxXmDMOheqMryuPManLEekkVT3IZ1kK6/p1DYre+1x8XvbB1/wAd9Lvl8sWa5jW07DQrQiOJpVQMLESRtY7G/HBxavUnVeR1AioKhFqaadozLrOkBNY2a/i/j3tziYzzJmQy12XR08zIt56SU2SZQLelvyNpGx44vxfAFxrlw60G3Ubd8ifljM12b2oP7qhJ8zoDlxeqpErIEHrky9zrQe+i6uB9r4gKSryaSpaTpjquupZ3YdylrZnmRx7FZgx/UEY7VfUmVfwqWfp2s/CzOlgslOxkQ82YMCP/AEQcV7ntRR5hSy1NUkdHnMUiBkgW0dQjX/mxjwQR6l+bg8jEh4f0xd0VNFSkg4j4u6m1AhQnEpMjjFC3zqWxv2/PHaeR+hqExrxbxjMaxfBSCQqMikgEgRWY1jMZbHsVlP8AJPTXNU9ztGkgmqA+rTZljbTY+9yLYlqHr6vqOgKHLOwkckzO9ZP3NTVFn5t+XVbcfHzgTzsvH05JDF/35lUJSxj3VbM37lP8HHVwkKpDEBoiQRIB7KLYXLrTLXVb4+8ICg2B8zPTpPDrUg1cOW7I2GCTUlW1ArIqt99Pb9IPOxvvh7QdcZ/RZeKEVgnpVXQqzLd1TygceoD73tiEiqwlHPAUH8whtXkWBFvtv+2GuOen6Aw227a3LYWgLlMgHBA4dDiDEV1u79TikOtqhUQY6gmiDOaynMsFVlrFFnTuBWtdWBs8bAePnjyOdomrqvxKqWTS6+QdrYaj4xscYOs9CtbTYpIlSJg8wDOPMR18zia4Pag88CFHB4iv/9k=" alt="1280px-Sunflower_from_Silesia2.jpg" /><a/>'},
#             headers = {"Content-Type": "application/json"},
#             timeout=60,
#         )
# print(response)
# print(response.headers["messageId"])

response = requests.post(
            os.environ.get("TEAMS_FLOW_URL2"),
            json = {"message" : "Hello, Teams!"},
            headers = {"Content-Type": "application/json"},
            timeout=60,
        )
print(response)