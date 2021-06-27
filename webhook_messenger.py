import requests
import rsa
import base64
import sys
import os

url = os.environ.get("webhook_url")
Event_Name = os.environ.get("GITHUB_EVENT_NAME")
Job_ID = os.environ.get("GITHUB_JOB")
Action_ID = os.environ.get("GITHUB_ACTION")
Run_ID = os.environ.get("GITHUB_RUN_ID")
Run_Number = os.environ.get("GITHUB_RUN_NUMBER")

if len(sys.argv) > 1:
    if sys.argv[1] == "stop":
        content = "stop"
        embed = [
            {
                "title": "Stop",
                "description": "GitHub Actions requests the bot to stop now."
                + f"\nEvent_Name: {Event_Name}"
                + f"\nJob_ID: {Job_ID}"
                + f"\nAction_ID: {Action_ID}"
                + f"\nRun_ID: {Run_ID}"
                + f"\nRun_Number: {Run_Number}",
                "footer": {
                    "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Gnome-application-certificate.svg/20px-Gnome-application-certificate.svg.png"
                },
            }
        ]

data = {
    "username": "GitHub Actions",
    "avatar_url": "https://github.githubassets.com/images/modules/logos_page/Octocat.png",
    "content": content,
    "embeds": embed,
}

result = requests.post(url, json=data)

try:
    result.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err)
    raise err
else:
    print(
        "Payload delivered successfully, code {}.".format(result.status_code)
    )
