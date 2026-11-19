"""19.11 Artur 01:19: linki z paska w Wycen usluge (#v=graf, #v=dodaj) otwieraja wlasciwy widok aplikacji; pasek widoczny w wycen-usluge.html."""
import os, sys, threading, urllib.request
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
TU = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TU)
import mock_serwer as M
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]; bledy = []
urllib.request.urlopen(urllib.request.Request(BASE + '/mock/reset', data=b'{}', method='POST'))
with sync_playwright() as p:
    br = p.chromium.launch(channel='msedge'); ctx = br.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    ctx.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
    pg = ctx.new_page(); pg.on('pageerror', lambda e: bledy.append(str(e)))
    pg.goto(BASE + '/aplikacja/#v=graf'); pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn'); pg.wait_for_selector('#login', state='hidden'); pg.wait_for_timeout(1200)
    v = pg.evaluate("window.__spk().S.v"); print('widok', v, pg.url); assert v == 'graf'
    pg.goto('about:blank'); pg.goto(BASE + '/aplikacja/#v=dodaj'); pg.wait_for_timeout(2500)
    jest = pg.evaluate("!!document.querySelector('.okno, #okno, [role=dialog]') && /Szybki wpis/.test(document.body.innerText)"); print('szybki wpis', jest); assert jest
    print('BLEDY:', bledy[:3])
print('OK')
