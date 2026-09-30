#!/usr/bin/env python3
"""Record real dashboard interactions over a freshly generated synthetic replay."""
from pathlib import Path
import json, os, socket, subprocess, tempfile, time, urllib.request
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'diode-sentinel-launch/public/captures'
OUT.mkdir(parents=True,exist_ok=True);PORT=18711
PY=str(ROOT/'.venv/bin/python');metadata={'source':'fresh seeded synthetic replay','viewport':{'width':1600,'height':1000},'clips':{},'interactions':[]}
children=[]
def api(path):
    with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/{path}',timeout=2) as r:return json.load(r)
def ready():
    for _ in range(100):
        try:api('api/stats');return
        except Exception:time.sleep(.1)
    raise RuntimeError('dashboard failed to start')
with tempfile.TemporaryDirectory(prefix='diode-product-') as temp:
    folder=Path(temp);capture=folder/'synthetic.pcap';alerts=folder/'alerts.jsonl';fifo=folder/'feed.pcap';os.mkfifo(fifo)
    env={**os.environ,'DIODESENTINEL_PCAP_PATH':str(capture),'DIODESENTINEL_ALERTS_PATH':str(alerts),'DIODESENTINEL_DEMO':'1'}
    env.pop('MESSY',None)
    subprocess.run([PY,'gen_traffic.py'],cwd=ROOT,env=env,check=True,stdout=subprocess.DEVNULL)
    log=open(OUT/'pipeline.log','w')
    try:
        server=subprocess.Popen([PY,'dashboard.py',str(PORT)],cwd=ROOT,env=env,stdout=log,stderr=log);children.append(server);ready()
        pipe=subprocess.Popen([PY,'run.py','--pipe',str(fifo),'--no-state','--dga-cnn','--ml','--models-567','models567/manifest.json'],cwd=ROOT,env=env,stdout=log,stderr=log);children.append(pipe)
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('PW_CHROMIUM'),headless=True)
            page=browser.new_page(viewport={'width':1600,'height':1000})
            page.goto(f'http://127.0.0.1:{PORT}/',wait_until='networkidle')
            page.evaluate("document.documentElement.style.zoom='1'")
            # A visible cursor overlay follows the same real Playwright mouse
            # events used to operate the app. It changes no product component.
            page.evaluate('''()=>{const c=document.createElement('div');c.id='demo-cursor';c.style.cssText='position:fixed;left:0;top:0;z-index:999999;pointer-events:none;filter:drop-shadow(0 2px 4px #000);transform:translate(-100px,-100px)';c.innerHTML='<svg width="28" height="36" viewBox="0 0 28 36"><path d="M3 2 L3 27 L10 21 L16 33 L21 30 L15 18 L25 17 Z" fill="white" stroke="#111" stroke-width="2"/></svg>';document.body.append(c);document.addEventListener('mousemove',e=>{c.style.transform=`translate(${e.clientX}px,${e.clientY}px)`});document.addEventListener('mousedown',()=>c.style.filter='drop-shadow(0 0 12px #ff8a1f)');document.addEventListener('mouseup',()=>c.style.filter='drop-shadow(0 2px 4px #000)');}''')
            def move(selector,click=False):
                loc=page.locator(selector).first;loc.wait_for(state='visible',timeout=10000);loc.scroll_into_view_if_needed();box=loc.bounding_box()
                page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2,steps=45);page.wait_for_timeout(260)
                if click:loc.click();page.wait_for_timeout(600)
                metadata['interactions'].append({'clip':current,'selector':selector,'click':click})
                return box
            def record(name,action,focus,hold=1400):
                nonlocal_dummy=None
                global current
                current=name
                page.screencast.start(path=str(OUT/f'{name}.webm'),size={'width':1600,'height':1000})
                start=time.monotonic();action();page.wait_for_timeout(hold)
                box=page.locator(focus).first.bounding_box()
                metadata['clips'][name]={'focus':box,'recordedSeconds':round(time.monotonic()-start,3),'focusSelector':focus}
                page.screencast.stop();page.screenshot(path=str(OUT/f'{name}.png'))
                (OUT/'capture-manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
                print('Captured '+name,flush=True)
            replay=subprocess.Popen([PY,'demo_replay.py',str(capture),str(fifo),'--speed','25'],cwd=ROOT,env=env,stdout=log,stderr=log);children.append(replay)
            current='overview'
            def overview():
                move('#sensor-strip');page.wait_for_timeout(3600);move('#kpis');page.wait_for_timeout(3600);move('#queue-count')
            record('overview',overview,'#sensor-strip',hold=1700)
            page.wait_for_selector('#alert-rows tr[data-key]',timeout=15000)
            # Use an actual beacon record, not an invented 0.94 risk score.
            def select_alert(term):
                move('#search',True);page.locator('#search').fill(term);page.wait_for_timeout(900)
                page.wait_for_selector('#alert-rows tr[data-key]',timeout=8000);move('#alert-rows tr[data-key]',True)
            def evidence():
                select_alert('beacon');move('#detail-facts');page.wait_for_timeout(2000);move('#detail-meta')
            record('evidence',evidence,'#detail-modal .modal-box',hold=1800)
            page.keyboard.press('Escape');page.locator('#search').fill('');page.wait_for_timeout(800)
            def sources():
                move('#top-sources');page.wait_for_timeout(1800);move('#top-sources [data-source]',True);page.wait_for_timeout(1600);move('#source-filter')
            record('sources',sources,'#top-sources',hold=1200)
            page.locator('#clear-source').click();page.wait_for_timeout(800)
            def correlation():select_alert('confirmed_c2');move('#detail-related');page.wait_for_timeout(1700)
            record('correlation',correlation,'#detail-modal .modal-box',hold=1200)
            page.keyboard.press('Escape');page.locator('#search').fill('');page.wait_for_timeout(500)
            for name,term in [('dns','dns'),('encrypted','encrypted_session_malware'),('scan','recon_model_scan'),('exfil','data_exfiltration_model')]:
                def action(term=term):select_alert(term);move('#detail-facts');page.wait_for_timeout(1100)
                record(name,action,'#detail-modal .modal-box',hold=1500)
                page.keyboard.press('Escape');page.locator('#search').fill('');page.wait_for_timeout(500)
            def sensor():move('a.nav-link[href="#sensor-strip"]',True);move('#sensor-strip');page.wait_for_timeout(1200)
            record('sensor',sensor,'#sensor-strip',hold=1200)
            metadata['stats']=api('api/stats');metadata['alerts']=api('api/alerts')
            browser.close()
        for name in metadata['clips']:
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(OUT/f'{name}.webm'),'-c:v','libx264','-preset','fast','-crf','16','-vf','tpad=stop_mode=clone:stop_duration=3','-r','30','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/f'{name}.mp4')],check=True)
        (OUT/'capture-manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    finally:
        for child in reversed(children):
            if child.poll() is None:child.terminate()
        for child in children:
            try:child.wait(timeout=5)
            except subprocess.TimeoutExpired:child.kill()
        log.close()
