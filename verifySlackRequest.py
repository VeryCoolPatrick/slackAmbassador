########################################################################################################
# Verifies a slack request by hashing the signing secret with the request body and compares the result
# to the given hash. Should not be needed if using the slack api event addapter.
########################################################################################################

import hashlib
import hmac
import base64git
import logging
import json
import time


def authenticate_message(request, slackSigningSecret) -> bool:
    signature = request.headers.get('signature')
    timestamp = request.headers.get('timestamp')

    if not signature or not timestamp:
        print("SIG/TS NOT FOUND")
        return False

    if abs(time.time() - int(timestamp)) > 60 * 5:
        print("TS OLD")
        return False

    baseString = f"v0:{timestamp}:{request.data.decode('utf-8')}"
    mySignature = 'v0=' + hmac.new(
        bytes(slackSigningSecret, "utf-8"),
        bytes(baseString, "utf-8"),
        hashlib.sha256).hexdigest()
    print("COMPARED")
    return hmac.compare_digest(mySignature, signature)