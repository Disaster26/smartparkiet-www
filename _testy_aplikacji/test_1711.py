"""17.11: soboty w grafiku (mniejsze, przekreslone, 'rezerwa') + status 'Wycena gotowa' niebieski."""
import os, sys, json, threading, urllib.request, time
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
TU = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TU)
import mock_serwer as M
import kafnav  # 19.11: nawigacja przez ekran z kafelkami
ZRZ = os.path.join(TU, 'zrzuty'); os.makedirs(ZRZ, exist_ok=True)
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]; bledy = []
def post(path, d=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(d or {}).encode(), method='POST'); return json.loads(urllib.request.urlopen(r).read())
with sync_playwright() as p:
    for w, h, mob in ((390, 844, True), (1440, 900, False)):
        post('/mock/reset')
        b = p.chromium.launch(channel='msedge')
        ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=mob, is_mobile=mob, device_scale_factor=2 if mob else 1)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: bledy.append('%d: %s' % (w, e)))
        pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1');localStorage.setItem('spk-motyw','ciemny')}catch(e){}")
        pg.goto(BASE + '/aplikacja/'); pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn')
        pg.wait_for_selector('#login', state='hidden'); pg.wait_for_timeout(800)
        nav = ('.tabs' if mob else '.side') + ' button[data-v=%s]'
        pg.click(nav % 'graf'); pg.wait_for_timeout(700)
        r = pg.evaluate("""()=>{var s=[...document.querySelectorAll('.gk.sob:not(.gn)')],n=[...document.querySelectorAll('.gk.gn.sob')],z=[...document.querySelectorAll('.gk:not(.sob):not(.gn):not(.gsp)')];
          var e=s.find(x=>!x.children.length);return {sob:s.length,h:e?e.getBoundingClientRect().height:0,hz:z[0].getBoundingClientRect().height,
          bg:e?getComputedStyle(e).backgroundImage.slice(0,30):'',aft:e?getComputedStyle(e,'::after').content:'',rez:n.filter(x=>/rezerwa/.test(x.textContent)).length,nn:n.length}}""")
        print(w, r)
        assert r['sob'] >= 4 and r['h'] < r['hz'] and 'gradient' in r['bg'] and 'rezerwa' in r['aft'] and r['rez'] > 0, r
        el = pg.locator('.gk.sob').first; el.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ZRZ, '1711_grafik_sob_%d.png' % w))
        n = pg.evaluate("()=>{var X=__spk();return X.D?1:0}") if False else 0
        txt = pg.evaluate("()=>document.documentElement.innerHTML.indexOf('Była rozmowa')")
        pass
        pg.click(nav % 'lista'); pg.wait_for_timeout(500); pg.locator('.karta').first.click(); pg.wait_for_timeout(600)
        assert pg.get_by_text('Wycena gotowa').count() > 0
        pg.screenshot(path=os.path.join(ZRZ, '1711_status_%d.png' % w))
        b.close()
print('BLEDY:', bledy); assert not bledy
print('OK')
