# -*- coding: utf-8 -*-
"""Test zapytan e-mail (15.11): zrodlo E-mail na liscie i w filtrze, tresc, miniatury, galeria (strzalki, palec, Esc),
   Odpowiedz (mailto - tylko sprawdzenie adresu, bez klikania), status, Do kalendarza, szukanie po tresci, nowy mail z serwera.
   python _testy_aplikacji/test_maile.py"""
import os, sys, json, threading, urllib.request, time
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
T = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, T)
os.chdir(os.path.dirname(T))
import mock_serwer as M
import kafnav  # 19.11: nawigacja przez ekran z kafelkami
ZRZ = os.path.join(T, 'zrzuty', 'maile'); os.makedirs(ZRZ, exist_ok=True)
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]
URL = BASE + '/aplikacja/'
bledy = []
EID = 'm_18c1a2b3c4d5e6f7'


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


def run(p, w, h, mobile, ciemny=False):
    post('/mock/reset')
    b = p.chromium.launch(channel='msedge')
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=mobile, is_mobile=mobile, device_scale_factor=2 if mobile else 1)
    pg = ctx.new_page()
    pg.on('console', lambda m: m.type == 'error' and bledy.append('%d: %s' % (w, m.text)))
    pg.on('pageerror', lambda e: bledy.append('%d: %s' % (w, e)))
    nav = ('.tabs' if mobile else '.side') + ' button[data-v=%s]'
    pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1');localStorage.setItem('spk-mig-b4','1')}catch(e){}" + ("try{localStorage.setItem('spk-motyw','ciemny')}catch(e){}" if ciemny else ''))
    pg.goto(URL)
    pg.fill('#haslo', M.HASLO); pg.click('#loginBtn')
    czekaj(lambda: pg.locator('#login').is_hidden(), 'zalogowanie')
    czekaj(lambda: 'Zapisane' in pg.inner_text('#syncTx'), 'wczytanie')
    pg.click(nav % 'lista'); pg.wait_for_timeout(200)
    k = pg.locator('.karta', has_text='Paweł Dorawa')
    assert k.count() == 1, 'brak karty e-mail'
    tx = k.inner_text()
    assert 'E-mail' in tx and '6 zdj.' in tx and '45 m² Warszawa Mokotów' in tx, tx
    # filtr zrodla E-mail
    pg.click('[data-act=fT][data-f=e]'); pg.wait_for_timeout(150)
    assert pg.locator('.karta').count() == 1, pg.locator('.karta').count()
    pg.screenshot(path='%s/lista_%d%s.png' % (ZRZ, w, '_c' if ciemny else ''))
    k.click(); pg.wait_for_timeout(300)
    det = pg.locator('#det')
    assert 'E-mail od klienta' in det.inner_text() and 'proszę o wycenę cyklinowania' in det.inner_text()
    # Odpowiedz: mailto do klienta z tematem (nie klikamy)
    href = det.locator('a.odp').get_attribute('href')
    assert href.startswith('mailto:paweldorawa02@gmail.com?subject=Re%3A%2045%20m%C2%B2'), href
    # miniatury
    czekaj(lambda: det.locator('.m-z img[src^="data:image"]').count() == 6, 'miniatury: %d' % det.locator('.m-z img[src^="data:image"]').count())
    det.locator('.mail-s').scroll_into_view_if_needed()
    pg.screenshot(path='%s/karta_%d%s.png' % (ZRZ, w, '_c' if ciemny else ''))
    # galeria
    det.locator('.m-z').nth(1).click()
    czekaj(lambda: pg.locator('.gal').is_visible(), 'galeria')
    czekaj(lambda: pg.locator('.gal-f img').evaluate('i=>i.naturalWidth') >= 1600, 'pełne zdjęcie')
    assert pg.inner_text('.gal-c') == '2 / 7'.replace('7', '6')
    pg.screenshot(path='%s/galeria_%d.png' % (ZRZ, w))
    if mobile:
        cdp = ctx.new_cdp_session(pg)
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 300, 'y': 400}]})
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 150, 'y': 405}]})
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        czekaj(lambda: pg.inner_text('.gal-c') == '3 / 6', 'przesunięcie palcem: ' + pg.inner_text('.gal-c'))
        pg.click('.gal-x')
    else:
        pg.click('.gal-n'); czekaj(lambda: pg.inner_text('.gal-c') == '3 / 6', 'strzałka')
        pg.keyboard.press('ArrowLeft'); czekaj(lambda: pg.inner_text('.gal-c') == '2 / 6', 'klawisz')
        pg.keyboard.press('Escape')
    czekaj(lambda: pg.locator('.gal').count() == 0, 'zamknięcie galerii')
    # status Zatwierdzone zapisuje sie (uwaga Artura 21:23)
    det.locator('.stg button[data-s=zatw]').click()
    assert det.locator('.st-ok').inner_text().upper().startswith('ZATWIERDŹ'), 'brak przycisku zatwierdzenia'
    pg.screenshot(path='%s/status_wybor_%d%s.png' % (ZRZ, w, '_c' if ciemny else ''))
    det.locator('.st-ok').click()
    czekaj(lambda: db()['status'].get(EID, {}).get('st') == 'zatw', 'status zatw na serwerze')
    czekaj(lambda: 'Zapisane' in pg.inner_text('#syncTx'), 'Zapisane po statusie')
    if not mobile:
        assert 'kst' in pg.locator('.karta', has_text='Paweł Dorawa').get_attribute('class')
    # Do kalendarza godzinowego
    pg.locator('.k-dok').scroll_into_view_if_needed(); pg.click('.k-dok'); pg.wait_for_timeout(300)
    assert pg.locator('.kop-bar').is_visible()
    pg.locator('[data-kk$="|c2|4"]').click()
    czekaj(lambda: any(v.get('zid') == EID for v in db()['kal'].values()), 'kafelek z maila')
    kaf = [v for v in db()['kal'].values() if v.get('zid') == EID][0]
    assert '45 m² Warszawa Mokotów' in kaf['x'] or 'Mokotów' in kaf['x'], kaf
    pg.screenshot(path='%s/kalendarz_%d.png' % (ZRZ, w))
    # szukanie po tresci maila
    pg.click(nav % 'szuk'); pg.wait_for_timeout(150)
    pg.fill('#q', 'lakierowania'); pg.wait_for_timeout(300)
    assert pg.locator('.karta', has_text='Paweł Dorawa').count() == 1
    # nowy mail z serwera (wyzwalacz) pojawia sie po odswiezeniu
    post('/mock/mail', {'kl': 'Anna Nowa'})
    pg.reload(); czekaj(lambda: 'Zapisane' in pg.inner_text('#syncTx'), 'po odświeżeniu')
    pg.click(nav % 'lista'); pg.wait_for_timeout(200)
    assert pg.locator('.karta', has_text='Anna Nowa').count() == 1
    # niezatwierdzony status przy wyjsciu z karty -> pytanie (Artur 22:30)
    pg.click(nav % 'lista'); pg.wait_for_timeout(200)
    pg.locator('.karta', has_text='Paweł Dorawa').click(); pg.wait_for_timeout(300)
    pg.locator('#det .stg button[data-s=ogledziny]').click()
    pg.once('dialog', lambda d: d.accept())
    if mobile:
        pg.locator('#det [data-act=zamknij]').click()
    else:
        pg.locator('.karta', has_text='Wróblewska').click()  # na komputerze: przejscie do innej karty
    czekaj(lambda: db()['status'].get(EID, {}).get('st') == 'ogledziny', 'status po pytaniu przy wyjsciu')
    pg.wait_for_timeout(300)
    if not mobile:
        assert 'kst' in pg.locator('.karta', has_text='Paweł Dorawa').get_attribute('class')
    # Szybki wpis: przycisk Powrot zamyka okno (Artur 21:37)
    (pg.click('.tabs [data-act=szybki]') if mobile else pg.locator('[data-act=szybki]:visible').first.click()); pg.wait_for_timeout(250)
    assert pg.locator('.okno .btn-powrot').is_visible()
    pg.screenshot(path='%s/szybki_%d.png' % (ZRZ, w))
    pg.click('.okno .btn-powrot'); czekaj(lambda: pg.locator('.okno').count() == 0, 'zamkniecie szybkiego wpisu')
    # inne zrodla dalej dzialaja: karta z analizatora ma PDF oferty
    if mobile: pg.click(nav % 'lista'); pg.wait_for_timeout(300)  # 19.11: z ekranu kafelkow
    pg.click('[data-act=fT][data-f=all]'); pg.wait_for_timeout(150)
    pg.locator('.karta', has_text='Wróblewska').click(); pg.wait_for_timeout(300)
    assert pg.locator('#det [data-act=pdf]').count() == 1 and pg.locator('#det .mail-s').count() == 0
    b.close()


with sync_playwright() as p:
    run(p, 1440, 900, False)
    run(p, 390, 844, True)
    run(p, 390, 844, True, ciemny=True)
print('BLEDY:', bledy)
assert not bledy
print('OK')
