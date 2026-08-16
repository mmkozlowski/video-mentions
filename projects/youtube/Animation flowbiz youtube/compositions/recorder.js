/* flowbiz inline recorder — getDisplayMedia → MediaRecorder
   Usage:
     await window.flowbizRecorder.record({
       timeline: gsapTimelineInstance,
       duration: 5.0,           // seconds of animation
       tail: 0.5,               // extra hold seconds at end
       fileName: 'scene-01.webm'
     });
*/
(function(){
  function fmt(n){ return String(n).padStart(2,'0'); }
  function ts(){
    const d=new Date();
    return d.getFullYear()+fmt(d.getMonth()+1)+fmt(d.getDate())+'-'+fmt(d.getHours())+fmt(d.getMinutes())+fmt(d.getSeconds());
  }

  async function record(opts){
    const {timeline, duration=5.0, tail=0.4, fileName='scene.webm'} = opts || {};
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      alert('Twoja przeglądarka nie wspiera nagrywania ekranu (getDisplayMedia). Użyj Chrome/Edge.');
      return;
    }

    // Force 1:1 native mode if function is exposed
    if (typeof window.toggleNative === 'function' && !document.body.classList.contains('native')) {
      document.body.classList.add('native');
      if (typeof window.fit === 'function') window.fit();
      // also direct the layout function used by scenes via the inline fit() closure
      window.dispatchEvent(new Event('resize'));
    }
    document.body.classList.add('export');

    // Ask the browser for a capture stream at native 1920×1080@60
    let stream;
    try {
      const constraints = {
        video: {
          width:  { ideal: 1920, max: 1920 },
          height: { ideal: 1080, max: 1080 },
          frameRate: { ideal: 60, max: 60 },
          displaySurface: 'browser'
        },
        audio: false,
        // Hint Chrome to default to the current tab
        preferCurrentTab: true,
        selfBrowserSurface: 'include',
        surfaceSwitching: 'exclude',
        systemAudio: 'exclude'
      };
      stream = await navigator.mediaDevices.getDisplayMedia(constraints);
    } catch(e){
      document.body.classList.remove('export');
      console.error(e);
      alert('Nie wybrałeś źródła do nagrania (anulowane).');
      return;
    }

    // Pick the best webm codec available
    const candidates = [
      'video/webm;codecs=vp9,opus',
      'video/webm;codecs=vp9',
      'video/webm;codecs=vp8',
      'video/webm'
    ];
    const mimeType = candidates.find(t => MediaRecorder.isTypeSupported(t)) || 'video/webm';

    const chunks = [];
    const rec = new MediaRecorder(stream, {
      mimeType,
      videoBitsPerSecond: 25_000_000  // 25 Mbps — robust quality at 1080p60
    });
    rec.ondataavailable = e => { if (e.data && e.data.size) chunks.push(e.data); };

    const stoppedP = new Promise(res => rec.onstop = res);
    rec.start(250);

    // Tiny pre-roll so first frames aren't black, then play the timeline from 0
    await new Promise(r => setTimeout(r, 250));
    try {
      if (timeline && typeof timeline.restart === 'function') {
        timeline.restart(true);
      } else if (timeline && typeof timeline.play === 'function') {
        timeline.play(0);
      }
    } catch(e){ console.warn(e); }

    // Stop after duration + tail
    const totalMs = Math.round((duration + tail) * 1000);
    await new Promise(r => setTimeout(r, totalMs));

    try { rec.stop(); } catch(e){}
    stream.getTracks().forEach(t => t.stop());
    await stoppedP;

    const blob = new Blob(chunks, { type: mimeType });
    const url  = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName.replace(/\.webm$/i,'') + '-' + ts() + '.webm';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(url), 2000);

    document.body.classList.remove('export');
    return blob;
  }

  window.flowbizRecorder = { record };
})();
