# src/bot_whatsapp.py
import requests
import os
from flask import Flask, request
from tools.search_directory import search_office
from tools.rate_office import save_rating
from tools.generate_pdf import generate_complaint_pdf

app = Flask(__name__)
TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")

def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {"messaging_product": "whatsapp", "to": to, "text": {"body": text}}
    requests.post(url, headers=headers, json=data)

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
