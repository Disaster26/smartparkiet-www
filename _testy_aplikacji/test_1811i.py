"""18.11 Artur WA 22:48-22:50: w karcie zapytania (Termin) klawisz "Kopiuj do Grafika" zamiast pola Godzina - kopiuje zlecenie i otwiera Grafik w trybie wklejania."""
import os, sys, json, threading, urllib.request
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
TU = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TU)
import mock_serwer as M
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]; APP = BASE + (os.environ.get('APP_URL') or '/aplikacja/'); bledy = []
urllib.request.urlopen(urllib.request.Request(BASE + '/mock/reset', data=b'{}', method='POST'))
r0 = M.rejestr_poczatkowy()[0]
with sync_playwright() as p:
    br = p.chromium.launch(channel='msedge'); pg = br.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    pg.on('pageerror', lambda e: bledy.append(str(e)))
    pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
    pg.goto(APP + '?motyw=ciemny'); pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn'); pg.wait_for_selector('#login', state='hidden'); pg.wait_for_timeout(1000)
    pg.click('.tabs button[data-v=lista]'); pg.wait_for_timeout(600)
    pg.locator('.karta', has_text=r0['kl'].split()[0]).first.click(); pg.wait_for_timeout(800)
    btn = pg.locator('button[data-act=zKopG]'); assert btn.count() == 1, 'brak klawisza'
    assert pg.locator('#tG').get_attribute('type') == 'hidden'
    btn.scroll_into_view_if_needed(); pg.screenshot(path=os.path.join(TU, 'zrzuty', '1811i_karta.png'))
    btn.click(); pg.wait_for_timeout(800)
    st = pg.evaluate("(()=>{const X=window.__spk();return {v:X.S.v,zk:X.S.zKop}})()")
    print('po kliknieciu', st)
    assert st['v'] == 'graf' and st['zk'] == r0['id'], st
    pg.screenshot(path=os.path.join(TU, 'zrzuty', '1811i_grafik.png'))
    n0 = pg.evaluate("window.__spk().D.graf.k.length")
    pg.locator('.gk[data-act=gcel]').first.click(); pg.wait_for_timeout(800)
    n1 = pg.evaluate("window.__spk().D.graf.k.length")
    print('kafelki grafiku', n0, '->', n1); assert n1 == n0 + 1
    pg.evaluate("(()=>{const X=window.__spk();X.S.gd=new Date(Date.now()+21*864e5);X.render(true);})()")
    pg.click('.tabs button[data-v=lista]'); pg.wait_for_timeout(400); pg.click('.tabs button[data-v=graf]'); pg.wait_for_timeout(600)
    tyd = pg.evaluate("(()=>{const X=window.__spk();const g=new Date(X.S.gd),d=new Date();return Math.abs(g-d)<864e5*1.1})()")
    print('grafik na biezacym tygodniu:', tyd); assert tyd
    print('BLEDY:', bledy); assert not bledy
print('OK')
