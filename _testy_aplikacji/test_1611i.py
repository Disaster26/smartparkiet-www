"""16.11i: zawsze widoczny przycisk Wstecz + gest wstecz przegladarki; Kopiuj zapytanie -> Wklej w Kalendarz / Grafik (+ Cofnij)."""
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
        pg.on('dialog', lambda d: d.accept())
        pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
        pg.goto(BASE + '/aplikacja/')
        pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn')
        czekaj(lambda: pg.locator('#login').is_hidden(), 'logowanie')
        pg.wait_for_timeout(800)
        nav = ('.tabs' if mob else '.side') + ' button[data-v=%s]'
        WS = '#wstecz' if mob else '#wstS'
        st = lambda: pg.evaluate("()=>{var X=__spk(),S=X.S;return {v:S.v,sel:S.sel,dzien:S.dzien,kt:S.kt,zk:S.zKop||null,h:X.HIST.length}}")

        def wstecz():
            pg.click(WS); pg.wait_for_timeout(450)

        def wyl():
            if mob:
                return pg.evaluate("()=>{var b=document.getElementById('wstecz');return b.classList.contains('on')&&b.classList.contains('off')}")
            return pg.locator('#wstS').is_disabled()
        # 19.11: start = ekran kafelkow; telefon - Wstecz schowany, komputer - wyszarzony
        assert st()['v'] == 'start', st()
        assert (pg.locator(WS).is_hidden() if mob else wyl()), 'Wstecz na starcie'
        pg.screenshot(path=os.path.join(ZRZ, '1611i_dzis_%d.png' % w))
        # Dzis > Zapytania > karta > Wstecz > Wstecz
        pg.click(nav % 'lista'); pg.wait_for_timeout(500)
        assert not wyl()
        pg.locator('.karta').first.click(); pg.wait_for_timeout(600)
        s1 = st(); assert s1['sel'], s1
        assert pg.locator(WS).is_visible(), 'Wstecz niewidoczny w karcie'
        pg.screenshot(path=os.path.join(ZRZ, '1611i_karta_%d.png' % w))
        wstecz(); s2 = st(); assert s2['v'] == 'lista' and not s2['sel'], s2
        wstecz(); s3 = st(); assert s3['v'] == 'start' and s3['h'] == 0, s3
        assert (pg.locator(WS).is_hidden() if mob else wyl())
        # Kalendarz > dzien > Wstecz (widok Miesiac)
        pg.click(nav % 'kal'); pg.wait_for_timeout(500)
        pg.evaluate("()=>{var X=__spk();X.S.kt='mies';X.render()}"); pg.wait_for_timeout(300)
        pg.locator('#kalSiatka [data-day]').nth(10).click(); pg.wait_for_timeout(500)
        s4 = st(); assert s4['dzien'], s4
        assert pg.locator(WS).is_visible()
        wstecz(); s5 = st(); assert not s5['dzien'] and s5['v'] == 'kal', s5
        # Szukaj > wynik > Wstecz
        pg.click(nav % 'szuk'); pg.wait_for_timeout(400)
        pg.fill('#q', 'Bajana'); pg.wait_for_timeout(600)
        pg.locator('#view .karta').first.click(); pg.wait_for_timeout(500)
        s6 = st(); assert s6['sel'] and s6['v'] == 'szuk', s6
        wstecz(); s7 = st(); assert s7['v'] == 'szuk' and not s7['sel'], s7
        # gest wstecz przegladarki
        pg.click(nav % 'graf'); pg.wait_for_timeout(500)
        pg.click(nav % 'lista'); pg.wait_for_timeout(400)
        pg.locator('.karta').first.click(); pg.wait_for_timeout(500)
        pg.go_back(); pg.wait_for_timeout(500); g1 = st(); assert g1['v'] == 'lista' and not g1['sel'], g1
        pg.go_back(); pg.wait_for_timeout(500); g2 = st(); assert g2['v'] == ('start' if mob else 'graf'), g2  # telefon: przez kafelki
        if not mob: pg.go_back(); pg.wait_for_timeout(500); g3 = st(); assert g3['v'] == 'szuk', g3
        assert pg.url.startswith(BASE + '/aplikacja/'), pg.url
        # okno zamykane gestem wstecz
        pg.evaluate("()=>{__spk().okno('<h3><span>Test</span></h3>')}"); pg.wait_for_timeout(200)
        pg.go_back(); pg.wait_for_timeout(400)
        assert pg.locator('.okno').count() == 0, 'okno nie zamknięte gestem'
        assert st()['v'] == ('start' if mob else 'szuk')
        # wyjscie do Dzis i dalej z aplikacji nie wyrzuca bez potrzeby
        for _ in range(6):
            if st()['v'] == 'start' and not st()['sel']:
                break
            pg.go_back(); pg.wait_for_timeout(400)
        assert st()['v'] == 'start', st()
        assert pg.url.startswith(BASE + '/aplikacja/'), pg.url

        # ---- Kopiuj -> Kalendarz (godzinowy) ----
        pg.click(nav % 'lista'); pg.wait_for_timeout(500)
        kb = pg.locator('.karta .zkb').first
        zid = kb.get_attribute('data-id')
        kb.click(); pg.wait_for_timeout(500)
        s8 = st(); assert s8['zk'] == zid and s8['v'] == 'kal', s8
        assert pg.locator('#zkop').is_visible()
        pg.evaluate("()=>{var X=__spk();X.S.kt='dzien';X.render()}"); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ZRZ, '1611i_kopiuj_kal_%d.png' % w))
        n0 = pg.evaluate("()=>__spk().D.kal.k.length")
        pg.locator('#kalG .ks-k[data-kk$="|4"]').first.click(); pg.wait_for_timeout(500)
        n1 = pg.evaluate("()=>__spk().D.kal.k.length"); assert n1 == n0 + 1, (n0, n1)
        info = pg.evaluate("(z)=>{var X=__spk(),D=X.D,S=X.S,it=X.item(z),k=D.kal.k[D.kal.k.length-1];return {dz:it.dz,g:it.g,kz:k.zid,kdz:k.dz,x:k.x,zk:S.zKop||null}}", zid)
        assert info['kz'] == zid and info['dz'] == info['kdz'] and not info['zk'], info
        assert 'Wstawiono' in pg.locator('#toast').inner_text()
        pg.screenshot(path=os.path.join(ZRZ, '1611i_wstawiono_kal_%d.png' % w))
        # Cofnij przyciskiem Wstecz
        wstecz()
        assert pg.evaluate("()=>__spk().D.kal.k.length") == n0, 'cofnij kalendarz'
        # ---- Kopiuj z otwartej karty -> Grafik ----
        pg.click(nav % 'lista'); pg.wait_for_timeout(500)
        pg.locator('.karta').nth(2).click(); pg.wait_for_timeout(600)
        zid2 = pg.evaluate("()=>__spk().S.sel")
        pg.locator('.det button[data-act=zKopG]').click(); pg.wait_for_timeout(600)  # 19.11: klawisz Kopiuj do Grafika (dawny .zk-d usuniety)
        assert st()['v'] == 'graf' and st()['zk'] == zid2
        pg.screenshot(path=os.path.join(ZRZ, '1611i_kopiuj_graf_%d.png' % w))
        g0 = pg.evaluate("()=>__spk().D.graf.k.length")
        cel = pg.locator('.gsiat .gk[data-act=gcel]').nth(3)
        celv = cel.get_attribute('data-cel'); cel.click(); pg.wait_for_timeout(500)
        gi = pg.evaluate("(z)=>{var X=__spk(),D=X.D,S=X.S,it=X.item(z),k=D.graf.k[D.graf.k.length-1];return {n:D.graf.k.length,zid:k.zid,od:k.od,br:k.br,dz:it.dz}}", zid2)
        assert gi['n'] == g0 + 1 and gi['zid'] == zid2 and gi['dz'] == gi['od'], gi
        assert celv.split('|')[1] == gi['br'], (celv, gi)
        # Cofnij z toastu
        pg.locator('#toast .t-cof').click(); pg.wait_for_timeout(400)
        assert pg.evaluate("()=>__spk().D.graf.k.length") == g0, 'cofnij grafik'
        # Anuluj
        pg.click(nav % 'lista'); pg.wait_for_timeout(400)
        pg.locator('.karta .zkb').first.click(); pg.wait_for_timeout(400)
        pg.locator('#zkop [data-act=zkAnul]').click(); pg.wait_for_timeout(300)
        assert not st()['zk'] and pg.locator('#zkop').is_hidden()
        # swipe w lewo dalej dziala (tylko telefon)
        if mob:
            pg.click(nav % 'lista'); pg.wait_for_timeout(400)
            k = pg.locator('.sw-w .karta').first.bounding_box()
            y = k['y'] + k['height'] / 2
            pg.mouse.move(k['x'] + k['width'] - 20, y); pg.mouse.down()
            for i in range(1, 11):
                pg.mouse.move(k['x'] + k['width'] - 20 - i * 15, y); pg.wait_for_timeout(16)
            pg.mouse.up(); pg.wait_for_timeout(400)
            assert pg.locator('.sw-w.otw').count() == 1, 'swipe nie otworzył Odpadło'
            pg.screenshot(path=os.path.join(ZRZ, '1611i_swipe_%d.png' % w))
        # 19:51 opis wpisu z reki na karcie listy
        pg.click(nav % 'lista'); pg.wait_for_timeout(300)
        pg.evaluate("()=>{var X=__spk(),it=X.D.items[0];it.typ='r';it.zr='Rozmawiałem czekam na dane';X.render()}"); pg.wait_for_timeout(300)
        assert 'Rozmawiałem czekam na dane' in pg.locator('.karta .zrl').first.inner_text()
        pg.screenshot(path=os.path.join(ZRZ, '1611i_zr_%d.png' % w))
        # ciemny motyw
        pg.evaluate("()=>{document.documentElement.setAttribute('data-motyw','ciemny')}")
        pg.click(nav % 'kal'); pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(ZRZ, '1611i_ciemny_%d.png' % w))
        b.close()
print('BLEDY:', bledy)
print('OK')
