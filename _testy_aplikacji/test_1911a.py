"""19.11 Artur 00:06-00:07: STATUS wersalikami, pomaranczowy ZATWIERDZ obok naglowka (rozmiar kafelka statusu), zatwierdzenie dziala; lista Zlecenia w Grafiku w kolorach statusu."""
import os, sys, threading, urllib.request
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
TU = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TU)
import mock_serwer as M
import kafnav  # 19.11: nawigacja przez ekran z kafelkami
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]; APP = BASE + '/aplikacja/'; bledy = []
urllib.request.urlopen(urllib.request.Request(BASE + '/mock/reset', data=b'{}', method='POST'))
r0 = M.rejestr_poczatkowy()[0]
with sync_playwright() as p:
    br = p.chromium.launch(channel='msedge'); pg = br.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
    pg.on('pageerror', lambda e: bledy.append(str(e)))
    pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
    pg.goto(APP + '?motyw=ciemny'); pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn'); pg.wait_for_selector('#login', state='hidden'); pg.wait_for_timeout(900)
    pg.click('.tabs button[data-v=lista]'); pg.wait_for_timeout(500)
    pg.screenshot(path=os.path.join(TU, 'zrzuty', '1911a_lista.png'))
    pg.locator('.karta', has_text=r0['kl'].split()[0]).first.click(); pg.wait_for_timeout(700)
    assert pg.locator('.det .zk-d').count() == 0 and pg.locator('.det .hist').count() == 0
    pg.locator('.det .stg button[data-s=wtoku]').click(); pg.wait_for_timeout(400)
    ok = pg.locator('.det .st-h .st-ok'); assert ok.count() == 1
    b1 = ok.bounding_box(); b2 = pg.locator('.det .stg button').first.bounding_box(); print('zatwierdz', b1, 'kafelek', b2)
    assert abs(b1['width'] - b2['width']) < 4
    pg.screenshot(path=os.path.join(TU, 'zrzuty', '1911a_status.png'))
    ok.click(); pg.wait_for_timeout(600)
    st = pg.evaluate("(z)=>window.__spk().item(z).st", r0['id']); print('status', st); assert st == 'wtoku'
    pg.click('.det .wst'); pg.wait_for_timeout(400); pg.click('.tabs button[data-v=graf]'); pg.wait_for_timeout(700); pg.click('.gdr-kaf'); pg.wait_for_timeout(400)
    n = pg.locator('.gtray .chips .ch.chst').count(); print('kolorowe pozycje', n); assert n > 0
    pg.screenshot(path=os.path.join(TU, 'zrzuty', '1911a_graf.png'))
    print('BLEDY:', bledy); assert not bledy
print('OK')
