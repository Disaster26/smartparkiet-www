"""18.11 Artur WA 13:17-13:34: soboty (kratki + rezerwa) w kolorze podwykonawcy, tlo biezacego tygodnia grafitowe,
oferta w otwartej formie (Edytuj ofertę) w karcie i w oknie zlecenia na grafiku. APP_URL=/sciezka/ opcjonalnie."""
import os, sys, json, threading, urllib.request, time
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
TU = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TU)
import mock_serwer as M
URL = os.environ.get('APP_URL')
ZRZ = os.path.join(TU, 'zrzuty'); os.makedirs(ZRZ, exist_ok=True)
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]; bledy = []
APP = BASE + (URL or '/aplikacja/')


def post(path, d=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(d or {}).encode(), method='POST'); return json.loads(urllib.request.urlopen(r).read())


def zaloguj(pg, motyw):
    pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
    pg.goto(APP + '?motyw=' + motyw); pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn')
    pg.wait_for_selector('#login', state='hidden'); pg.wait_for_timeout(800)


def kolory(pg):
    return pg.evaluate("""(()=>{const g=s=>{const e=document.querySelector(s);return e?getComputedStyle(e).backgroundColor:null};
      return {sob:g('.gk.sob:not(.gn)'),rez:g('.gk.gn.sob'),gbt:g('.gsiat>.gbt'),n:document.querySelectorAll('.gsiat>.gbt').length,
        gbtH:(document.querySelector('.gsiat>.gbt')||{}).offsetHeight||0,
        tydz:(()=>{const b=document.querySelector('.gsiat>.gbt').getBoundingClientRect(),d=[...document.querySelectorAll('.gdn')].filter(x=>{const r=x.getBoundingClientRect();return r.top>=b.top-1&&r.bottom<=b.bottom+1});return d.length})()}})()""")


with sync_playwright() as p:
    for motyw, vw in (('ciemny', 390), ('jasny', 390), ('ciemny', 1440)):
        post('/mock/reset')
        br = p.chromium.launch(channel='msedge')
        tel = vw < 900
        ctx = br.new_context(viewport={'width': vw, 'height': 844 if tel else 1100}, has_touch=tel, is_mobile=tel, device_scale_factor=2 if tel else 1)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: bledy.append('%s %s: %s' % (motyw, vw, e))); zaloguj(pg, motyw)
        pg.click(('.tabs' if tel else '.side') + ' button[data-v=graf]'); pg.wait_for_timeout(700)
        k = kolory(pg); print(motyw, vw, k)
        assert k['n'] == 1 and k['tydz'] == 6, k
        assert pg.evaluate("[...document.querySelectorAll('.gdn')].every(e=>Math.abs(e.getBoundingClientRect().left-document.querySelector('.gsiat').getBoundingClientRect().left)<2)"), 'dni nie w 1. kolumnie'
        assert pg.evaluate("document.querySelector('.gsiat').scrollWidth<=document.querySelector('.gsiat').clientWidth+1"), 'poziomy przewijak siatki'
        if motyw == 'ciemny': assert k['sob'] == 'rgb(61, 27, 42)' and k['rez'] == 'rgb(61, 27, 42)' and k['gbt'] == 'rgb(255, 106, 19)', k
        else: assert '255, 111, 174' in k['sob'] and '255, 111, 174' in k['rez'], k
        assert k['gbt'] not in ('rgba(0, 0, 0, 0)', None), k
        pg.screenshot(path=os.path.join(ZRZ, '1811c_grafik_%s_%d.png' % (motyw, vw)))
        pg.evaluate("document.querySelector('.gk.gn.sob').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ZRZ, '1811c_sobota_%s_%d.png' % (motyw, vw)))
        if motyw == 'ciemny' and tel:
            # okno zlecenia na grafiku: powiazanie z oferta -> podglad + Podgląd i poprawka oferty
            kf = pg.locator('.kf[data-id="k1"]').first; kf.scroll_into_view_if_needed(); kf.tap(); pg.wait_for_timeout(600)
            if pg.locator('#fQ').count() == 0: kf.dblclick(); pg.wait_for_timeout(600)
            assert pg.locator('#fQ').count() == 1, 'okno zlecenia nie otwarte'
            pg.fill('#fQ', 'Puławska'); pg.wait_for_timeout(400); pg.locator('#fQw .of').first.tap(); pg.wait_for_timeout(400)
            href = pg.locator('.of-pg-e').get_attribute('href'); assert href == '/analizator.html#oferta=MOCK0', href
            assert pg.locator('.of-pg-b button[data-g=ofpdf]').count() == 1
            pg.screenshot(path=os.path.join(ZRZ, '1811c_okno_oferta_390.png'))
            pg.locator('[data-zam]').first.tap(); pg.wait_for_timeout(400)
            # karta zapytania: Edytuj ofertę zamiast PDF
            pg.click('.tabs button[data-v=lista]'); pg.wait_for_timeout(500)
            pg.locator('.lista .karta', has_text='Wróblewska').first.tap(); pg.wait_for_timeout(600)
            print('karta:', pg.locator('.hd h2').first.inner_text(), pg.locator('.akcje').first.inner_text().replace(chr(10),' | '))
            a = pg.locator('.akcje a.of-ed'); assert a.count() == 1 and a.get_attribute('href') == '/analizator.html#oferta=MOCK0'
            assert pg.locator('.akcje button[data-act=pdf]').count() == 0
            assert pg.locator('.linki button[data-act=pdf]').count() == 1
            pg.screenshot(path=os.path.join(ZRZ, '1811c_karta_390.png'))
            a.tap(); pg.wait_for_timeout(1200); assert 'oferta=MOCK0' in pg.url, pg.url
        if motyw == 'ciemny' and tel:
            # 16:35: klawisz Do Grafika w analizatorze -> /aplikacja/#dograf=...
            import urllib.parse
            d = json.dumps({'tel': '512 384 207', 'ul': 'Puławska 182/14', 'kl': 'Katarzyna', 'm2': '46', 't': int(time.time() * 1000)})
            pg.goto(APP + '#dograf=' + urllib.parse.quote(d)); pg.wait_for_timeout(2500)
            if pg.locator('#fQ').count() == 0:
                pg.screenshot(path=os.path.join(ZRZ, '1811c_dograf_blad.png')); print('URL', pg.url, pg.locator('#login').is_visible())
            assert pg.locator('#fQ').count() == 1, 'brak okna zlecenia po dograf'
            assert 'Wróblewska' in pg.locator('.of-z').inner_text(), pg.locator('#fQw').inner_text()
            assert pg.locator('#fA').input_value() == 'PUŁAWSKA 182' and pg.locator('#fMi').input_value() == '14'
            assert 'dograf' not in pg.url
            pg.screenshot(path=os.path.join(ZRZ, '1811c_dograf_390.png'))
            pg.select_option('#fB', index=1); pg.locator('.akc-z').tap(); pg.wait_for_timeout(1200)
            gr = json.loads(urllib.request.urlopen(BASE + '/mock/stan').read())['grafik']
            assert any(v.get('zid') == 'a_MOCKARKUSZ00' + 'x' * 14 for v in gr.values()), gr
            # nieznany telefon -> po czasie zlecenie bez powiazania z polami z analizatora (skrocony test: tylko start)
        br.close()
print('BLEDY:', bledy); assert not bledy
print('OK')
