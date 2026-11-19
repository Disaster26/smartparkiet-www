"""19.11 Artur WA 16:14-16:15: ekran glowny SMART OFFICE z kafelkami zamiast dolnego paska.
Telefon 360/390/412 (dotyk) + komputer 1440: start = kafelki, kazdy kafelek otwiera swoj widok,
powrot do kafelkow: logo w naglowku, przycisk Wstecz, gest wstecz przegladarki; brak przewijania w bok, brak bledow konsoli."""
import os, sys, threading, urllib.request
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
TU = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TU)
import mock_serwer as M
ZRZ = os.path.join(TU, 'zrzuty'); os.makedirs(ZRZ, exist_ok=True)
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]
APP = os.environ.get('APP_URL', '/aplikacja/')
bledy = []
urllib.request.urlopen(urllib.request.Request(BASE + '/mock/reset', data=b'{}', method='POST'))
WIDOKI = ['dzis', 'lista', 'szuk', 'graf', 'kal']


def bez_poziomego(pg, gdzie):
    r = pg.evaluate("()=>({d:document.documentElement.scrollWidth,w:innerWidth,v:(function(){var v=document.getElementById('view');return v.scrollWidth-v.clientWidth})()})")
    assert r['d'] <= r['w'] and r['v'] <= 1, (gdzie, r)


with sync_playwright() as p:
    br = p.chromium.launch(channel='msedge')
    for w, h, tel in [(360, 740, True), (390, 844, True), (412, 915, True), (1440, 900, False)]:
        ctx = br.new_context(viewport={'width': w, 'height': h}, is_mobile=tel, has_touch=tel, device_scale_factor=2 if tel else 1)
        ctx.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
        pg = ctx.new_page()
        pg.on('pageerror', lambda e, w=w: bledy.append('%d: %s' % (w, e)))
        pg.on('console', lambda m, w=w: m.type == 'error' and bledy.append('%d: %s' % (w, m.text)))
        pg.on('dialog', lambda d: d.accept())
        pg.goto(BASE + APP); pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn')
        pg.wait_for_selector('#login', state='hidden'); pg.wait_for_timeout(1200)
        S = lambda: pg.evaluate("()=>{var X=__spk();return {v:X.S.v,sel:X.S.sel,h:X.HIST.length}}")
        assert S()['v'] == 'start', S()
        assert pg.locator('.tabs').is_hidden(), 'dolny pasek widoczny'
        assert pg.locator('.st-nazwa').inner_text().strip() == 'SMART OFFICE'
        assert pg.locator('.st-logo img').is_visible()
        assert pg.locator('.kaf').count() == 7, pg.locator('.kaf').count()
        for v in WIDOKI + ['anl']:
            assert pg.locator('.kaf[data-v=%s]' % v).is_visible(), v
        if tel:
            assert pg.locator('#wstecz').is_hidden(), 'Wstecz na ekranie startowym'
            # wszystkie kafelki mieszcza sie na ekranie bez przewijania
            dol = pg.evaluate("Math.max.apply(null,[].map.call(document.querySelectorAll('.kaf'),function(k){return k.getBoundingClientRect().bottom}))")
            print(w, 'dol ostatniego kafelka', round(dol), '/', h)
        bez_poziomego(pg, '%d start' % w)
        pg.screenshot(path=os.path.join(ZRZ, '1911c_kafelki_%d.png' % w))
        tap = (lambda sel: pg.locator(sel).first.tap()) if tel else (lambda sel: pg.locator(sel).first.click())
        # kazdy kafelek: wejscie i powrot na trzy sposoby
        sposoby = ['logo', 'wstecz', 'gest']
        for i, v in enumerate(WIDOKI):
            tap('.kaf[data-v=%s]' % v); pg.wait_for_timeout(500)
            s = S(); assert s['v'] == v, (v, s)
            assert pg.locator('.top-r .home-b').first.is_visible(), 'brak logo-powrotu w ' + v
            bez_poziomego(pg, '%d %s' % (w, v))
            if v != 'dzis' or w == 390:
                pg.screenshot(path=os.path.join(ZRZ, '1911c_%s_%d.png' % (v, w)))
            sp = sposoby[i % 3]
            if sp == 'logo':
                tap('.top-r .home-b')
            elif sp == 'wstecz':
                pg.click('#wstecz' if tel else '#wstS')
            else:
                pg.go_back()
            pg.wait_for_timeout(450)
            s = S(); assert s['v'] == 'start' and s['h'] == 0, (v, sp, s)
            assert pg.url.startswith(BASE + APP), pg.url
            print(w, v, 'powrot przez', sp, 'OK')
        # Dodaj = Szybki wpis; gest wstecz zamyka okno, zostajemy na kafelkach
        tap('.kaf-dod'); pg.wait_for_timeout(400)
        assert pg.locator('.okno').count() == 1 and 'Szybki wpis' in pg.locator('.okno').inner_text()
        pg.go_back(); pg.wait_for_timeout(400)
        assert pg.locator('.okno').count() == 0 and S()['v'] == 'start'
        # Zapytania > karta > Wstecz > Wstecz = kafelki
        tap('.kaf[data-v=lista]'); pg.wait_for_timeout(500)
        tap('.lista .karta'); pg.wait_for_timeout(600)
        s = S(); assert s['sel'], s
        if tel:
            pg.screenshot(path=os.path.join(ZRZ, '1911c_karta_%d.png' % w))
        pg.click('#wstecz' if tel else '#wstS'); pg.wait_for_timeout(450)
        s = S(); assert s['v'] == 'lista' and not s['sel'], s
        pg.click('#wstecz' if tel else '#wstS'); pg.wait_for_timeout(450)
        s = S(); assert s['v'] == 'start', s
        # gest wstecz na kafelkach nie wychodzi z aplikacji bez potrzeby (zostaje wpis bazowy)
        if not tel:
            pg.click('.side .nv-start'); pg.wait_for_timeout(300); assert S()['v'] == 'start'
            pg.click('.side button[data-v=graf]'); pg.wait_for_timeout(400); assert S()['v'] == 'graf'
            pg.click('.side .nv-start'); pg.wait_for_timeout(300); assert S()['v'] == 'start'
        # Analizator: link do /analizator.html
        assert pg.locator('.kaf[data-v=anl]').get_attribute('href') == '/analizator.html'
        if w == 390:
            pg.evaluate("document.documentElement.setAttribute('data-motyw','ciemny')"); pg.wait_for_timeout(200)
            pg.screenshot(path=os.path.join(ZRZ, '1911c_kafelki_ciemny_%d.png' % w))
            pg.evaluate("document.documentElement.removeAttribute('data-motyw')")
        ctx.close()
    br.close()
print('BLEDY:', bledy[:5])
assert not bledy
print('OK')
