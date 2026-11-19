"""18.11 Artur WA 23:05: Do rozplanowania jako pomaranczowy kafelek; klik otwiera liste Zlecenia."""
import os, sys, threading, urllib.request
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
TU = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TU)
import mock_serwer as M
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]; APP = BASE + '/aplikacja/'; bledy = []
urllib.request.urlopen(urllib.request.Request(BASE + '/mock/reset', data=b'{}', method='POST'))
with sync_playwright() as p:
    br = p.chromium.launch(channel='msedge'); pg = br.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
    pg.on('pageerror', lambda e: bledy.append(str(e)))
    pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
    pg.goto(APP + '?motyw=ciemny'); pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn'); pg.wait_for_selector('#login', state='hidden'); pg.wait_for_timeout(900)
    pg.click('.tabs button[data-v=graf]'); pg.wait_for_timeout(600)
    assert pg.locator('.gtray.zw').count() == 1 and not pg.locator('.gtray .chips').is_visible()
    pg.screenshot(path=os.path.join(TU, 'zrzuty', '1811k_zw.png'))
    pg.click('.gdr-kaf'); pg.wait_for_timeout(500)
    n = pg.locator('.gtray.ot .chips .ch').count(); print('zlecen na liscie', n); assert n > 0
    pg.screenshot(path=os.path.join(TU, 'zrzuty', '1811k_ot.png'))
    pg.locator('.gtray .chips .ch').first.click(); pg.wait_for_timeout(300)
    n0 = pg.evaluate("window.__spk().D.graf.k.length"); pg.locator('.gk[data-act=gcel]').first.click(); pg.wait_for_timeout(600)
    print('wstawione', n0, '->', pg.evaluate("window.__spk().D.graf.k.length"))
    print('BLEDY:', bledy); assert not bledy
print('OK')
