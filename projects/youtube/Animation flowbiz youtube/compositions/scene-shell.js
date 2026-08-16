/* Shared scene shell — chrome + fit + native mode + recorder integration.
 *
 * Każda scena woła na końcu:
 *   flowbizScene.init({
 *     id: 'scene-01',            // matches window.__timelines[id]
 *     duration: 2.5,             // seconds of animation
 *     tail: 0.4,                 // hold after duration (default 0.4)
 *     label: 'Hook · 5.0s',      // shown in corner brand
 *     timeline: tl,              // GSAP timeline (paused:true)
 *   });
 *
 * Wymagane przed init():
 *   - DOM: <div class="wrap" id="wrap"><div class="stage" id="stage">…</div></div>
 *   - GSAP załadowany
 *   - recorder.js załadowany (opcjonalnie — jeśli chcesz nagrywać przez przycisk)
 */
(function(global){
  function buildControls(label){
    const brand = document.createElement('div');
    brand.className = 'corner-brand';
    brand.innerHTML = `<b>Build with Matt</b> · ${label}`;
    document.body.appendChild(brand);

    const c = document.createElement('div');
    c.className = 'controls';
    c.innerHTML = `
      <button id="__play" class="primary" title="Odtwórz (spacja)">▶ Odtwórz</button>
      <button id="__restart" title="Restart">↻ Restart</button>
      <span class="t"><b id="__tnow">0.00</b> / <span id="__tend">0.00</span>s</span>
      <button id="__rec" title="Nagraj (WebM)" style="color:#FF6E4F">● Nagraj</button>
      <button id="__full" title="Pełny ekran do nagrywania">⛶ Full</button>
      <button id="__native" title="Tryb 1:1 (1920×1080)">1:1</button>
    `;
    document.body.appendChild(c);
  }

  function init(opts){
    const { id, duration, tail = 0.4, label = id, timeline } = opts;

    // Watermark (if missing).
    if (!document.querySelector('.watermark')) {
      const wm = document.createElement('div');
      wm.className = 'watermark';
      wm.textContent = 'flowbiz.pl';
      document.querySelector('.stage').appendChild(wm);
    }

    buildControls(label);

    // Fit 1920x1080 → viewport.
    const stage = document.getElementById('stage');
    const wrap  = document.getElementById('wrap');
    function fit(){
      const s = Math.min(wrap.clientWidth/1920, wrap.clientHeight/1080);
      stage.style.transform = `scale(${s})`;
      const w = 1920*s, h = 1080*s;
      stage.style.left = ((wrap.clientWidth - w)/2)+'px';
      stage.style.top  = ((wrap.clientHeight - h)/2)+'px';
    }
    function toggleNative(){
      document.body.classList.toggle('native');
      fit();
    }
    window.addEventListener('resize', fit);
    window.fit = fit;
    window.toggleNative = toggleNative;

    // URL/hash native flag (for renderer).
    const q = new URLSearchParams(location.search);
    if (q.get('native') === '1' || location.hash === '#native') {
      document.body.classList.add('native');
    }
    // Chromakey background override (for keying in NLE).
    //   ?bg=green       → standard broadcast green (#00B140)
    //   ?bg=greenpure   → pure digital green (#00FF00)
    //   ?bg=blue        → blue screen (#0000FF)
    //   ?bg=magenta     → magenta key (#FF00FF)
    //   ?bg=%23RRGGBB   → arbitrary hex (URL-encoded)
    const bgParam = q.get('bg');
    if (bgParam) {
      const map = { green:'#00B140', greenpure:'#00FF00', blue:'#0000FF', magenta:'#FF00FF' };
      const color = map[bgParam] || bgParam;
      document.body.classList.add('chromakey');
      const css = document.createElement('style');
      css.textContent = `
        body.chromakey .stage { background:${color} !important; }
        body.chromakey svg.grid,
        body.chromakey svg.s07-bg,
        body.chromakey svg.s09-bg-rays,
        body.chromakey .watermark { display:none !important; }
      `;
      document.head.appendChild(css);
    }
    fit();

    // Register timeline on window (renderer + tests).
    window.__timelines = window.__timelines || {};
    window.__timelines[id] = timeline;
    window.__sceneTimeline = timeline;
    // Intended scene length (in seconds). render.js prefers this over
    // timeline.duration() because infinite-repeat tweens (repeat:-1) push
    // duration to Infinity — but the scene still has a well-defined cut-point.
    window.__sceneDuration = duration;

    // Time readout.
    const tnow = document.getElementById('__tnow');
    const tend = document.getElementById('__tend');
    tend.textContent = duration.toFixed(2);
    timeline.eventCallback('onUpdate', () => {
      tnow.textContent = timeline.time().toFixed(2);
    });

    // Buttons.
    document.getElementById('__play').onclick = () => {
      if (timeline.progress() >= 1) timeline.restart();
      else timeline.play();
    };
    document.getElementById('__restart').onclick = () => timeline.restart();
    document.getElementById('__native').onclick  = toggleNative;
    document.getElementById('__full').onclick = async () => {
      document.body.classList.add('export');
      try { await document.documentElement.requestFullscreen({ navigationUI:'hide' }); } catch(e){}
      setTimeout(()=>{
        if (window.innerWidth >= 1920 && window.innerHeight >= 1080) document.body.classList.add('native');
        fit();
      }, 80);
    };
    document.addEventListener('fullscreenchange', () => {
      if (!document.fullscreenElement) {
        document.body.classList.remove('export');
        document.body.classList.remove('native');
        fit();
      }
    });
    document.getElementById('__rec').onclick = async () => {
      if (!window.flowbizRecorder) { alert('recorder.js nieostatnie wczytany'); return; }
      const btn = document.getElementById('__rec');
      const old = btn.innerHTML;
      btn.innerHTML = '… wybierz tę kartę';
      btn.disabled = true;
      try {
        await window.flowbizRecorder.record({ timeline, duration, tail, fileName: id + '.webm' });
      } finally {
        btn.innerHTML = old; btn.disabled = false;
      }
    };

    // Spacebar play/pause.
    document.addEventListener('keydown', e => {
      if (e.key === ' ' || e.code === 'Space') {
        e.preventDefault();
        if (timeline.progress() >= 1) timeline.restart();
        else timeline.paused() ? timeline.play() : timeline.pause();
      }
    });

    // Autoplay after fonts load (unless ?autoplay=0 — used by index.html player
    // to preload scenes without consuming them in hidden iframes).
    const autoplay = q.get('autoplay') !== '0';
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(()=>{
      // Always pause at 0 first so external controllers (parent iframe) start from clean state.
      timeline.pause(0);
      if (autoplay) setTimeout(()=>timeline.play(0), 250);
    });
  }

  global.flowbizScene = { init };
})(window);
