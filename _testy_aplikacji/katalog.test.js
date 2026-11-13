/* Testy logiki ai/katalog.gs (+ routing w ai/wyceny_dysk.gs) w Node, z atrapami usług Google.
   Uruchomienie: node --test _testy_aplikacji/katalog.test.js */
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');
const eq = (a, b, m) => assert.deepStrictEqual(JSON.parse(JSON.stringify(a)), b, m); /* tablice z kontekstu vm maja inny prototyp */

const AI = path.join(__dirname, '..', 'ai');
const KOD = fs.readFileSync(path.join(AI, 'wyceny_dysk.gs'), 'utf8') + '\n' + fs.readFileSync(path.join(AI, 'katalog.gs'), 'utf8');

/* ---------------- atrapy ---------------- */
function iter(arr) { let i = 0; return { hasNext: () => i < arr.length, next: () => arr[i++] }; }
function rt(text, url) { return { getText: () => text, getLinkUrl: () => url || null }; }

class Range {
  constructor(sh, r, c, nr, nc) { Object.assign(this, { sh, r, c, nr: nr || 1, nc: nc || 1 }); }
  _cells(f) { const out = []; for (let i = 0; i < this.nr; i++) { const row = []; for (let j = 0; j < this.nc; j++) row.push(f(this.r + i, this.c + j)); out.push(row); } return out; }
  getValues() { return this._cells((r, c) => this.sh.get(r, c)); }
  getDisplayValues() { return this._cells((r, c) => { const v = this.sh.get(r, c); return v instanceof Date ? v.toISOString() : String(v == null ? '' : v); }); }
  getRichTextValues() { return this._cells((r, c) => rt(String(this.sh.get(r, c)), this.sh.links[r + ':' + c])); }
  getValue() { return this.sh.get(this.r, this.c); }
  setValue(v) { this.sh.set(this.r, this.c, v); return this; }
  setValues(vs) { vs.forEach((row, i) => row.forEach((v, j) => this.sh.set(this.r + i, this.c + j, v))); return this; }
  setRichTextValue(v) { this.sh.set(this.r, this.c, v.text); this.sh.links[this.r + ':' + this.c] = v.url; return this; }
  setFormula() { return this; }
}
['setFontWeight', 'setBackground', 'setFontColor', 'setNumberFormat'].forEach(m => { Range.prototype[m] = function () { return this; }; });

class Sheet {
  constructor(name) { this.name = name; this.rows = []; this.links = {}; }
  get(r, c) { const row = this.rows[r - 1]; return row && row[c - 1] !== undefined ? row[c - 1] : ''; }
  set(r, c, v) { while (this.rows.length < r) this.rows.push([]); this.rows[r - 1][c - 1] = v; }
  getName() { return this.name; }
  getLastRow() { let n = this.rows.length; while (n > 0 && !this.rows[n - 1].some(v => v !== '' && v != null)) n--; return n; }
  getLastColumn() { return Math.max(0, ...this.rows.map(r => r.length)); }
  getRange(r, c, nr, nc) { return new Range(this, r, c, nr, nc); }
  appendRow(v) { const n = this.getLastRow(); this.rows.splice(n, 0, v.slice()); this.rows.length = Math.max(this.rows.length, n + 1); }
  deleteRow(r) { this.rows.splice(r - 1, 1); const nl = {}; Object.keys(this.links).forEach(k => { const [rr, cc] = k.split(':').map(Number); if (rr < r) nl[k] = this.links[k]; else if (rr > r) nl[(rr - 1) + ':' + cc] = this.links[k]; }); this.links = nl; }
  insertRowAfter(r) { this.rows.splice(r, 0, []); const nl = {}; Object.keys(this.links).forEach(k => { const [rr, cc] = k.split(':').map(Number); nl[(rr > r ? rr + 1 : rr) + ':' + cc] = this.links[k]; }); this.links = nl; }
  setFrozenRows() {}
}
class SS {
  constructor(id, name) { this.id = id; this.name = name; this.sheets = [new Sheet('Arkusz1')]; }
  getId() { return this.id; }
  getSheets() { return this.sheets.slice(); }
  getActiveSheet() { return this.sheets[0]; }
  getSheetByName(n) { return this.sheets.find(s => s.name === n) || null; }
  insertSheet(n, idx) { const s = new Sheet(n); this.sheets.splice(idx == null ? 0 : idx, 0, s); return s; }
}

function swiat() {
  const props = {}, cache = {}, lock = { held: 0, calls: 0 };
  const ss = new SS('SS1', 'Rejestr wycen');
  const files = {};
  const folderMies = { name: '2026-11', pliki: [], getFilesByType: () => iter(folderMies.pliki), getName: () => '2026-11' };
  const rejFile = { getId: () => 'SS1', moveTo() {} };
  const glowny = { getFilesByName: n => iter(n === 'Rejestr wycen' ? [rejFile] : []), getFoldersByName: () => iter([]), createFolder: () => folderMies, addEditor() {} };
  const G = {
    console: { log() {}, error() {} },
    Logger: { log() {} },
    Utilities: {
      DigestAlgorithm: { SHA_256: 'sha256' }, Charset: { UTF_8: 'utf8' },
      computeDigest: (a, s) => Array.from(crypto.createHash('sha256').update(String(s), 'utf8').digest()).map(b => b > 127 ? b - 256 : b),
      getUuid: () => crypto.randomUUID(), sleep() {},
      formatDate: (d, tz, f) => f === 'yyyy-MM-dd' ? d.toISOString().slice(0, 10) : d.toISOString()
    },
    PropertiesService: { getScriptProperties: () => ({
      getProperty: k => (k in props ? props[k] : null), setProperty: (k, v) => { props[k] = String(v); }, deleteProperty: k => { delete props[k]; }, getProperties: () => Object.assign({}, props) }) },
    CacheService: { getScriptCache: () => ({ get: k => (k in cache ? cache[k] : null), put: (k, v) => { cache[k] = String(v); } }) },
    LockService: { getScriptLock: () => ({ tryLock: () => { lock.held++; lock.calls++; return true; }, waitLock: () => { lock.held++; lock.calls++; }, releaseLock: () => { lock.held--; } }) },
    SpreadsheetApp: {
      openById: id => { if (id !== 'SS1') throw new Error('brak'); return ss; }, open: () => ss, create: () => ss, flush() {},
      newRichTextValue: () => { const o = { text: '', url: '' }; return { setText(t) { o.text = t; return this; }, setLinkUrl(u) { o.url = u; return this; }, build: () => o }; }
    },
    DriveApp: {
      getFoldersByName: () => iter([glowny]), createFolder: () => glowny,
      getFileById: id => files[id] || rejFile
    },
    MimeType: { PDF: 'application/pdf' },
    ContentService: { MimeType: { JSON: 'json' }, createTextOutput: s => ({ s, setMimeType() { return this; }, getContent() { return s; } }) },
    MailApp: { sendEmail() {} }
  };
  vm.createContext(G);
  vm.runInContext(KOD, G, { filename: 'gs.js' });
  return { G, props, cache, lock, ss, files, folderMies };
}

/* przykładowy Rejestr wycen: najnowsze na górze, jak w rejestr() */
function rejestrPrzyklad(w) {
  const sh = w.ss.getSheets()[0];
  sh.rows = [
    ['Data', 'Klient', 'Telefon', 'Adres', 'm²', 'Kwota netto (zł)', 'Termin', 'Arkusz', 'Popraw i wyślij ponownie', 'Nr zamówienia', 'Upust (zł)', 'Renowacja schodów', 'Odświeżenie listew', 'Informacje dodatkowe', 'Źródło'],
    ['2026-11-13 10-15', 'Anna Nowak', '600 100 200', 'Puławska 10/4, Warszawa', 46, 4370, 'grudzień', 'Otwórz arkusz', 'Otwórz w analizatorze', '', '', '', 'TAK', '3 piętro, winda: tak', 'analizator'],
    ['2026-11-12 18-02', 'Piotr Lis', '601 200 300', 'Dereniowa 9, Warszawa', '38,5', 3200, '', 'Otwórz arkusz', '', 'SMART/2026/1112/001', -150, 'TAK', '', '', ''],
    ['2026-11-11 09-00', 'Ewa Zając', '602 300 400', 'Grochowska 301, Warszawa', 27, 2565, '', 'Otwórz arkusz', '', '', '', '', '', '', ''],
    ['2026-10-22 15-35', '', '603 000 111', 'Stara 1', '', '', '', 'https://docs.google.com/spreadsheets/d/STARYxxxxxxxxxxxxxxxxxxxx/edit', '', '', '', '', '', '', '']
  ];
  sh.links['2:8'] = 'https://docs.google.com/spreadsheets/d/ARKUSZ1aaaaaaaaaaaaaaaaaaaa/edit';
  sh.links['2:9'] = 'https://smartparkiet.com.pl/analizator.html#oferta=XYZ';
  sh.links['3:8'] = 'https://docs.google.com/spreadsheets/d/ARKUSZ2bbbbbbbbbbbbbbbbbbbb/edit';
  sh.links['4:8'] = 'https://docs.google.com/spreadsheets/d/ARKUSZ3cccccccccccccccccccc/edit';
}
function zalogowany(haslo) {
  const w = swiat();
  rejestrPrzyklad(w);
  w.props.KATALOG_NOWE_HASLO = haslo || 'Parkiet-2026';
  w.G.katalogUstawHaslo();
  const r = w.G.katalogObsluz({ akcja: 'katalog_login', haslo: haslo || 'Parkiet-2026' });
  assert.ok(r.ok, JSON.stringify(r));
  return { w, token: r.token, K: d => w.G.katalogObsluz(Object.assign({ token: r.token }, d)) };
}

/* ---------------- testy ---------------- */
test('hasło: bez ustawienia logowanie odmawia', () => {
  const w = swiat();
  const r = w.G.katalogObsluz({ akcja: 'katalog_login', haslo: 'cokolwiek' });
  assert.strictEqual(r.ok, false);
  assert.match(r.blad, /nie jest jeszcze ustawione/);
});

test('hasło: katalogUstawHaslo zapisuje tylko skrót i usuwa jawne hasło', () => {
  const w = swiat();
  assert.throws(() => w.G.katalogUstawHaslo(), /KATALOG_NOWE_HASLO/);
  w.props.KATALOG_NOWE_HASLO = 'Parkiet-2026';
  w.G.katalogUstawHaslo();
  assert.ok(!('KATALOG_NOWE_HASLO' in w.props));
  assert.match(w.props.KATALOG_HASLO, /^[a-f0-9]{32}:[a-f0-9]{64}$/);
  assert.ok(w.props.KATALOG_HASLO.indexOf('Parkiet') < 0);
});

test('logowanie: złe hasło, blokada po kilku próbach, dobre hasło daje token', () => {
  const w = swiat();
  w.props.KATALOG_NOWE_HASLO = 'Parkiet-2026'; w.G.katalogUstawHaslo();
  assert.match(w.G.katalogObsluz({ akcja: 'katalog_login', haslo: 'zle' }).blad, /^Złe hasło/);
  const ok = w.G.katalogObsluz({ akcja: 'katalog_login', haslo: 'Parkiet-2026' });
  assert.ok(ok.ok); assert.match(ok.token, /^[a-f0-9]{64}$/);
  /* token przechowywany tylko jako skrót */
  assert.ok(!Object.keys(w.props).some(k => k.indexOf(ok.token) >= 0 || w.props[k].indexOf(ok.token) >= 0));
  for (let i = 0; i < 8; i++) w.G.katalogObsluz({ akcja: 'katalog_login', haslo: 'zle' + i });
  assert.match(w.G.katalogObsluz({ akcja: 'katalog_login', haslo: 'Parkiet-2026' }).blad, /Za dużo (prób|błędnych haseł)/);
});

test('token: bez tokenu, z obcym albo wylogowanym - brak dostępu', () => {
  const { w, token, K } = zalogowany();
  assert.strictEqual(w.G.katalogObsluz({ akcja: 'katalog_stan' }).kod, 'auth');
  assert.strictEqual(w.G.katalogObsluz({ akcja: 'katalog_stan', token: 'a'.repeat(64) }).kod, 'auth');
  assert.ok(K({ akcja: 'katalog_stan' }).ok);
  K({ akcja: 'katalog_wyloguj' });
  assert.strictEqual(w.G.katalogObsluz({ akcja: 'katalog_stan', token }).kod, 'auth');
});

test('token: wygasły nie działa, katalogWylogujWszystkich czyści sesje', () => {
  const { w, token, K } = zalogowany();
  Object.keys(w.props).filter(k => k.indexOf('katTok_') === 0).forEach(k => { w.props[k] = String(Date.now() - 1000); });
  assert.strictEqual(K({ akcja: 'katalog_stan' }).kod, 'auth');
  const t2 = w.G.katalogObsluz({ akcja: 'katalog_login', haslo: 'Parkiet-2026' }).token;
  w.G.katalogWylogujWszystkich();
  assert.strictEqual(w.G.katalogObsluz({ akcja: 'katalog_stan', token: t2 }).kod, 'auth');
  assert.ok(token);
});

test('stan: zapytania z Rejestru wycen, źródła rozpoznane, dane liczbowe', () => {
  const { K } = zalogowany();
  const s = K({ akcja: 'katalog_stan' });
  assert.ok(s.ok, s.blad);
  assert.strictEqual(s.items.length, 4);
  const [a, k, w, stary] = s.items;
  assert.strictEqual(a.id, 'a_ARKUSZ1aaaaaaaaaaaaaaaaaaaa'); assert.strictEqual(a.typ, 'a');
  assert.strictEqual(k.typ, 'k'); assert.strictEqual(k.nr, 'SMART/2026/1112/001'); assert.strictEqual(k.m2, 38.5); eq(k.zakres, ['schody']);
  assert.strictEqual(w.typ, 'w'); assert.strictEqual(a.kwota, 4370); eq(a.zakres, ['listwy']);
  assert.strictEqual(a.analizator, 'https://smartparkiet.com.pl/analizator.html#oferta=XYZ');
  assert.strictEqual(new Date(a.ts).getHours(), 10); assert.strictEqual(new Date(a.ts).getDate(), 13);
  assert.strictEqual(stary.id, 'a_STARYxxxxxxxxxxxxxxxxxxxx'); /* link wpisany tekstem w starych wierszach */
  assert.strictEqual(a.st, 'luzne');
  eq(s.graf.br.map(b => b.n), ['JARO.2', 'JAREK', 'MACIEK', 'PODWYKONAWCA']);
  assert.ok(s.graf.kol.length >= 5);
});

test('zapis: status, notatka, wpis z ręki, sprawa, kafelek, ustawienia - i trwałość', () => {
  const { w, K } = zalogowany();
  const r = K({ akcja: 'katalog_zapisz', ops: [
    { t: 'zap', id: 'a_ARKUSZ1aaaaaaaaaaaaaaaaaaaa', d: { st: 'termin', nt: 'klucze u sąsiada', dz: '2026-11-16', g: '8:00', widz: true, hist: [{ ts: 1, x: 'Status: Termin' }], kl: 'NIE NADPISUJ' } },
    { t: 'zap', id: 'r1700000000000', d: { reczne: true, kl: 'Jan Kowalski', tel: '600 000 000', ul: 'Lipowa 1', ds: 'Wola', m2: '30', st: 'rozmowa', nt: 'dzwonił', hist: [] } },
    { t: 'wpis', id: 'w1', d: { dz: '2026-11-17', g: '11:30', x: 'Dentysta', prv: true } },
    { t: 'wpis', id: 'w2', d: { dz: '2026-11-17', g: '', x: 'klucze u sąsiada', prv: false, br: 'b2' } },
    { t: 'kaf', id: 'k1', d: { ul: 'rycerska 12 radzymin', mies: '', m2: '60', info: 'warstwa + schody', tel: '600', kol: 'ok', c: '#FF6FAE', br: 'b2', od: '2026-11-16', dni: 2, zid: 'a_ARKUSZ1aaaaaaaaaaaaaaaaaaaa' } },
    { t: 'ust', d: { br: [{ id: 'b1', n: 'JARO.2' }, { id: 'b2', n: 'JAREK' }, { id: 'b3', n: 'MACIEK B' }, { id: 'b4', n: 'NOWA' }], kol: [{ id: 'ok', n: 'Potwierdzone', c: '#2E9E3A' }, { id: 'zly', n: 'x', c: 'red' }] } }
  ] });
  assert.ok(r.ok, r.blad);
  assert.strictEqual(w.lock.held, 0); assert.ok(w.lock.calls >= 1);
  /* Rejestr wycen zostaje pierwszym arkuszem */
  eq(w.ss.getSheets().map(s => s.name), ['Arkusz1', 'Katalog_logowania', 'Katalog_status', 'Katalog_sprawy', 'Grafik', 'Ustawienia_katalog']);
  const s = K({ akcja: 'katalog_stan' });
  const a = s.items.find(i => i.id === 'a_ARKUSZ1aaaaaaaaaaaaaaaaaaaa');
  assert.strictEqual(a.st, 'termin'); assert.strictEqual(a.nt, 'klucze u sąsiada'); assert.strictEqual(a.dz, '2026-11-16'); assert.strictEqual(a.kl, 'Anna Nowak');
  const rr = s.items.find(i => i.id === 'r1700000000000');
  assert.strictEqual(rr.typ, 'r'); assert.strictEqual(rr.kl, 'Jan Kowalski'); assert.strictEqual(rr.m2, 30);
  eq(s.wpisy, [{ dz: '2026-11-17', g: '11:30', x: 'Dentysta', prv: true, id: 'w1' }, { dz: '2026-11-17', g: '', x: 'klucze u sąsiada', prv: false, br: 'b2', id: 'w2' }]);
  const k = s.graf.k[0];
  assert.strictEqual(k.ul, 'RYCERSKA 12 RADZYMIN'); assert.strictEqual(k.info, 'WARSTWA + SCHODY'); assert.strictEqual(k.dni, 2); assert.strictEqual(k.c, '#FF6FAE');
  assert.strictEqual(s.graf.br[2].n, 'MACIEK B'); assert.strictEqual(s.graf.br.length, 4);
  assert.strictEqual(s.graf.kol[1].c, '#8A8178'); /* zły kolor zastąpiony */
  assert.strictEqual(s.rev, 1);
  /* czytelny opis w arkuszu Grafik */
  const g = w.ss.getSheetByName('Grafik');
  assert.match(g.get(2, 2), /^JAREK 2026-11-16 \(2 dni\) \| RYCERSKA 12 RADZYMIN \(60\) \/ WARSTWA \+ SCHODY/);
});

test('zapis: aktualizacja i usuwanie rekordów, zapytania z Rejestru nie do usunięcia', () => {
  const { w, K } = zalogowany();
  K({ akcja: 'katalog_zapisz', ops: [{ t: 'kaf', id: 'k1', d: { ul: 'A', br: '', od: null } }, { t: 'kaf', id: 'k2', d: { ul: 'B' } }, { t: 'wpis', id: 'w1', d: { x: 'Poczta', dz: '2026-11-18' } }] });
  K({ akcja: 'katalog_zapisz', ops: [{ t: 'kaf', id: 'k1', d: null }, { t: 'kaf', id: 'k2', d: { ul: 'B2', dni: 99 } }, { t: 'wpis', id: 'w1', d: null }, { t: 'zap', id: 'a_ARKUSZ1aaaaaaaaaaaaaaaaaaaa', d: null }] });
  const s = K({ akcja: 'katalog_stan' });
  eq(s.graf.k.map(k => [k.id, k.ul, k.dni]), [['k2', 'B2', 30]]);
  assert.strictEqual(s.wpisy.length, 0);
  assert.strictEqual(s.items.length, 4);
  assert.strictEqual(w.ss.getSheetByName('Grafik').getLastRow(), 2);
});

test('zapis: złe dane odrzucone, blokada zwolniona', () => {
  const { w, K } = zalogowany();
  assert.strictEqual(K({ akcja: 'katalog_zapisz', ops: [{ t: 'kaf', id: 'zle id!', d: {} }] }).ok, false);
  assert.strictEqual(K({ akcja: 'katalog_zapisz', ops: [{ t: 'nieznane', id: 'x1', d: {} }] }).ok, false);
  assert.strictEqual(K({ akcja: 'katalog_zapisz', ops: [{ t: 'ust', d: { br: [], kol: [] } }] }).ok, false);
  assert.strictEqual(K({ akcja: 'katalog_zapisz', ops: new Array(201).fill({ t: 'wpis', id: 'w', d: {} }) }).ok, false);
  assert.strictEqual(K({ akcja: 'katalog_zapisz', ops: 'nie tablica' }).ok, false);
  assert.strictEqual(w.lock.held, 0);
});

test('PDF: znajduje plik po dacie wyceny w folderze arkusza', () => {
  const { w, K } = zalogowany();
  w.files.ARKUSZ1aaaaaaaaaaaaaaaaaaaa = { getParents: () => iter([w.folderMies]), getUrl: () => 'https://arkusz' };
  w.folderMies.pliki.push({ getName: () => '2026-11-12 18-02 inna.pdf', getUrl: () => 'https://zly' }, { getName: () => '2026-11-13 10-15 Puławska.pdf', getUrl: () => 'https://pdf1' });
  eq(K({ akcja: 'katalog_pdf', id: 'a_ARKUSZ1aaaaaaaaaaaaaaaaaaaa' }), { ok: true, url: 'https://pdf1', nazwa: '2026-11-13 10-15 Puławska.pdf' });
  assert.strictEqual(K({ akcja: 'katalog_pdf', id: 'r123' }).ok, false);
});

test('routing: doPost/doGet przekazują katalog_*, reszta wycen bez zmian', () => {
  const w = swiat();
  const p = w.G.doPost({ postData: { contents: JSON.stringify({ akcja: 'katalog_ping' }) } });
  assert.strictEqual(JSON.parse(p.getContent()).wersja, '2026-11-14');
  assert.strictEqual(JSON.parse(w.G.doGet({ parameter: { akcja: 'katalog_ping' } }).getContent()).ok, true);
  assert.strictEqual(w.G.doGet({ parameter: {} }).getContent(), 'SMARTPARKIET wyceny - dziala');
  assert.strictEqual(JSON.parse(w.G.doGet({ parameter: { a: 'wersja' } }).getContent()).wersja, '2026-11-07');
  assert.strictEqual(JSON.parse(w.G.doPost({ postData: { contents: JSON.stringify({ akcja: 'katalog_stan' }) } }).getContent()).kod, 'auth');
});

test('rejestr(): nowa kolumna O "Źródło" i źródło wyceny z doPost', () => {
  const w = swiat();
  rejestrPrzyklad(w);
  w.G.rejestr({ imie: 'Test', tel: '1', adres: 'X', m2: 10, suma: 100, zrodlo: 'koszyk' }, '2026-11-14 08-00', 'https://docs.google.com/spreadsheets/d/NOWYdddddddddddddddddddddd/edit', '');
  const sh = w.ss.getSheets()[0];
  assert.strictEqual(sh.get(1, 15), 'Źródło'); assert.strictEqual(sh.get(2, 15), 'koszyk'); assert.strictEqual(sh.get(3, 15), 'analizator');
  assert.strictEqual(w.G.katZrodloWyceny({ kopiaArtur: true, zamowienie: true }), 'analizator');
  assert.strictEqual(w.G.katZrodloWyceny({ bezBcc: true }), 'analizator');
  assert.strictEqual(w.G.katZrodloWyceny({ zamowienie: true }), 'koszyk');
  assert.strictEqual(w.G.katZrodloWyceny({}), 'wycena klienta');
});
