# Archived legacy Messenger adapter.
# Preserved verbatim from the active repository before replacement.

import requests
import os
from flask import Flask, request
from tools.search_directory import search_office
from tools.rate_office import save_rating
from tools.generate_pdf import generate_complaint_pdf

app = Flask(__name__)
TOKEN = os.getenv("MESSENGER_TOKEN")
PHONE_ID = os.getenv("MESSENGER_PHONE_ID")

# reuse HTTP connections
_messenger_session = requests.Session()
_adapter = requests.adapters.HTTPAdapter(pool_maxsize=10)
_messenger_session.mount("https://", _adapter)

def send_messenger(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {"messaging_product": "messenger", "to": to, "text": {"body": text}}
    try:
        resp = _messenger_session.post(url, headers=headers, json=data, timeout=(2, 5))
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("send_messenger failed:", e)
        return False
    return True

@app.route("/webhook", methods=["GET","POST"])
def webhook():
    if request.method == "GET":
        return request.args.get("hub.challenge")
    data = request.get_json()
    msg = data['entry'][0]['changes'][0]['value']['messages'][0]
    phone = msg['from']
    text = msg['text']['body']

    if "search" in text.lower():
        reply = search_office("ration", "Kochi")
    else:
        reply = "Send: search ration Kochi"

    send_whatsapp(phone, reply)
    return "ok"

if __name__ == "__main__":
    app.run(port=5000)
