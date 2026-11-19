# -*- coding: utf-8 -*-
"""Test kalendarza godzinowego (15.11): wpis, wklejanie, Ctrl+V, przeciaganie mysza i palcem, wydluzanie, kolor, odswiezenie, Do kalendarza, tydzien, kolumny.
   python _testy_aplikacji/test_kalendarz.py [--ciemny]"""
import os, sys, json, threading, urllib.request, time
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
T = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, T)
os.chdir(os.path.dirname(T))
import mock_serwer as M
import kafnav  # 19.11: nawigacja przez ekran z kafelkami
ZRZ = os.path.join(T, 'zrzuty', 'kalendarz'); os.makedirs(ZRZ, exist_ok=True)
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]
URL = BASE + '/aplikacja/'
bledy = []

def post(path, d=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(d or {}).encode(), method='POST')
    return json.loads(urllib.request.urlopen(r).read())

def db():
    return json.loads(urllib.request.urlopen(BASE + '/mock/stan').read())

def czekaj(f, opis, t=8):
    k = time.time() + t
    while time.time() < k:
        try:
            v = f()
            if v:
                return v
        except Exception:
            pass
        time.sleep(0.15)
    raise AssertionError('nie doczekałem się: ' + opis)

def kal():
    return db()['kal']

def run(p, w, h, mobile, ciemny=False):
    post('/mock/reset')
    b = p.chromium.launch(channel='msedge')
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=mobile, is_mobile=mobile, device_scale_factor=2 if mobile else 1)
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin=BASE)
    pg = ctx.new_page()
    pg.on('console', lambda m: m.type == 'error' and bledy.append('%d: %s' % (w, m.text)))
    pg.on('pageerror', lambda e: bledy.append('%d: %s' % (w, e)))
    nav = ('.tabs' if mobile else '.side') + ' button[data-v=%s]'
    pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1');localStorage.setItem('spk-mig-b4','1')}catch(e){}" + ("try{localStorage.setItem('spk-motyw','ciemny')}catch(e){}" if ciemny else ''))
    pg.goto(URL)
    pg.fill('#haslo', M.HASLO); pg.click('#loginBtn')
    czekaj(lambda: pg.locator('#login').is_hidden(), 'zalogowanie')
    czekaj(lambda: 'Zapisane' in pg.inner_text('#syncTx'), 'wczytanie')
    pg.click(nav % 'kal'); pg.wait_for_timeout(200)
    assert pg.locator('.kgr').count() == 1, bledy
    pg.screenshot(path='%s/kal_pusty_%d.png' % (ZRZ, w))
    # 1) wpis z klawiatury w kratce 11:00 kolumna 1
    cel = pg.locator('[data-kk$="|c1|2"]')
    cel.click(); pg.wait_for_timeout(100)
    pg.keyboard.type('Kontakt Kowalski')
    pg.keyboard.press('Enter')
    
    czekaj(lambda: len(kal()) == 1, 'kafelek na serwerze')
    k1 = list(kal().values())[0]
    assert k1['g'] == '11:00' and k1['ko'] == 'c1' and k1['min'] == 60, k1
    # 2) wklejenie w edytorze (schowek)
    pg.evaluate("navigator.clipboard.writeText('Grójecka 12/4, Ochota (54 m²) · Nowak')")
    pg.locator('[data-kk$="|c2|6"]').click(); pg.wait_for_timeout(100)
    pg.keyboard.press('Control+V'); pg.wait_for_timeout(100)
    pg.keyboard.press('Enter')
    czekaj(lambda: any('Grójecka' in v['x'] for v in kal().values()), 'wklejony kafelek')
    # 3) Ctrl+V nad kratką (tylko komputer)
    if not mobile:
        pg.evaluate("navigator.clipboard.writeText('Odbiór lakieru')")
        pg.locator('[data-kk$="|c3|0"]').hover(); pg.wait_for_timeout(80)
        pg.keyboard.press('Control+V')
        czekaj(lambda: any(v['x'] == 'Odbiór lakieru' and v['g'] == '10:00' and v['ko'] == 'c3' for v in kal().values()), 'Ctrl+V nad kratką')
    pg.wait_for_timeout(300)
    pg.screenshot(path='%s/kal_3kafle_%d.png' % (ZRZ, w))
    # 4) przeciągnięcie kafelka Kowalski do kolumny 3, 14:00
    kt = pg.locator('.kt', has_text='Kontakt Kowalski')
    bb = kt.bounding_box(); cb = pg.locator('[data-kk$="|c3|8"]').bounding_box()
    sx, sy = bb['x'] + bb['width'] / 2, bb['y'] + 8
    tx, ty = cb['x'] + cb['width'] / 2, cb['y'] + 8
    if mobile:
        # dotyk: przytrzymanie 300 ms i przesuniecie (CDP touch)
        cdp = ctx.new_cdp_session(pg)
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': sx, 'y': sy}]})
        pg.wait_for_timeout(450)
        for i in range(1, 11):
            cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': sx + (tx - sx) * i / 10, 'y': sy + (ty - sy) * i / 10}]})
            pg.wait_for_timeout(30)
        pg.screenshot(path='%s/kal_ciagniecie_%d.png' % (ZRZ, w))
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    else:
        pg.mouse.move(sx, sy); pg.mouse.down()
        for i in range(1, 11):
            pg.mouse.move(sx + (tx - sx) * i / 10, sy + (ty - sy) * i / 10); pg.wait_for_timeout(20)
        pg.screenshot(path='%s/kal_ciagniecie_%d.png' % (ZRZ, w))
        pg.mouse.up()
    czekaj(lambda: any(v['x'] == 'Kontakt Kowalski' and v['g'] == '14:00' and v['ko'] == 'c3' for v in kal().values()), 'przeciągnięty kafelek ' + json.dumps(kal(), ensure_ascii=False))
    pg.wait_for_timeout(400)
    # 5) wydłużenie (dolny pasek) o 2 kratki
    kt = pg.locator('.kt', has_text='Kontakt Kowalski'); bb = kt.bounding_box()
    rz = kt.locator('.kt-roz').bounding_box(); kh = pg.locator('.ks-k').first.bounding_box()['height']
    rx, ry = rz['x'] + rz['width'] / 2, rz['y'] + rz['height'] / 2
    if mobile:
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': rx, 'y': ry}]})
        for i in range(1, 9):
            cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': rx, 'y': ry + kh * 2 * i / 8}]}); pg.wait_for_timeout(25)
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    else:
        pg.mouse.move(rx, ry); pg.mouse.down()
        for i in range(1, 9):
            pg.mouse.move(rx, ry + kh * 2 * i / 8); pg.wait_for_timeout(20)
        pg.mouse.up()
    czekaj(lambda: any(v['x'] == 'Kontakt Kowalski' and v['min'] == 120 for v in kal().values()), 'wydłużenie ' + json.dumps(kal(), ensure_ascii=False))
    pg.wait_for_timeout(450)
    # 6) zmiana koloru w oknie kafelka
    pg.locator('.kt', has_text='Grójecka').click(); pg.wait_for_timeout(250)
    pg.screenshot(path='%s/kal_okno_%d.png' % (ZRZ, w))
    pg.click('.k-pal button[data-kp="#FF5FCB"]'); pg.click('.akc-z[data-k=ok]')
    czekaj(lambda: any('Grójecka' in v['x'] and v['c'] == '#FF5FCB' for v in kal().values()), 'kolor')
    # 7) odświeżenie - zostaje
    pg.reload(); czekaj(lambda: 'Zapisane' in pg.inner_text('#syncTx'), 'po odświeżeniu'); pg.click(nav % 'kal'); pg.wait_for_timeout(200)
    czekaj(lambda: pg.locator('.kt').count() == (2 if mobile else 3), 'kafelki po odświeżeniu: %d' % pg.locator('.kt').count())
    pg.wait_for_timeout(300)
    pg.screenshot(path='%s/kal_po_odsw_%d.png' % (ZRZ, w))
    pg.screenshot(path='%s/kal_po_odsw_pelny_%d.png' % (ZRZ, w), full_page=True)
    # 8) Do kalendarza z karty zapytania
    pg.click(nav % 'lista'); pg.wait_for_timeout(150)
    pg.locator('.karta', has_text='Wróblewska').click(); pg.wait_for_timeout(400)
    pg.locator('.k-dok').scroll_into_view_if_needed(); pg.click('.k-dok'); pg.wait_for_timeout(300)
    assert pg.locator('.kop-bar').is_visible()
    pg.screenshot(path='%s/kal_wstaw_%d.png' % (ZRZ, w))
    pg.locator('[data-kk$="|c2|1"]').click()
    czekaj(lambda: any(v.get('zid') and v['g'] == '10:30' for v in kal().values()), 'kafelek z zapytania')
    # 9) tydzień
    pg.click('.kseg button[data-k=tg]'); pg.wait_for_timeout(300)
    assert pg.locator('.kdn').count() >= 6
    pg.screenshot(path='%s/kal_tydzien_%d.png' % (ZRZ, w))
    # 10) kolumny
    pg.click('[data-act=kust]'); pg.wait_for_timeout(200)
    pg.fill('[data-kn="0"]', 'artur'); pg.click('[data-kz]')
    czekaj(lambda: db()['ust'].get('kalKol', [{}])[0].get('n') == 'ARTUR', 'nazwa kolumny')
    # Terminy (stary widok) nadal dziala
    pg.click('.kseg button[data-k=tydz]'); pg.wait_for_timeout(200)
    assert pg.locator('.tray').count() == 1
    pg.click('.kseg button[data-k=dzien]'); pg.wait_for_timeout(200)
    # Dziś pokazuje kafelki
    pg.click(nav % 'dzis'); pg.wait_for_timeout(200)
    pg.screenshot(path='%s/dzis_%d.png' % (ZRZ, w))
    b.close()

with sync_playwright() as p:
    run(p, 1440, 900, False)
    run(p, 390, 844, True)
    run(p, 390, 844, True, ciemny=True) if '--ciemny' in sys.argv else None
print('BLEDY:', bledy)
print('OK')
