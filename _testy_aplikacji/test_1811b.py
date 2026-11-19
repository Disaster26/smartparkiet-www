"""18.11 Artur WA 12:38-12:43: kafelki zlecen w kratce 'rezerwa' pod sobota (dotyk + mysz + wskazanie), status Zakonczone (grafitowy).
APP_URL=/sciezka/ (opcjonalnie) - test na innej kopii aplikacji serwowanej przez mock (np. kopia z produkcji)."""
import os, sys, json, threading, urllib.request, time, datetime
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
TU = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TU)
import mock_serwer as M
import kafnav  # 19.11: nawigacja przez ekran z kafelkami
URL = os.environ.get('APP_URL')
ZRZ = os.path.join(TU, 'zrzuty'); os.makedirs(ZRZ, exist_ok=True)
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]; bledy = []
APP = BASE + (URL or '/aplikacja/')
PRE = os.environ.get('ZRZ_PRE', '1811b')


def post(path, d=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(d or {}).encode(), method='POST'); return json.loads(urllib.request.urlopen(r).read())


def stan(): return json.loads(urllib.request.urlopen(BASE + '/mock/stan').read())


def czekaj(f, t=8):
    k = time.time() + t
    while time.time() < k:
        if f(): return True
        time.sleep(0.2)
    return False


pn = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
SOB = (pn + datetime.timedelta(days=5)).isoformat(); PON = pn.isoformat()


def dek(d):
    d = dict(d or {})
    if str(d.get('br') or '').endswith('~rez'): d['br'] = d['br'][:-4]; d['rez'] = 1
    return d


def kaf(i): return dek(stan()['grafik'].get(i))


def zak(v):
    if v.get('st') == 'zakonczone': return True
    h = [x.get('x') for x in (v.get('hist') or []) if str(x.get('x') or '').startswith('Status: ')]
    return v.get('st') == 'zrobione' and h and h[-1] == 'Status: Zakończone'


def hold_drag(cdp, a, b, kroki=14):
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': a[0], 'y': a[1]}]})
    time.sleep(0.45)
    for i in range(1, kroki + 1):
        x = a[0] + (b[0] - a[0]) * i / kroki; y = a[1] + (b[1] - a[1]) * i / kroki
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y}]}); time.sleep(0.03)
    time.sleep(0.1); cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})


def bok(pg, sel):
    bb = pg.locator(sel).first.bounding_box(); return (bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2)


def zaloguj(pg):
    pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
    pg.goto(APP); pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn')
    pg.wait_for_selector('#login', state='hidden'); pg.wait_for_timeout(800)


def REZ(b): return '.gk.gn.sob[data-cel="%s|N:%s"]' % (SOB, b)


with sync_playwright() as p:
    # ---------- telefon 390, dotyk ----------
    post('/mock/reset')
    br = p.chromium.launch(channel='msedge')
    ctx = br.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True, device_scale_factor=2)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: bledy.append('390: %s' % e)); zaloguj(pg)
    cdp = ctx.new_cdp_session(pg)
    pg.click('.tabs button[data-v=graf]'); pg.wait_for_timeout(600)
    assert pg.locator(REZ('b1') + ' .gn-rez').count() == 1
    # kafelek OGRODOWA (k2, b1, sroda) -> rezerwa pod sobota, brygada b3
    pg.evaluate("document.querySelector('.kf[data-id=k2]').scrollIntoView({block:'start'});document.getElementById('view').scrollTop-=150"); pg.wait_for_timeout(300)
    a = bok(pg, '.kf[data-id="k2"]'); b = bok(pg, REZ('b3')); assert 100 < a[1] < b[1] < 760, (a, b)
    hold_drag(cdp, a, b); pg.wait_for_timeout(600)
    assert czekaj(lambda: kaf('k2').get('rez') == 1 and kaf('k2').get('od') == SOB and kaf('k2').get('br') == 'b3'), kaf('k2')
    assert pg.locator(REZ('b3') + ' .kf[data-id="k2"]').count() == 1
    if os.environ.get('NATYWNE'):  # serwer >= 2026-11-18b: natywne pole rez, brygada bez ~rez
        raw = stan()['grafik']['k2']; assert raw.get('rez') == 1 and raw.get('br') == 'b3', raw
    assert pg.locator(REZ('b3') + ' .gn-rez').count() == 0
    assert pg.locator('.gk:not(.gn) .kf[data-id="k2"]').count() == 0
    pg.screenshot(path=os.path.join(ZRZ, PRE + '_grafik_390.png'))
    # i z powrotem do zwyklej kratki (sobota b1, nad rezerwa)
    a = bok(pg, REZ('b3') + ' .kf[data-id="k2"]'); b = bok(pg, '.gk[data-cel="%s|b1"]' % SOB)
    hold_drag(cdp, a, b, 18); pg.wait_for_timeout(600)
    assert czekaj(lambda: not kaf('k2').get('rez') and kaf('k2').get('od') == SOB and kaf('k2').get('br') == 'b1'), kaf('k2')
    # zlecenie z 'Do rozplanowania' (k6) -> stuknij i wskaz rezerwe
    if pg.locator('.gtray.zw').count(): pg.locator('.gdr-kaf').click(); pg.wait_for_timeout(400)  # 18.11 23:05: lista zlecen zwinieta w kafelek
    ch = pg.locator('.gtray .ch[data-k="g:k6:0"]'); ch.scroll_into_view_if_needed(); ch.tap(); pg.wait_for_timeout(400)
    pg.locator(REZ('b1')).scroll_into_view_if_needed(); pg.locator(REZ('b1')).tap(); pg.wait_for_timeout(600)
    assert czekaj(lambda: kaf('k6').get('rez') == 1 and kaf('k6').get('od') == SOB and kaf('k6').get('br') == 'b1'), kaf('k6')
    # po przeladowaniu dalej w rezerwie
    pg.reload(); pg.wait_for_timeout(1500); pg.click('.tabs button[data-v=graf]'); pg.wait_for_timeout(600)
    assert pg.locator(REZ('b1') + ' .kf[data-id="k6"]').count() == 1
    pg.locator(REZ('b1')).scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    pg.screenshot(path=os.path.join(ZRZ, PRE + '_rezerwa_390.png'))
    # ---------- status Zakonczone ----------
    pg.click('.tabs button[data-v=lista]'); pg.wait_for_timeout(500)
    assert pg.locator('.chip[data-f="zakonczone"]').count() == 1, 'brak chipa'
    n_otw0 = int(pg.locator('.chip[data-f="otwarte"] .n').inner_text())
    pg.locator('.lista .karta').first.tap(); pg.wait_for_timeout(600)
    btn = pg.locator('.stg button[data-s="zakonczone"]'); btn.scroll_into_view_if_needed()
    kol = pg.evaluate("getComputedStyle(document.querySelector('.stg button[data-s=zakonczone]')).getPropertyValue('--sc').trim()")
    assert kol.upper() == '#3A3F46', kol
    pg.screenshot(path=os.path.join(ZRZ, PRE + '_statusy_390.png'))
    btn.tap(); pg.wait_for_timeout(300); pg.locator('.st-ok').tap(); pg.wait_for_timeout(700)
    assert czekaj(lambda: any(zak(v) for v in stan()['status'].values())), 'nie zapisano statusu'
    if os.environ.get('NATYWNE'):
        assert any(v.get('st') == 'zakonczone' for v in stan()['status'].values()), 'status nie natywny'
    pg.screenshot(path=os.path.join(ZRZ, PRE + '_statusy_po_390.png'))
    pg.locator('#wstecz').tap(); pg.wait_for_timeout(500)
    if pg.locator('.chip[data-f="otwarte"]').count() == 0: pg.click('.tabs button[data-v=lista]'); pg.wait_for_timeout(500)
    assert int(pg.locator('.chip[data-f="otwarte"] .n').inner_text()) == n_otw0 - 1
    assert pg.locator('.chip[data-f="zakonczone"] .n').inner_text() == '1'
    pg.locator('.chip[data-f="zakonczone"]').tap(); pg.wait_for_timeout(400)
    assert pg.locator('.lista .karta').count() == 1
    pg.screenshot(path=os.path.join(ZRZ, PRE + '_lista_zakonczone_390.png'))
    pg.reload(); pg.wait_for_timeout(1500); pg.click('.tabs button[data-v=lista]'); pg.wait_for_timeout(500)
    assert pg.locator('.chip[data-f="zakonczone"] .n').inner_text() == '1', 'po przeladowaniu brak Zakonczone'
    assert int(pg.locator('.chip[data-f="otwarte"] .n').inner_text()) == n_otw0 - 1
    for v in ('dzis', 'szuk', 'kal', 'graf'):
        pg.click('.tabs button[data-v=%s]' % v); pg.wait_for_timeout(400)
    br.close()

    # ---------- komputer 1440, mysz ----------
    post('/mock/reset')
    br = p.chromium.launch(channel='msedge')
    ctx = br.new_context(viewport={'width': 1440, 'height': 1300})
    pg = ctx.new_page(); pg.on('pageerror', lambda e: bledy.append('1440: %s' % e)); zaloguj(pg)
    pg.click('.side button[data-v=graf]'); pg.wait_for_timeout(600)

    def mysz(src, dst):
        pg.locator(dst).scroll_into_view_if_needed(); pg.wait_for_timeout(200)
        a = pg.locator(src).first.bounding_box(); b = pg.locator(dst).bounding_box()
        if a['y'] < 80 or a['y'] > 1200:
            pg.locator(src).first.evaluate("e=>{e.scrollIntoView({block:'start'});document.getElementById('view').scrollTop-=120}"); pg.wait_for_timeout(200)
            a = pg.locator(src).first.bounding_box(); b = pg.locator(dst).bounding_box()
        assert 60 < a['y'] < 1250 and 60 < b['y'] < 1250, (src, a, dst, b)
        x0, y0 = a['x'] + a['width'] / 2, a['y'] + a['height'] / 2; x1, y1 = b['x'] + b['width'] / 2, b['y'] + b['height'] / 2
        pg.mouse.move(x0, y0); pg.mouse.down()
        for i in range(1, 21): pg.mouse.move(x0 + (x1 - x0) * i / 20, y0 + (y1 - y0) * i / 20); pg.wait_for_timeout(15)
        pg.mouse.up(); pg.wait_for_timeout(600)
    mysz('.kf[data-id="k3"]', REZ('b2'))
    assert czekaj(lambda: kaf('k3').get('rez') == 1 and kaf('k3').get('od') == SOB and kaf('k3').get('br') == 'b2'), kaf('k3')
    pg.screenshot(path=os.path.join(ZRZ, PRE + '_grafik_1440.png'))
    mysz(REZ('b2') + ' .kf[data-id="k3"]', REZ('b1'))
    assert czekaj(lambda: kaf('k3').get('rez') == 1 and kaf('k3').get('br') == 'b1'), kaf('k3')
    if pg.locator('.gtray.zw').count(): pg.locator('.gdr-kaf').click(); pg.wait_for_timeout(400)
    ch = pg.locator('.gtray .ch[data-k^="i:"]').first; kod = ch.get_attribute('data-k'); zid = kod[2:]
    mysz('.gtray .ch[data-k="%s"]' % kod, REZ('b3'))
    assert czekaj(lambda: any(dek(v).get('zid') == zid and dek(v).get('rez') == 1 and dek(v).get('br') == 'b3' for v in stan()['grafik'].values())), 'zapytanie nie w rezerwie'
    mysz(REZ('b1') + ' .kf[data-id="k3"]', '.gk[data-cel="%s|b3"]' % SOB)
    assert czekaj(lambda: not kaf('k3').get('rez') and kaf('k3').get('od') == SOB and kaf('k3').get('br') == 'b3'), kaf('k3')
    pg.click('.side button[data-v=lista]'); pg.wait_for_timeout(500)
    assert pg.locator('.chip[data-f="zakonczone"]').count() == 1
    br.close()
print('BLEDY:', bledy); assert not bledy
print('OK')
