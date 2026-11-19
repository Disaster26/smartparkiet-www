"""18.11 Artur WA 22:23: poprawiona oferta z analizatora (nowa pozycja w Rejestrze) ma zmieniac kwote/m2/link na karcie, na ktorej sie pracuje (np. Zatwierdzone);
nowsza luzna wersja nie stoi jako osobny kafelek. APP_URL=/sciezka/ opcjonalnie."""
import os, sys, json, threading, urllib.request, time
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
TU = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TU)
import mock_serwer as M
srv = ThreadingHTTPServer(('127.0.0.1', 0), M.H); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]; APP = BASE + (os.environ.get('APP_URL') or '/aplikacja/'); bledy = []
def post(path, d=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(d or {}).encode(), method='POST'); return json.loads(urllib.request.urlopen(r).read())
post('/mock/reset')
r0 = M.rejestr_poczatkowy()[0]
M.DB['status'][r0['id']] = {'st': 'zatw', 'nt': '', 'dz': None, 'g': '', 'widz': True, 'hist': []}
nowy = post('/mock/nowa', {'kl': r0['kl'], 'ul': r0['ul'], 'tel': r0['tel'], 'typ': 'a', 'kwota': 4310, 'm2': 23, 'analizator': 'https://smartparkiet.com.pl/analizator.html#oferta=NOWA123', 'ts': r0['ts'] + 3600000})['id']
with sync_playwright() as p:
    br = p.chromium.launch(channel='msedge'); pg = br.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    pg.on('pageerror', lambda e: bledy.append(str(e)))
    pg.add_init_script("try{localStorage.setItem('spk-katalog-przew','1')}catch(e){}")
    pg.goto(APP + '?motyw=ciemny'); pg.fill('#haslo', 'test-haslo-123'); pg.click('#loginBtn'); pg.wait_for_selector('#login', state='hidden'); pg.wait_for_timeout(1200)
    w = pg.evaluate("""(a)=>{const X=window.__spk&&window.__spk();const D=X.D;const it=D.items.find(i=>i.id===a[0]);
       const html=document.body.innerHTML;return {st:it&&it.st, n:D.items.filter(i=>i.kl===it.kl).length}}""", [r0['id']])
    print('dane', w)
    pg.click('.tabs button[data-v=lista]'); pg.wait_for_timeout(700)
    tx = pg.evaluate("document.body.innerText")
    print('lista Wroblewska:', [l for l in tx.split(chr(10)) if 'Wr' in l][:4])
    karty = [k for k in pg.evaluate("[...document.querySelectorAll('.zl')].map(e=>e.textContent.replace(/\s/g,' '))") if '4 310' in k or '5 600' in k]
    print('znaczki:', [l for l in tx.split(chr(10)) if 'starsz' in l or 'nowe! mail' in l][:5])
    kt = pg.locator('.karta', has_text=r0['kl'].split()[0]).first.inner_text(); assert 'nowe! mail' not in kt and 'starsza wersja' not in kt, ('mylacy znaczek', kt)
    print('kwoty na ekranie:', karty[:6])
    pg.screenshot(path=os.path.join(TU, 'zrzuty', '1811f_lista.png'))
    assert any('4 310' in l for l in karty), 'brak nowej kwoty na liscie'
    assert not any('5 600' in l for l in karty), 'stara kwota nadal widoczna'
    pg.locator('.karta', has_text=r0['kl'].split()[0]).first.click(); pg.wait_for_timeout(800)
    hrefs = pg.evaluate("[...document.querySelectorAll('a[href*=oferta]')].map(a=>a.getAttribute('href'))")
    kw = pg.evaluate("(document.querySelector('.kw')||{}).textContent||''")
    print('karta:', kw.replace(chr(160),' '), hrefs)
    pg.screenshot(path=os.path.join(TU, 'zrzuty', '1811f_karta.png'))
    assert hrefs and all('NOWA123' in h for h in hrefs), hrefs
    assert '4 310' in kw.replace(chr(160),' ') and '23' in kw, kw
    print('BLEDY:', bledy); assert not bledy
print('OK')
