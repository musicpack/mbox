import requests
import rsa
import base64
import sys
import os
from src.auth import Crypto

embed = []
TOKEN = os.environ.get('DiscordToken_mbox')
# url = os.environ.get('webhook_url')
url = 'https://discord.com/api/webhooks/842600473789333504/itmdWwe0IJBJHtJqGy0d3ePNVpE4BDdKYvJv6HvRQS7sq_CePk6v8Bf7uc_PPA1Fa9ao'
pubkey = rsa.PublicKey.load_pkcs1(base64.b64decode('LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1JR0pBb0dCQUpMclBGMEF0MHJKQ0p1b09GMkhDeW9rbUpqRUF4ZSsyN1kyZFFiNnVNNHdHblhURkpUREZvM20KUklTUXpFU3I2aUtFMzVBQlJ2SHR2QVBkeTBXQnRhaDQ5ZDZ3WTRiZVdDeUw4WmI0bGNxQnpyR2wxb0ZXVkZqcwo2VDZTMXVubWpSNG5wK0R3UnlxeHlaUDZ3VTcxOVhTc0h2WmZiTC9QNmNRVVY5bzFrK3VWQWdNQkFBRT0KLS0tLS1FTkQgUlNBIFBVQkxJQyBLRVktLS0tLQo='))
Event_Name = os.environ.get('GITHUB_EVENT_NAME')
Job_ID = os.environ.get('GITHUB_JOB')
Action_ID = os.environ.get('GITHUB_ACTION')
Run_ID = os.environ.get('GITHUB_RUN_ID')
Run_Number = os.environ.get('GITHUB_RUN_NUMBER')

if len(sys.argv) > 1:
    if sys.argv[1] == 'stop-warn':
        embed = [
            {
                "title" : "Stop Warning",
                "description" : "GitHub Actions is going to request the bot to stop soon."
                + f"\nEvent_Name: {Event_Name}"
                + f"\nJob_ID: {Job_ID}"
                + f"\nAction_ID: {Action_ID}"
                + f"\nRun_ID: {Run_ID}"
                + f"\nRun_Number: {Run_Number}",
                "footer": {
                    "text": Crypto(pubkey=pubkey).encrypt_token_time(TOKEN),
                    "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Gnome-application-certificate.svg/20px-Gnome-application-certificate.svg.png"
                }
            }
        ]
    elif sys.argv[1] == 'stop':
        embed = [
            {
                "title" : "Stop Order",
                "description" : "GitHub Actions requests the bot to stop now."
                + f"\nEvent_Name: {Event_Name}"
                + f"\nJob_ID: {Job_ID}"
                + f"\nAction_ID: {Action_ID}"
                + f"\nRun_ID: {Run_ID}"
                + f"\nRun_Number: {Run_Number}",
                "footer": {
                    "text": Crypto(pubkey=pubkey).encrypt_token_time(TOKEN),
                    "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Gnome-application-certificate.svg/20px-Gnome-application-certificate.svg.png"
                }
            }
        ]

data = {
    "username" : "GitHub Actions",
    "avatar_url": "https://github.githubassets.com/images/modules/logos_page/Octocat.png"
}

data["embeds"] = embed

result = requests.post(url, json = data)

try:
    result.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err)
    raise err
else:
    print("Payload delivered successfully, code {}.".format(result.status_code))