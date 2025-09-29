from flask import Flask, request
import requests

app = Flask(__name__)

# Jenkins details
JENKINS_URL = "https://0640f2ef4501.ngrok-free.app"   # ngrok URL for Jenkins (port 8080)
JOB_NAME = "voting-app-pipeline"                      # Jenkins job name
USERNAME = "Ans Faraz"                                # your Jenkins username
API_TOKEN = "111fc77cf1e14c6109c62442667f178d64"      # Jenkins API token

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.form.get('Body', '').strip().lower()

    if "yes" in incoming_msg:
        requests.post(
            f"{JENKINS_URL}/job/{JOB_NAME}/input/Proceed/proceedEmpty",
            auth=(USERNAME, API_TOKEN)
        )
        return "Approved ✅", 200

    elif "no" in incoming_msg:
        requests.post(
            f"{JENKINS_URL}/job/{JOB_NAME}/input/Proceed/abort",
            auth=(USERNAME, API_TOKEN)
        )
        return "Rejected ❌", 200

    return "Reply YES or NO", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
