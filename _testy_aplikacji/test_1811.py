"""18.11 Artur WA 02:56: usuwanie zdublowanych kafelkow przesunieciem w lewo (Szukaj, Zapytania), Cofnij 5 s, trwaly zapis."""
import os, sys, json, threading, urllib.request, time
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
TU = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TU)
import mock_serwer as M
import kafnav  # 19.11: nawigacja przez ekran z kafelkami

# kopia sytuacji ze zrzutow Artura: ten sam adres kilka razy (Analizator + Wycena klienta) + wpis z reki
_rej = M.rejestr_poczatkowy
def rej():
    out = _rej()
    for n, (typ, kw, dni) in enumerate((('a', 6291, 1), ('a', 5951, 1), ('w', 5951, 0))):
        out.append({'id': 'a_MAJDANSKA%02d%s' % (n, 'x' * 14), 'typ': typ, 'ts': M.ts(dni, 10 + n, 0), 'kiedy': '', 'nr': '', 'kl': '',
                    'tel': '', 'ul': 'MAJDAŃSKA 3.113, WARSZAWA', 'ds': '', 'em': '', 'm2': 45, 'kwota': kw, 'upust': 0, 'termin': '',
                    'arkusz': '', 'analizator': '', 'zakres': [], 'info': ''})
    return out
M.rejestr_poczatkowy = rej
_st = M.stan_poczatkowy
def st0():
    d = _st()
    d['status']['a_MAJDANSKA00' + 'x' * 14] = M.czysc_zap({'st': 'odpadlo'}, False)
    d['status']['a_MAJDANSKA01' + 'x' * 14] = M.czysc_zap({'st': 'odpadlo'}, False)
    d['status']['a_MAJDANSKA02' + 'x' * 14] = M.czysc_zap({'st': 'zatw'}, False)
    d['status']['rTESTRECZNY1'] = M.czysc_zap({'reczne': True, 'ts': M.ts(0, 8, 0), 'kl': 'Emilii Gierczak', 'tel': '', 'ul': 'EMILII GIERCZAK 1/36, WARSZAWA', 'zr': 'Telefon'}, True)
    return d
M.stan_poczatkowy = st0

ZRZ = os.path.join(TU, 'zrzuty'); os.makedirs(ZRZ, exist_ok=True)
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]; bledy = []
def post(path, d=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(d or {}).encode(), method='POST'); return json.loads(urllib.request.urlopen(r).read())
def stan():
    return json.loads(urllib.request.urlopen(BASE + '/mock/stan').read())
ZN = 'Usunięto z aplikacji'
def ukryte():
    return sorted(k for k, v in stan()['status'].items() if any(h.get('x') == ZN for h in (v.get('hist') or [])))
def czekaj(f, t=6):
    k = time.time() + t
    while time.time() < k:
        if f(): return True
        time.sleep(0.2)
    return False

def dotyk(cdp, pkty, krok_ms):
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': pkty[0][0], 'y': pkty[0][1]}]})
    for x, y in pkty[1:]:
        time.sleep(krok_ms / 1000)
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y}]})
    time.sleep(krok_ms / 1000)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})

def ile(pg): return pg.locator('#wyn .sw-pel').count()

with sync_playwright() as p:
    # ---------- telefon 390 px, prawdziwe zdarzenia dotyku ----------
    post('/mock/reset')
    b = p.chromium.launch(channel='msedge')
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True, device_scale_factor=2)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: bledy.append('390: %s' % e))
    pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
    pg.goto(BASE + '/aplikacja/'); pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn')
    pg.wait_for_selector('#login', state='hidden'); pg.wait_for_timeout(800)
    cdp = ctx.new_cdp_session(pg)
    pg.click('.tabs button[data-v=szuk]'); pg.fill('#q', 'majdanska'); pg.wait_for_timeout(400)
    pg.evaluate("document.activeElement.blur()")
    assert ile(pg) == 3, ile(pg)
    pg.screenshot(path=os.path.join(ZRZ, '1811_szukaj_przed.png'))
    def box(i=0):
        return pg.locator('#wyn .sw-pel .karta').nth(i).bounding_box()
    # pionowe przewiniecie po kafelku: kafelek nie jedzie w bok
    bb = box(0); x0, y0 = bb['x'] + bb['width'] * 0.6, bb['y'] + bb['height'] / 2
    dotyk(cdp, [(x0, y0)] + [(x0 - 2 * i, y0 - 14 * i) for i in range(1, 8)], 16)
    tr = pg.evaluate("document.querySelector('#wyn .sw-pel .karta').style.transform")
    assert tr in ('', 'none'), tr
    # krotkie przesuniecie: odslania Usun, nie usuwa
    bb = box(0); x0, y0 = bb['x'] + bb['width'] * 0.7, bb['y'] + bb['height'] / 2
    dotyk(cdp, [(x0, y0)] + [(x0 - 9 * i, y0) for i in range(1, 9)], 30)
    pg.wait_for_timeout(300)
    assert pg.locator('#wyn .sw-pel.otw').count() == 1 and ile(pg) == 3
    pg.screenshot(path=os.path.join(ZRZ, '1811_odsloniete_usun.png'))
    # stukniecie obok zamyka
    pg.touchscreen.tap(195, 120); pg.wait_for_timeout(300)
    assert pg.locator('#wyn .sw-pel.otw').count() == 0
    # pelne przesuniecie powoli: usuwa + pasek Cofnij
    bb = box(0); x0, y0 = bb['x'] + bb['width'] - 20, bb['y'] + bb['height'] / 2
    dotyk(cdp, [(x0, y0)] + [(x0 - 18 * i, y0 + (i % 2)) for i in range(1, 17)], 30)
    pg.wait_for_timeout(150); pg.screenshot(path=os.path.join(ZRZ, '1811_w_trakcie.png'))
    pg.wait_for_timeout(500)
    assert ile(pg) == 2, ile(pg)
    assert pg.locator('#toast.on .t-cof').count() == 1
    pg.screenshot(path=os.path.join(ZRZ, '1811_usunieto_cofnij.png'))
    assert czekaj(lambda: len(ukryte()) == 1), ukryte()
    # Cofnij
    pg.locator('#toast .t-cof').tap(); pg.wait_for_timeout(400)
    assert ile(pg) == 3
    assert czekaj(lambda: len(ukryte()) == 0), ukryte()
    # szybkie machniecie: usuwa
    bb = box(1); x0, y0 = bb['x'] + bb['width'] * 0.75, bb['y'] + bb['height'] / 2
    dotyk(cdp, [(x0, y0)] + [(x0 - 22 * i, y0) for i in range(1, 5)], 12)
    pg.wait_for_timeout(700)
    assert ile(pg) == 2, ile(pg)
    assert czekaj(lambda: len(ukryte()) == 1)
    # pasek Cofnij znika po ok. 5 s
    pg.wait_for_timeout(5200); assert pg.locator('#toast.on').count() == 0
    # trwale: po przeladowaniu dalej ukryte
    pg.reload(); pg.wait_for_timeout(1500)
    pg.click('.tabs button[data-v=szuk]'); pg.fill('#q', 'majdanska'); pg.wait_for_timeout(400)
    assert ile(pg) == 2, ile(pg)
    # wpis z reki: usuwany naprawde
    pg.fill('#q', 'gierczak'); pg.wait_for_timeout(400); pg.evaluate("document.activeElement.blur()")
    assert ile(pg) == 1
    bb = box(0); x0, y0 = bb['x'] + bb['width'] - 20, bb['y'] + bb['height'] / 2
    dotyk(cdp, [(x0, y0)] + [(x0 - 20 * i, y0) for i in range(1, 16)], 25)
    pg.wait_for_timeout(700); assert ile(pg) == 0
    assert czekaj(lambda: 'rTESTRECZNY1' not in stan()['status'])
    pg.locator('#toast .t-cof').tap(); pg.wait_for_timeout(300)
    assert ile(pg) == 1 and czekaj(lambda: 'rTESTRECZNY1' in stan()['status'])
    # Zapytania: odsloniety przycisk Usun dziala bez okna
    pg.click('.tabs button[data-v=lista]'); pg.wait_for_timeout(500)
    n0 = pg.locator('.lista .sw-pel').count()
    pg.locator('.lista .sw-pel').nth(2).scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    bb = pg.locator('.lista .sw-pel').nth(2).bounding_box(); x0, y0 = bb['x'] + bb['width'] * 0.7, bb['y'] + bb['height'] / 2
    dotyk(cdp, [(x0, y0)] + [(x0 - 9 * i, y0) for i in range(1, 10)], 30); pg.wait_for_timeout(300)
    assert pg.locator('.lista .sw-pel.otw').count() == 1
    pg.screenshot(path=os.path.join(ZRZ, '1811_zapytania_usun.png'))
    pg.touchscreen.tap(bb['x'] + bb['width'] - 40, y0); pg.wait_for_timeout(700)
    assert pg.locator('.okno').count() == 0 and pg.locator('.lista .sw-pel').count() == n0 - 1
    pg.locator('#toast .t-cof').tap(); pg.wait_for_timeout(400)
    assert pg.locator('.lista .sw-pel').count() == n0
    # inne widoki bez bledow
    for v in ('dzis', 'graf', 'kal'):
        pg.click('.tabs button[data-v=%s]' % v); pg.wait_for_timeout(500)
    b.close()

    # ---------- komputer 1440: kosz przy najechaniu + przeciaganie myszy ----------
    post('/mock/reset')
    b = p.chromium.launch(channel='msedge')
    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    pg = ctx.new_page(); pg.on('pageerror', lambda e: bledy.append('1440: %s' % e))
    pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
    pg.goto(BASE + '/aplikacja/'); pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn')
    pg.wait_for_selector('#login', state='hidden'); pg.wait_for_timeout(800)
    pg.click('.side button[data-v=szuk]'); pg.fill('#q', 'majdanska'); pg.wait_for_timeout(400)
    assert ile(pg) == 3
    pg.locator('#wyn .sw-pel').first.hover(); pg.wait_for_timeout(500)
    op = pg.evaluate("getComputedStyle(document.querySelector('#wyn .sw-pel .sw-kosz')).opacity")
    assert op == '1', op
    pg.screenshot(path=os.path.join(ZRZ, '1811_pc_kosz.png'))
    pg.locator('#wyn .sw-pel .sw-kosz').first.click(); pg.wait_for_timeout(700)
    assert ile(pg) == 2 and pg.locator('#toast.on .t-cof').count() == 1
    pg.locator('#toast .t-cof').click(); pg.wait_for_timeout(400); assert ile(pg) == 3
    bb = pg.locator('#wyn .sw-pel .karta').nth(2).bounding_box(); x0, y0 = bb['x'] + bb['width'] * 0.6, bb['y'] + bb['height'] / 2
    pg.mouse.move(x0, y0); pg.mouse.down()
    for i in range(1, 25): pg.mouse.move(x0 - 20 * i, y0); pg.wait_for_timeout(15)
    pg.mouse.up(); pg.wait_for_timeout(700)
    assert ile(pg) == 2, ile(pg)
    # zwykle klikniecie w kafelek nadal otwiera zapytanie
    pg.locator('#wyn .sw-pel .karta').first.click(); pg.wait_for_timeout(500)
    assert pg.locator('#wyn .karta.sel').count() == 1
    b.close()
print('BLEDY:', bledy); assert not bledy
print('OK')
