"""Real Chromium smoke test; uses locally installed Playwright and Chrome/Chromium.

Run: python tests/browser_smoke.py
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def main():
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking'])
            page=browser.new_page(viewport={'width':1500,'height':940},accept_downloads=True)
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            # Network-free in-memory browser test. The host environment blocks even
            # loopback HTTP in Chromium, so the real HTML/CSS/JS are injected directly.
            html=(ROOT/'index.html').read_text()
            html=re.sub(r'<script src="web/(engine|app)\.js" defer></script>','',html)
            html=re.sub(r'<link rel="stylesheet" href="web/style\.css">','',html)
            css=(ROOT/'web/style.css').read_text()
            css=css[css.index(':root'):]  # drop optional Google Fonts import for offline QA
            page.set_content(html,wait_until='domcontentloaded')
            page.add_style_tag(content=css)
            document=(ROOT/'research/results.json').read_text()
            page.evaluate('(payload) => {window.fetch = async () => ({ok:true,json:async()=>payload});}', json.loads(document))
            page.add_script_tag(content=(ROOT/'web/engine.js').read_text())
            page.add_script_tag(content=(ROOT/'web/app.js').read_text())
            page.wait_for_function("document.querySelector('#train-s').textContent.trim() !== '—'",timeout=15000)
            assert page.locator('#candidates tr').count()==10
            assert page.locator('#equity svg').count()==1
            assert page.locator('#scatter svg').count()==1
            assert page.locator('.heat-cell').count()==50
            assert page.locator('#null svg').count()==1
            assert page.locator('#candidate').input_value()=='momentum-2'
            assert 'FROZEN PROTOCOL' in page.locator('#status').inner_text()
            page.wait_for_timeout(2500)
            page.screenshot(path=str(ROOT/'screenshots'/'desktop.png'),full_page=True)
            page.locator('#cost').fill('20')
            assert '20 bps' in page.locator('#costout').inner_text()
            assert 'EXPLORATORY' in page.locator('#status').inner_text()
            page.locator('#candidate').select_option('reversal-5')
            assert 'EXPLORATORY' in page.locator('#candidate-warning').inner_text()
            page.locator('#methods').click();assert page.locator('#dialog').evaluate('(d)=>d.open')
            page.locator('#close').click();assert not page.locator('#dialog').evaluate('(d)=>d.open')
            with page.expect_download() as dl:page.locator('#export').click()
            assert dl.value.suggested_filename.startswith('alpha-autopsy-')
            page.locator('#reset').click()
            assert page.locator('#candidate').input_value()=='momentum-2'
            assert 'FROZEN PROTOCOL' in page.locator('#status').inner_text()
            page.set_viewport_size({'width':390,'height':844})
            page.screenshot(path=str(ROOT/'screenshots'/'mobile.png'),full_page=True)
            overflow=page.evaluate('document.documentElement.scrollWidth - window.innerWidth')
            assert overflow<=3,f'mobile horizontal overflow: {overflow}px'
            assert not errors,'Browser errors: '+str(errors)
            browser.close()
            print('Browser PASS — real Chromium charts, sensitivity inputs, modal, exports, reset, desktop and mobile.')
    finally:pass

if __name__=='__main__':
    (ROOT/'screenshots').mkdir(exist_ok=True)
    main()