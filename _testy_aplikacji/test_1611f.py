"""16.11f: zolte luzne, czerwony kafelek daty + okno daty, ASAP!, Analizator w pasku, tygodnie w grafiku, nizsze karty."""
import os, sys, json, threading, urllib.request, time
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import mock_serwer as M
import kafnav  # 19.11: nawigacja przez ekran z kafelkami

ZRZ = os.path.join(TU, 'zrzuty'); os.makedirs(ZRZ, exist_ok=True)
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]
bledy = []


def post(path, d=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(d or {}).encode(), method='POST')
    return json.loads(urllib.request.urlopen(r).read())


def db():
    return json.loads(urllib.request.urlopen(BASE + '/mock/stan').read())


def czekaj(f, opis, t=10):
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


with sync_playwright() as p:
    for w, h, mob in ((390, 844, True), (1440, 900, False)):
        post('/mock/reset')
        b = p.chromium.launch(channel='msedge')
        ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=mob, is_mobile=mob, device_scale_factor=2 if mob else 1)
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: bledy.append('%d: %s' % (w, e)))
        pg.on('console', lambda m: m.type == 'error' and bledy.append('%d: %s' % (w, m.text)))
        pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
        pg.goto(BASE + '/aplikacja/')
        pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn')
        czekaj(lambda: pg.locator('#login').is_hidden(), 'logowanie')
        nav = ('.tabs' if mob else '.side') + ' button[data-v=%s]'
        pg.click(nav % 'lista'); pg.wait_for_timeout(600)
        # Analizator w pasku / menu
        sel = '.kaf[data-v=anl][href="/analizator.html"]' if mob else '#sideNav a[href="/analizator.html"]'
        if mob: kafnav.do_kafelkow(pg); pg.wait_for_timeout(300)
        assert pg.locator(sel).count() == 1, 'brak Analizatora'
        if mob: pg.click(nav % 'lista'); pg.wait_for_timeout(600)
        # luzne zolte
        kol = pg.evaluate("""()=>{var k=[...document.querySelectorAll('.karta.kst')].map(e=>getComputedStyle(e).getPropertyValue('--kst').trim());return k}""")
        assert any(c.upper() == '#FFD43B' for c in kol), ('brak żółtej karty', kol[:5])
        # kafelek daty: ustaw status termin na pierwszej karcie przez okno -> pusty kafelek
        pg.locator('.karta').first.click(); pg.wait_for_timeout(500)
        pg.screenshot(path=os.path.join(ZRZ, '1611f_karta_%d.png' % w))
        pg.wait_for_timeout(1500); stb = pg.locator('.stg button[data-s="asap"]')
        assert stb.count() >= 1, 'brak statusu ASAP!'
        pg.locator('.stg button[data-s="termin"]').click(); pg.wait_for_timeout(400)
        pg.locator('[data-act="stOk"]').click(); pg.wait_for_timeout(600)
        if mob:
            wr = pg.locator('button:has-text("Wróć")')
            if wr.count(): wr.first.click(); pg.wait_for_timeout(500)
        pg.click(nav % 'lista'); pg.wait_for_timeout(500)
        pust = pg.locator('.karta .dzr.pust')
        assert pust.count() >= 1, 'brak pustego czerwonego kafelka'
        pust.first.click(); pg.wait_for_timeout(400)
        assert pg.locator('#kdzD').count() == 1, 'brak okna daty'
        pg.fill('#kdzD', '2026-12-14'); pg.click('#kdzOk'); pg.wait_for_timeout(600)
        txt = pg.locator('.karta .dzr').first.inner_text()
        assert '14 GRU' in txt, txt
        czekaj(lambda: any((it.get('dz') == '2026-12-14') for it in (db().get('zap') or {}).values() if isinstance(it, dict)) or '2026-12-14' in json.dumps(db()), 'data na serwerze')
        pg.screenshot(path=os.path.join(ZRZ, '1611f_lista_%d.png' % w))
        hk = pg.evaluate("()=>Math.round(document.querySelector('.karta').getBoundingClientRect().height)")
        print(w, 'wysokość karty', hk)
        # 14:46 zrodlo wpisu z reki
        pg.click(('.tabs' if mob else '.side') + ' [data-act=szybki]'); pg.wait_for_timeout(300)
        pg.fill('#sKl', 'Jan Reczny'); pg.fill('#sTel', '600 111 222'); pg.fill('#sAd', 'Lipowa 3, Wola')
        pg.click('[data-act=zapiszZap]')
        czekaj(lambda: any(v.get('kl') == 'Jan Reczny' and v.get('reczne') for v in db()['status'].values()), 'wpis z ręki')
        pg.wait_for_timeout(800)
        if pg.locator('.zr-ed').count() == 0:
            pg.click(nav % 'lista'); pg.wait_for_timeout(400); pg.locator('.karta', has_text='Jan Reczny').first.click(); pg.wait_for_timeout(600)
        pg.locator('.zr-ed').first.click(); pg.wait_for_timeout(300)
        pg.locator('.zr-ch button[data-g="SMS"]').click(); pg.click('#zrOk')
        czekaj(lambda: any(v.get('kl') == 'Jan Reczny' and v.get('zr') == 'SMS' for v in db()['status'].values()), 'zr na serwerze')
        assert 'SMS' in pg.locator('.zr-ed').first.inner_text()
        pg.screenshot(path=os.path.join(ZRZ, '1611f_zrodlo_%d.png' % w))
        if mob:
            wr = pg.locator('.det .wst')
            if wr.count(): wr.first.click(); pg.wait_for_timeout(400)
        # grafik: 4 tygodnie
        pg.click(nav % 'graf'); pg.wait_for_timeout(700)
        n = pg.locator('.gtyd').count(); dni = pg.locator('.gdn').count()
        assert n == 3 and dni == 24, (n, dni)
        pg.screenshot(path=os.path.join(ZRZ, '1611f_grafik_%d.png' % w), full_page=True)
        pg.evaluate("()=>document.querySelectorAll('.gtyd')[0].scrollIntoView()"); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ZRZ, '1611f_grafik2_%d.png' % w))
        b.close()
print('BLEDY:', bledy)
print('OK')
