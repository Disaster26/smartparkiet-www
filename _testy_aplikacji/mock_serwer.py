# -*- coding: utf-8 -*-
"""Lokalny mock backendu katalogu (ten sam kontrakt JSON co ai/katalog.gs) + serwer plikow aplikacji.

  python _testy_aplikacji/mock_serwer.py [port]       ->  http://127.0.0.1:<port>/aplikacja/
  haslo: test-haslo-123 (zmienna MOCK_HASLO)

POST /api               akcje katalog_* (text/plain JSON, jak Apps Script)
POST /mock/awaria       {"on": true}  -> kolejne katalog_zapisz koncza sie bledem HTTP 500 (test cofania zmian)
POST /mock/nowa         dopisuje nowa wycene do "Rejestru" (jak wycena ze strony)
POST /mock/reset        stan poczatkowy
GET  /mock/stan         podglad stanu (testy)
"""
import json, os, re, sys, threading, uuid, time, datetime, hashlib
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

KORZEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HASLO = os.environ.get('MOCK_HASLO', 'test-haslo-123')
LOCK = threading.Lock()
ST_ZAP = ['luzne', 'rozmowa', 'ogledziny', 'termin', 'wtoku', 'zrobione', 'odpadlo']
BRYGADY = [{'id': 'b1', 'n': 'JARO.2'}, {'id': 'b2', 'n': 'JAREK'}, {'id': 'b3', 'n': 'MACIEK'}]
STATUSY = [{'id': 'ok', 'n': 'Potwierdzone', 'c': '#2E9E3A'}, {'id': 'mysli', 'n': 'Zastanawia się', 'c': '#FF8A00'},
           {'id': 'wst', 'n': 'Wstępnie', 'c': '#FFD60A'}, {'id': 'ogl', 'n': 'Oględziny / pomiar', 'c': '#A8D8F5'},
           {'id': 'term', 'n': 'Termin do potwierdzenia', 'c': '#1E63D6'}, {'id': 'pilne', 'n': 'Pilne', 'c': '#E0262B'},
           {'id': 'awaria', 'n': 'Awaria', 'c': '#6B2A5E'}, {'id': 'gotowe', 'n': 'Zrobione', 'c': '#B6FF1A'}, {'id': 'inne', 'n': 'Inne', 'c': '#FF6FAE'}]


def ts(dni, h, m):
    d = datetime.datetime.now().replace(hour=h, minute=m, second=0, microsecond=0) - datetime.timedelta(days=dni)
    return int(d.timestamp() * 1000)


def rejestr_poczatkowy():
    R = [  # dni temu, godz, klient, tel, adres, m2, kwota, zrodlo, zakres, info, nr
        (0, 9, 41, 'Katarzyna Wróblewska', '512 384 207', 'Puławska 182/14, Warszawa', 46, 5600, 'a', ['listwy'], '3 piętro, winda: tak', ''),
        (0, 8, 12, 'Paweł Michalak', '601 227 945', 'Dereniowa 9/33, Warszawa', 38, 4860, 'k', [], 'preferowane terminy: 2026-11-24', 'SMART/2026/1113/001'),
        (1, 21, 7, 'Joanna Lis', '693 118 402', 'Górczewska 64/2, Warszawa', 27, 2565, 'w', [], '', ''),
        (1, 14, 30, 'Marek Jankowski', '508 640 913', 'Bajana 17/5, Warszawa', 62, 8950, 'a', ['listwy'], 'parter', ''),
        (2, 11, 5, 'Agnieszka Ostrowska', '664 905 318', 'Mickiewicza 27/40, Warszawa', 54, 8100, 'a', [], '', ''),
        (2, 19, 48, 'Tomasz Zieliński', '733 052 671', 'Grochowska 301/8, Warszawa', 41, 5970, 'w', ['listwy'], '', ''),
        (3, 7, 55, 'Magdalena Dudek', '602 771 436', 'Sarmacka 12/101, Warszawa', 33, 3930, 'k', [], 'piętro 2, winda: tak', 'SMART/2026/1110/002'),
        (3, 16, 20, 'Krzysztof Baran', '516 309 822', 'Grójecka 120/7, Warszawa', 58, 6550, 'a', [], '', ''),
        (5, 10, 2, 'Michał Sobczak', '605 812 590', 'Marywilska 44/3, Warszawa', 71, 11460, 'a', ['schody', 'listwy'], '', ''),
        (6, 13, 37, 'Aleksandra Kubiak', '698 230 714', 'Hoża 51/18, Warszawa', 63, 9810, 'k', [], 'kamienica, 3 piętro bez windy', 'SMART/2026/1107/001'),
        (9, 12, 0, 'Grzegorz Adamczyk', '603 455 128', 'Lipowa 7, Ząbki', 22, 6010, 'a', ['schody'], '', ''),
        (12, 8, 48, 'Wojciech Głowacki', '509 731 664', 'Chełmżyńska 80, Warszawa', 47, 6020, 'w', [], 'dom z lat 30.', ''),
    ]
    out = []
    for i, r in enumerate(R):
        d = datetime.datetime.fromtimestamp(ts(r[0], r[1], r[2]) / 1000)
        out.append({'id': 'a_MOCKARKUSZ%02d%s' % (i, 'x' * 14), 'typ': r[8], 'ts': ts(r[0], r[1], r[2]), 'kiedy': d.strftime('%Y-%m-%d %H-%M'),
                    'nr': r[11], 'kl': r[3], 'tel': r[4], 'ul': r[5], 'ds': '', 'em': '', 'm2': r[6], 'kwota': r[7], 'upust': 0,
                    'termin': '', 'arkusz': 'https://docs.google.com/spreadsheets/d/MOCKARKUSZ%02d/edit' % i,
                    'analizator': 'https://smartparkiet.com.pl/analizator.html#oferta=MOCK%d' % i if r[8] == 'a' else '',
                    'zakres': r[9], 'info': r[10]})
    return out


def stan_poczatkowy():
    pn = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    d = lambda n: (pn + datetime.timedelta(days=n)).isoformat()
    K = [('LIPOWA 7 ZĄBKI', '', '60', 'WARSTWA + SCHODY', '604 218 377', 'ok', 'b1', 0, 2),
         ('OGRODOWA 21', '4', '38', 'WOLA, MOZAIKA', '512 660 943', 'mysli', 'b1', 2, 1),
         ('POLNA 5 PIASECZNO', '', '52', 'KLEPKA, LAKIER 3X', '601 739 208', 'ok', 'b2', 0, 1),
         ('SŁONECZNA 9 MARKI', '', '70', 'JODEŁKA + LISTWY', '730 245 816', 'term', 'b2', 1, 2),
         ('BRZOZOWA 18 KONSTANCIN', '', '120', 'MOZAIKA + STABILIZACJA', '608 553 761', 'ok', 'b3', 0, 3),
         ('KLONOWA 8 WOŁOMIN', '', '55', 'WARSTWA', '609 842 377', 'mysli', '', None, 1)]
    graf = {}
    for i, k in enumerate(K):
        graf['k%d' % (i + 1)] = {'ul': k[0], 'mies': k[1], 'm2': k[2], 'info': k[3], 'tel': k[4], 'kol': k[5], 'c': '', 'br': k[6],
                                 'od': d(k[7]) if k[7] is not None else None, 'dni': k[8], 'zid': None}
    return {'rejestr': rejestr_poczatkowy(), 'status': {}, 'sprawy': {'w1': {'dz': d(1), 'g': '11:30', 'x': 'Dentysta', 'prv': True}},
            'grafik': graf, 'ust': {}, 'rev': 0, 'tokeny': {}, 'awaria': False, 'bledy': 0, 'zapisy': 0}


DB = stan_poczatkowy()


def txt(v, n):
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', '' if v is None else str(v))[:n]


def dzien(v):
    return v if isinstance(v, str) and re.match(r'^\d{4}-\d{2}-\d{2}$', v) else None


def godz(v):
    return v if isinstance(v, str) and re.match(r'^\d{1,2}:\d{2}$', v) else ''


def liczba(v):
    try:
        return float(str(v).replace(',', '.'))
    except Exception:
        return 0


def czysc_zap(d, reczne):
    o = {'st': d.get('st') if d.get('st') in ST_ZAP else 'luzne', 'nt': txt(d.get('nt'), 4000), 'dz': dzien(d.get('dz')), 'g': godz(d.get('g')),
         'widz': bool(d.get('widz')), 'hist': [{'ts': int(x.get('ts') or 0), 'x': txt(x.get('x'), 200)} for x in (d.get('hist') or [])[-60:] if isinstance(x, dict)]}
    if reczne:
        o.update({'reczne': True, 'typ': 'r', 'ts': int(d.get('ts') or time.time() * 1000), 'nr': txt(d.get('nr'), 30), 'kl': txt(d.get('kl'), 120),
                  'tel': txt(d.get('tel'), 40), 'ul': txt(d.get('ul'), 200), 'ds': txt(d.get('ds'), 60), 'em': txt(d.get('em'), 120),
                  'm2': liczba(d.get('m2')), 'kwota': 0, 'zakres': [], 'info': txt(d.get('info'), 300)})
    return o


def czysc_kaf(d):
    return {'ul': txt(d.get('ul'), 160).upper(), 'mies': txt(d.get('mies'), 20).upper(), 'm2': txt(d.get('m2'), 10), 'info': txt(d.get('info'), 200).upper(),
            'tel': txt(d.get('tel'), 40), 'kol': txt(d.get('kol'), 40), 'c': d.get('c') if re.match(r'^#[0-9A-Fa-f]{6}$', str(d.get('c') or '')) else '',
            'br': txt(d.get('br'), 40), 'od': dzien(d.get('od')), 'dni': min(30, max(1, int(round(liczba(d.get('dni')) or 1)))), 'zid': txt(d.get('zid'), 80) if d.get('zid') else None}


def stan():
    items = []
    st = dict(DB['status'])
    for r in DB['rejestr']:
        it = dict(r, st='luzne', nt='', dz=None, g='', widz=False, hist=[])
        o = st.pop(r['id'], None)
        if o:
            for k in ('st', 'nt', 'dz', 'g', 'widz', 'hist'):
                if k in o:
                    it[k] = o[k]
        items.append(it)
    for i, o in st.items():
        if o.get('reczne'):
            items.append(dict(o, id=i))
    return {'ok': True, 'wersja': 'mock', 'rev': DB['rev'], 'czas': int(time.time() * 1000), 'items': items,
            'wpisy': [dict(v, id=k) for k, v in DB['sprawy'].items()],
            'graf': {'v': 2, 'br': DB['ust'].get('brygady', BRYGADY), 'kol': DB['ust'].get('statusy', STATUSY),
                     'k': [dict(v, id=k) for k, v in DB['grafik'].items()]}}


def obsluz(d):
    a = str(d.get('akcja') or '')
    if a == 'katalog_ping':
        return {'ok': True, 'wersja': 'mock'}
    if a == 'katalog_login':
        if DB['bledy'] >= 8:
            return {'ok': False, 'blad': 'Za dużo prób. Spróbuj za 15 minut.'}
        if d.get('haslo') != HASLO:
            DB['bledy'] += 1
            return {'ok': False, 'blad': 'Złe hasło'}
        t = uuid.uuid4().hex + uuid.uuid4().hex
        DB['tokeny'][hashlib.sha256(t.encode()).hexdigest()] = time.time() + 180 * 86400
        return {'ok': True, 'token': t}
    t = str(d.get('token') or '')
    if DB['tokeny'].get(hashlib.sha256(t.encode()).hexdigest(), 0) < time.time():
        return {'ok': False, 'kod': 'auth', 'blad': 'Sesja wygasła. Zaloguj się ponownie.'}
    if a == 'katalog_stan':
        return stan()
    if a == 'katalog_wyloguj':
        DB['tokeny'].pop(hashlib.sha256(t.encode()).hexdigest(), None)
        return {'ok': True}
    if a == 'katalog_pdf':
        i = str(d.get('id') or '')
        if not i.startswith('a_'):
            return {'ok': False, 'blad': 'Brak PDF dla tego zapytania'}
        return {'ok': True, 'url': 'https://drive.google.com/file/d/MOCKPDF/view', 'nazwa': 'mock.pdf'}
    if a == 'katalog_zapisz':
        ops = d.get('ops')
        if not isinstance(ops, list) or len(ops) > 200:
            return {'ok': False, 'blad': 'Złe zmiany'}
        for op in ops:
            if op.get('t') == 'ust':
                DB['ust']['brygady'] = [{'id': txt(b.get('id'), 40), 'n': txt(b.get('n'), 24)} for b in op['d']['br']]
                DB['ust']['statusy'] = [{'id': txt(c.get('id'), 40), 'n': txt(c.get('n'), 30), 'c': c.get('c')} for c in op['d']['kol']]
                continue
            i = str(op.get('id') or '')
            if not re.match(r'^[A-Za-z0-9_.:-]{1,80}$', i):
                return {'ok': False, 'blad': 'Złe ID'}
            v = op.get('d')
            if op['t'] == 'zap':
                if v is None:
                    if i.startswith('r'):
                        DB['status'].pop(i, None)
                    continue
                DB['status'][i] = czysc_zap(v, bool(v.get('reczne')) or i.startswith('r'))
            elif op['t'] == 'wpis':
                if v is None:
                    DB['sprawy'].pop(i, None)
                else:
                    DB['sprawy'][i] = {'dz': dzien(v.get('dz')) or datetime.date.today().isoformat(), 'g': godz(v.get('g')), 'x': txt(v.get('x'), 200), 'prv': bool(v.get('prv'))}
            elif op['t'] == 'kaf':
                if v is None:
                    DB['grafik'].pop(i, None)
                else:
                    DB['grafik'][i] = czysc_kaf(v)
            else:
                return {'ok': False, 'blad': 'Nieznana zmiana'}
        DB['rev'] += 1
        DB['zapisy'] += 1
        return stan()
    return {'ok': False, 'blad': 'Nieznana akcja'}


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=KORZEN, **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def _json(self, o, kod=200):
        b = json.dumps(o, ensure_ascii=False).encode('utf-8')
        self.send_response(kod)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith('/mock/stan'):
            with LOCK:
                return self._json({k: v for k, v in DB.items() if k != 'tokeny'})
        if self.path in ('/', ''):
            self.send_response(302)
            self.send_header('Location', '/aplikacja/')
            self.end_headers()
            return
        if not (self.path.startswith('/aplikacja/') or self.path == '/aplikacja'):
            self.send_error(404)
            return
        return super().do_GET()

    def do_POST(self):
        global DB
        n = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(n).decode('utf-8') if n else '{}'
        try:
            d = json.loads(raw or '{}')
        except Exception:
            return self._json({'ok': False, 'blad': 'zły JSON'})
        with LOCK:
            if self.path == '/mock/awaria':
                DB['awaria'] = bool(d.get('on'))
                return self._json({'ok': True})
            if self.path == '/mock/reset':
                DB = stan_poczatkowy()
                return self._json({'ok': True})
            if self.path == '/mock/nowa':
                r = rejestr_poczatkowy()[0]
                r.update({'id': 'a_MOCKNOWY%s' % uuid.uuid4().hex[:16], 'ts': int(time.time() * 1000), 'kl': d.get('kl', 'Nowy Klient'),
                          'tel': '700 000 001', 'typ': 'k', 'nr': 'SMART/2026/1114/009'})
                DB['rejestr'].insert(0, r)
                return self._json({'ok': True, 'id': r['id']})
            if self.path != '/api':
                return self._json({'ok': False}, 404)
            if d.get('akcja') == 'katalog_zapisz' and DB['awaria']:
                return self._json({'ok': False, 'blad': 'awaria testowa'}, 500)
            time.sleep(0.15)  # jak prawdziwy serwer: chwila na odpowiedz
            return self._json(obsluz(d))


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8796
    srv = ThreadingHTTPServer(('127.0.0.1', port), H)
    print('mock: http://127.0.0.1:%d/aplikacja/  haslo: %s' % (srv.server_address[1], HASLO), flush=True)
    srv.serve_forever()
