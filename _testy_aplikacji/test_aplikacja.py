# -*- coding: utf-8 -*-
"""Testy aplikacji /aplikacja/ na lokalnym mocku backendu (Playwright, Edge).
   python _testy_aplikacji/test_aplikacja.py        (zrzuty w _testy_aplikacji/zrzuty/)"""
import os, sys, json, threading, urllib.request, time
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import openpyxl

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import mock_serwer as M

ZRZ = os.path.join(TU, 'zrzuty'); os.makedirs(ZRZ, exist_ok=True)
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


def run(p, w, h, mobile):
    post('/mock/reset')
    b = p.chromium.launch(channel='msedge')
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=mobile, is_mobile=mobile, accept_downloads=True, device_scale_factor=2 if mobile else 1)
    pg = ctx.new_page()
    oczekiwane = {'on': False}
    def kons(m):
        if m.type == 'error' and not (oczekiwane['on'] and ('Failed to load resource' in m.text or 'ERR_INTERNET_DISCONNECTED' in m.text or 'Failed to fetch' in m.text)):
            bledy.append('%d: %s' % (w, m.text))
    pg.on('console', kons)
    pg.on('pageerror', lambda e: bledy.append('%d: %s' % (w, e)))
    nav = ('.tabs' if mobile else '.side') + ' button[data-v=%s]'
    pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
    pg.goto(URL)
    # --- logowanie
    assert pg.locator('#login').is_visible()
    pg.fill('#haslo', 'zle-haslo'); pg.click('#loginBtn')
    czekaj(lambda: 'Złe hasło' in pg.inner_text('#loginErr'), 'komunikat złego hasła')
    pg.fill('#haslo', M.HASLO); pg.click('#loginBtn')
    czekaj(lambda: pg.locator('#login').is_hidden(), 'zalogowanie')
    czekaj(lambda: 'Zapisane' in pg.inner_text('#syncTx'), 'pasek stanu po wczytaniu')
    pg.screenshot(path='%s/dzis_%d.png' % (ZRZ, w))
    # --- lista
    pg.click(nav % 'lista'); pg.wait_for_timeout(150)
    assert pg.locator('.karta').count() == 12, pg.locator('.karta').count()
    pg.screenshot(path='%s/lista_%d.png' % (ZRZ, w))
    # --- karta: status, notatka, termin
    pg.locator('.karta', has_text='Wróblewska').click(); pg.wait_for_timeout(350)
    zid = 'a_MOCKARKUSZ00' + 'x' * 14
    pg.click('.stg button[data-s=rozmowa]')
    czekaj(lambda: db()['status'].get(zid, {}).get('st') == 'rozmowa', 'status na serwerze')
    pg.fill('#nt', 'Klucze u sąsiadki, kolor naturalny')
    czekaj(lambda: db()['status'].get(zid, {}).get('nt') == 'Klucze u sąsiadki, kolor naturalny', 'notatka na serwerze')
    pg.locator('.szyb button', has_text='Jutro').click()
    czekaj(lambda: db()['status'].get(zid, {}).get('dz'), 'termin na serwerze')
    assert db()['status'][zid]['st'] == 'termin'  # przypisanie terminu ustawia "Termin ustalony"
    pg.screenshot(path='%s/karta_%d.png' % (ZRZ, w))
    if mobile:
        pg.click('.det .wst'); pg.wait_for_timeout(350)
    # --- wpis z ręki
    pg.click(('.tabs' if mobile else '.side') + ' [data-act=szybki]'); pg.wait_for_timeout(200)
    pg.fill('#sKl', 'Jan Testowy'); pg.fill('#sTel', '600 111 222'); pg.fill('#sAd', 'Lipowa 3, Wola'); pg.fill('#sNt', 'dzwonił po wycenę')
    pg.click('[data-act=zapiszZap]')
    czekaj(lambda: any(v.get('kl') == 'Jan Testowy' and v.get('reczne') for v in db()['status'].values()), 'wpis z ręki na serwerze')
    if mobile:
        pg.click('.det .wst'); pg.wait_for_timeout(350)
    # --- grafik: przeciągnięcie zapytania z "do rozplanowania" na brygadę i dzień
    pg.click(nav % 'graf'); pg.wait_for_timeout(250)
    pg.screenshot(path='%s/grafik_%d.png' % (ZRZ, w))
    chip = pg.locator('.gtray .ch', has_text='Michalak').first
    cel = pg.locator('.gk[data-cel$="|b3"]').nth(1 if mobile else 4)
    if not mobile:
        cel.scroll_into_view_if_needed()
    chip.scroll_into_view_if_needed()
    cb = chip.bounding_box(); tb = cel.bounding_box()
    if mobile:
        cdp = ctx.new_cdp_session(pg)
        x0, y0 = cb['x'] + 20, cb['y'] + cb['height'] / 2
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x0, 'y': y0}]}); pg.wait_for_timeout(450)
        tb = cel.bounding_box(); x1, y1 = tb['x'] + tb['width'] / 2, tb['y'] + tb['height'] / 2
        for i in range(1, 11):
            cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x0 + (x1 - x0) * i / 10, 'y': y0 + (y1 - y0) * i / 10}]}); pg.wait_for_timeout(30)
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    else:
        pg.mouse.move(cb['x'] + 20, cb['y'] + cb['height'] / 2); pg.mouse.down()
        pg.mouse.move(tb['x'] + 30, tb['y'] + 30, steps=12); pg.mouse.up()
    k = czekaj(lambda: next((v for v in db()['grafik'].values() if v.get('zid') == 'a_MOCKARKUSZ01' + 'x' * 14), None), 'kafelek z katalogu na serwerze')
    assert k['br'] == 'b3' and k['ul'] == 'DERENIOWA 9' and k['mies'] == '33', k
    pg.wait_for_timeout(500)
    # --- kolor z palety
    kid = [i for i, v in db()['grafik'].items() if v.get('zid') == 'a_MOCKARKUSZ01' + 'x' * 14][0]
    kaf = pg.locator('.kf[data-id="%s"]' % kid).first
    kaf.scroll_into_view_if_needed(); kaf.locator('.kd').click(); pg.wait_for_timeout(150)
    pg.locator('.pal [data-pk="#6B2A5E"]').click()
    czekaj(lambda: db()['grafik'][kid]['c'] == '#6B2A5E', 'kolor na serwerze')
    assert '#FFFFFF' in pg.locator('.kf[data-id="%s"]' % kid).first.get_attribute('style')
    # --- zlecenie wielodniowe
    pg.locator('.kf[data-id="%s"]' % kid).first.click(); pg.wait_for_timeout(200)
    pg.click('.okno [data-dni="1"]'); pg.click('.okno [data-dni="1"]'); pg.click('.okno [data-g="zap"]')
    czekaj(lambda: db()['grafik'][kid]['dni'] == 3, 'wielodniowe na serwerze')
    czekaj(lambda: pg.locator('.kf[data-id="%s"]' % kid).count() >= 2, 'kafelek w kolejnych dniach')
    # --- nowe zlecenie wpisane małymi literami
    pg.click('[data-act=gnowy]'); pg.wait_for_timeout(150)
    pg.type('#fA', 'rycerska 12 radzymin'); pg.fill('#fM', '60'); pg.type('#fI', 'warstwa + schody')
    pg.click('.okno [data-g="zap"]')
    czekaj(lambda: any(v['ul'] == 'RYCERSKA 12 RADZYMIN' and v['info'] == 'WARSTWA + SCHODY' for v in db()['grafik'].values()), 'nowe zlecenie na serwerze')
    # --- eksport tygodnia
    with pg.expect_download() as dl:
        pg.click('[data-act=gxls]')
    f = '%s/grafik_%d.xlsx' % (ZRZ, w); dl.value.save_as(f)
    ws = openpyxl.load_workbook(f).active
    assert ws['B2'].value == 'JARO.2'
    assert 'LIPOWA 7 ZĄBKI (60) / WARSTWA + SCHODY' in '\n'.join(str(c.value) for r in ws.iter_rows() for c in r if c.value)
    pg.screenshot(path='%s/grafik_po_%d.png' % (ZRZ, w), full_page=True)
    # --- synchronizacja: druga karta (jak drugi telefon / komputer)
    pg2 = ctx.new_page()
    pg2.on('pageerror', lambda e: bledy.append('%d karta2: %s' % (w, e)))
    pg2.goto(URL); czekaj(lambda: 'Zapisane' in pg2.inner_text('#syncTx'), 'karta 2 wczytana')
    pg2.click(nav % 'graf'); pg2.wait_for_timeout(200)
    assert pg2.locator('.kf[data-id="%s"]' % kid).count() >= 2
    pg2.locator('.kf[data-id="%s"]' % kid).first.locator('.kd').click(); pg2.wait_for_timeout(150)
    pg2.locator('.pal [data-ps="ok"]').click()
    czekaj(lambda: db()['grafik'][kid]['c'] == '' and db()['grafik'][kid]['kol'] == 'ok', 'zmiana z karty 2 na serwerze')
    nowy = post('/mock/nowa', {'kl': 'Zofia Nowa'})
    pg.bring_to_front(); pg.evaluate('window.spkApp.pobierz()')
    czekaj(lambda: '#2E9E3A' in (pg.locator('.kf[data-id="%s"]' % kid).first.get_attribute('style') or ''), 'karta 1 widzi zmianę koloru z karty 2')
    pg.click(nav % 'dzis'); pg.wait_for_timeout(150)
    assert pg.locator('#gNowe', has_text='Zofia Nowa').count() == 1, 'nowe zapytanie ze strony w "Nowe"'
    pg2.close()
    # --- błąd zapisu: zmiana cofnięta
    oczekiwane['on'] = True
    post('/mock/awaria', {'on': True})
    pg.click(nav % 'lista'); pg.wait_for_timeout(150)
    pg.locator('.karta', has_text='Joanna Lis').click(); pg.wait_for_timeout(350)
    pg.click('.stg button[data-s=odpadlo]')
    czekaj(lambda: pg.locator('.stg button.on').get_attribute('data-s') == 'luzne', 'cofnięcie statusu po błędzie')
    assert 'cofnięta' in pg.inner_text('#toast') or 'Nie zapisano' in pg.inner_text('#syncTx')
    post('/mock/awaria', {'on': False})
    # --- offline: tylko podgląd
    pg.evaluate('window.spkApp.pobierz()'); czekaj(lambda: 'Zapisane' in pg.inner_text('#syncTx'), 'powrót online')
    ctx.set_offline(True)
    pg.evaluate('window.spkApp.pobierz()')
    czekaj(lambda: 'Brak internetu' in pg.inner_text('#syncTx'), 'pasek offline')
    przed = db()['zapisy']
    pg.click('.stg button[data-s=ogledziny]'); pg.wait_for_timeout(500)
    assert pg.locator('.stg button.on').get_attribute('data-s') == 'luzne' and db()['zapisy'] == przed, 'offline nie zmienia danych'
    ctx.set_offline(False)
    pg.evaluate('window.spkApp.pobierz()'); czekaj(lambda: 'Zapisane' in pg.inner_text('#syncTx'), 'online po offline')
    oczekiwane['on'] = False
    # --- PWA: service worker, manifest, noindex
    czekaj(lambda: pg.evaluate('navigator.serviceWorker && navigator.serviceWorker.getRegistration().then(r=>!!r)'), 'service worker')
    assert pg.locator('meta[name=robots]').get_attribute('content').startswith('noindex')
    ow = pg.evaluate('document.documentElement.scrollWidth - innerWidth')
    assert ow <= 0, ('poziomy scroll', ow)
    # --- wylogowanie
    if mobile:
        pg.click('.det .wst'); pg.wait_for_timeout(350)
    pg.click(nav % 'dzis'); pg.on('dialog', lambda d: d.accept())
    pg.locator('.dzis-w .wyl').click(); pg.wait_for_timeout(200)
    assert pg.locator('#login').is_visible() and not pg.evaluate("localStorage.getItem('spk-app-token')")
    b.close()
    print('OK', w, h)


with sync_playwright() as p:
    run(p, 390, 844, True)
    run(p, 1440, 900, False)
print('BLEDY KONSOLI:', bledy)
assert not bledy
srv.shutdown()
