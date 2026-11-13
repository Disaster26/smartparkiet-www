/* SMARTPARKIET - KATALOG ZAPYTAŃ i GRAFIK BRYGAD (backend aplikacji smartparkiet.com.pl/aplikacja/)

   Plik dopisany do TEGO SAMEGO projektu Apps Script co wyceny_dysk.gs (osobny plik w edytorze: katalog.gs).
   Wejście: doPost / doGet z wyceny_dysk.gs przekazują tu tylko zapytania z polem akcja = "katalog_*"
   (jedna linijka na początku obu funkcji). Akcje wycen (zapis PDF, szkice, opinie, numer, lista) działają bez zmian.

   Dane:
   - zapytania czytane z pierwszego arkusza "Rejestr wycen" (tam zapisuje każda wycena i zamówienie ze strony),
   - w tym samym pliku osobne zakładki: Katalog_status (statusy, notatki, terminy, wpisy z ręki),
     Katalog_sprawy (sprawy ogólne i prywatne), Grafik (kafelki brygad), Ustawienia_katalog (brygady, statusy).
     Kolumna "Dane" to zapis aplikacji - nie edytować ręcznie (kolumna "Opis" jest do czytania).

   Hasło Artura: tylko skrót (SHA-256 z solą, wielokrotnie) we właściwościach skryptu KATALOG_HASLO.
   Ustawienie: Ustawienia projektu -> Właściwości skryptu -> dodaj KATALOG_NOWE_HASLO = hasło (min. 8 znaków)
   -> w edytorze wybierz funkcję katalogUstawHaslo i Uruchom. Funkcja zapisze skrót i usunie jawne hasło.
   Aplikacja po zalogowaniu dostaje losowy token sesji (ważny 180 dni, na serwerze trzymany tylko jego skrót). */

const KAT_WERSJA = '2026-11-14';
const KAT_ARK = { status: 'Katalog_status', sprawy: 'Katalog_sprawy', grafik: 'Grafik', ust: 'Ustawienia_katalog' };
const KAT_NAGL = ['ID', 'Opis', 'Dane (zapis aplikacji - nie edytować)', 'Zmieniono'];
const KAT_TOKEN_DNI = 180;
const KAT_ITER = 400;          /* powtórzenia skrótu hasła */
const KAT_PROBY = 5;           /* 14.11: co 5 złych haseł blokada rosnąca (KAT_BLOKADY) */
const KAT_BLOKADY = [1, 15, 30, 300]; /* minuty: 1 min, 15 min, 30 min, potem za każdym razem 5 h */
const KAT_RESET_H = 24;        /* doba bez złych prób = licznik od zera */
const KAT_MAX_REJESTR = 800;   /* tyle najnowszych wierszy Rejestru trafia do katalogu */
const KAT_MAX_OPS = 200;
const KAT_ID = /^[A-Za-z0-9_.:-]{1,80}$/;

const KAT_BRYGADY = [{ id: 'b1', n: 'JARO.2' }, { id: 'b2', n: 'JAREK' }, { id: 'b3', n: 'MACIEK' }];
const KAT_STATUSY = [
  { id: 'ok', n: 'Potwierdzone', c: '#2E9E3A' }, { id: 'mysli', n: 'Zastanawia się', c: '#FF8A00' },
  { id: 'wst', n: 'Wstępnie', c: '#FFD60A' }, { id: 'ogl', n: 'Oględziny / pomiar', c: '#A8D8F5' },
  { id: 'term', n: 'Termin do potwierdzenia', c: '#1E63D6' }, { id: 'pilne', n: 'Pilne', c: '#E0262B' },
  { id: 'awaria', n: 'Awaria', c: '#6B2A5E' }, { id: 'gotowe', n: 'Zrobione', c: '#B6FF1A' }, { id: 'inne', n: 'Inne', c: '#FF6FAE' }];
const KAT_ST_ZAP = ['luzne', 'rozmowa', 'ogledziny', 'termin', 'wtoku', 'zrobione', 'odpadlo'];

/* ------------------------------------------------------------------ wejście */
function katalogObsluz(d) {
  try {
    d = d || {};
    const akcja = String(d.akcja || '');
    if (akcja === 'katalog_ping') return { ok: true, wersja: KAT_WERSJA };
    if (akcja === 'katalog_login') return katLogin(d.haslo, d.ua);
    if (!katTokenOk(d.token)) return { ok: false, kod: 'auth', blad: 'Sesja wygasła. Zaloguj się ponownie.' };
    if (akcja === 'katalog_stan') return katStan();
    if (akcja === 'katalog_zapisz') return katZapisz(d.ops);
    if (akcja === 'katalog_pdf') return katPdf(String(d.id || ''));
    if (akcja === 'katalog_wyloguj') { katUsunToken(d.token); return { ok: true }; }
    return { ok: false, blad: 'Nieznana akcja' };
  } catch (e) {
    console.error('katalog: ' + e + (e && e.stack ? '\n' + e.stack : ''));
    return { ok: false, blad: 'Błąd serwera: ' + String((e && e.message) || e) };
  }
}

/* ------------------------------------------------------------------ hasło i sesje */
function katHex(bytes) { return bytes.map(function (b) { return ('0' + (b & 255).toString(16)).slice(-2); }).join(''); }
function katSha(s) { return katHex(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, String(s), Utilities.Charset.UTF_8)); }
function katHashHasla(haslo, sol) {
  let h = katSha(sol + '|' + haslo);
  for (let i = 0; i < KAT_ITER; i++) h = katSha(sol + h);
  return h;
}
/* porównanie bez wczesnego wyjścia */
function katRowne(a, b) {
  a = String(a); b = String(b);
  let r = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i++) r |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return r === 0;
}

/* URUCHOMIĆ RAZ W EDYTORZE po dodaniu właściwości skryptu KATALOG_NOWE_HASLO */
function katalogUstawHaslo() {
  const p = PropertiesService.getScriptProperties();
  const nowe = String(p.getProperty('KATALOG_NOWE_HASLO') || '');
  if (nowe.length < 8) throw new Error('Najpierw dodaj właściwość skryptu KATALOG_NOWE_HASLO z hasłem (min. 8 znaków): Ustawienia projektu -> Właściwości skryptu.');
  const sol = Utilities.getUuid().replace(/-/g, '');
  p.setProperty('KATALOG_HASLO', sol + ':' + katHashHasla(nowe, sol));
  p.deleteProperty('KATALOG_NOWE_HASLO');
  katalogWylogujWszystkich();
  Logger.log('Hasło katalogu ustawione. Jawne hasło usunięte z właściwości, stare sesje wylogowane.');
}

/* awaryjnie: wylogowuje wszystkie telefony i komputery */
function katalogWylogujWszystkich() {
  const p = PropertiesService.getScriptProperties();
  const all = p.getProperties();
  Object.keys(all).forEach(function (k) { if (k.indexOf('katTok_') === 0) p.deleteProperty(k); });
}

function katLogin(haslo, ua) {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(15000)) return { ok: false, blad: 'Serwer zajęty, spróbuj za chwilę.' };
  try {
    const p = PropertiesService.getScriptProperties();
    const teraz = Date.now();
    let b = {};
    try { b = JSON.parse(p.getProperty('KAT_BLOKADA') || '{}') || {}; } catch (e) { b = {}; }
    if (b.ost && teraz - b.ost > KAT_RESET_H * 36e5) b = {};
    if (b.do && b.do > teraz) {
      katLogLogowania('BLOKADA (próba w czasie blokady)', ua);
      return { ok: false, blokada: true, blad: 'Za dużo błędnych haseł. Logowanie zablokowane jeszcze ' + katIleCzasu(b.do - teraz) + '.' };
    }
    const zap = String(p.getProperty('KATALOG_HASLO') || '');
    const i = zap.indexOf(':');
    if (i < 1) return { ok: false, blad: 'Hasło nie jest jeszcze ustawione (katalogUstawHaslo).' };
    const h = String(haslo || '');
    if (!h || h.length > 200 || !katRowne(katHashHasla(h, zap.slice(0, i)), zap.slice(i + 1))) {
      b.n = (b.n || 0) + 1; b.ost = teraz;
      let msg = 'Złe hasło';
      if (b.n >= KAT_PROBY) {
        const min = KAT_BLOKADY[Math.min(b.etap || 0, KAT_BLOKADY.length - 1)];
        b.do = teraz + min * 6e4; b.etap = (b.etap || 0) + 1; b.n = 0;
        msg = 'Złe hasło. Za dużo prób - logowanie zablokowane na ' + katIleCzasu(min * 6e4) + '.';
        katLogLogowania('ZŁE HASŁO -> blokada ' + katIleCzasu(min * 6e4), ua);
      } else {
        msg = 'Złe hasło. Zostało prób przed blokadą: ' + (KAT_PROBY - b.n) + '.';
        katLogLogowania('ZŁE HASŁO', ua);
      }
      p.setProperty('KAT_BLOKADA', JSON.stringify(b));
      Utilities.sleep(700);
      return { ok: false, blad: msg };
    }
    p.deleteProperty('KAT_BLOKADA');
    katSprzatnijTokeny(p);
    const token = Utilities.getUuid().replace(/-/g, '') + Utilities.getUuid().replace(/-/g, '');
    p.setProperty(katKluczTokenu(token), String(teraz + KAT_TOKEN_DNI * 864e5));
    katLogLogowania('OK - zalogowano', ua);
    return { ok: true, token: token };
  } finally {
    lock.releaseLock();
  }
}
function katIleCzasu(ms) {
  const m = Math.ceil(ms / 6e4);
  if (m < 60) return m + ' min';
  const g = Math.floor(m / 60), r = m % 60;
  return g + ' h' + (r ? ' ' + r + ' min' : '');
}
/* dziennik logowań: zakładka Katalog_logowania (data, wynik, urządzenie) - widać, czy ktoś obcy próbuje */
function katLogLogowania(wynik, ua) {
  try {
    const sh = katArkusz(katSS(), 'Katalog_logowania', ['Data', 'Wynik', 'Urządzenie (z przeglądarki)']);
    sh.appendRow([Utilities.formatDate(new Date(), 'Europe/Warsaw', 'yyyy-MM-dd HH:mm:ss'), wynik, katUrz(ua)]);
    const n = sh.getLastRow();
    if (n > 1001) sh.deleteRows(2, n - 1001);
  } catch (e) { console.error('log logowania: ' + e); }
}
function katUrz(ua) {
  ua = String(ua || '').slice(0, 300);
  if (!ua) return '?';
  const sys = /iPhone/.test(ua) ? 'iPhone' : /iPad/.test(ua) ? 'iPad' : /Android/.test(ua) ? 'Android' : /Windows/.test(ua) ? 'Windows' : /Mac OS X/.test(ua) ? 'Mac' : /Linux/.test(ua) ? 'Linux' : 'inne';
  const prz = /Edg\//.test(ua) ? 'Edge' : /OPR\//.test(ua) ? 'Opera' : /CriOS|Chrome\//.test(ua) ? 'Chrome' : /FxiOS|Firefox\//.test(ua) ? 'Firefox' : /Safari\//.test(ua) ? 'Safari' : 'inna';
  return sys + ' / ' + prz + ' | ' + ua.slice(0, 160);
}
/* URUCHOMIĆ W EDYTORZE, gdy Artur sam się zablokował: zeruje licznik złych haseł */
function katalogOdblokuj() {
  PropertiesService.getScriptProperties().deleteProperty('KAT_BLOKADA');
  Logger.log('Blokada logowania zdjęta.');
}
/* podgląd: ile aktywnych sesji (zalogowanych urządzeń) i stan blokady */
function katalogStanBezpieczenstwa() {
  const all = PropertiesService.getScriptProperties().getProperties(), t = Date.now();
  const sesje = Object.keys(all).filter(function (k) { return k.indexOf('katTok_') === 0 && Number(all[k]) > t; }).length;
  Logger.log('Aktywne sesje: ' + sesje + ' | blokada: ' + (all.KAT_BLOKADA || 'brak'));
}
function katKluczTokenu(t) { return 'katTok_' + katSha('tok|' + t).slice(0, 40); }
function katTokenOk(t) {
  t = String(t || '');
  if (!/^[a-f0-9]{64}$/.test(t)) return false;
  const v = PropertiesService.getScriptProperties().getProperty(katKluczTokenu(t));
  return !!v && Number(v) > Date.now();
}
function katUsunToken(t) { if (/^[a-f0-9]{64}$/.test(String(t || ''))) PropertiesService.getScriptProperties().deleteProperty(katKluczTokenu(String(t))); }
function katSprzatnijTokeny(p) {
  const all = p.getProperties(), teraz = Date.now();
  const tok = Object.keys(all).filter(function (k) { return k.indexOf('katTok_') === 0; });
  tok.forEach(function (k) { if (Number(all[k]) <= teraz) p.deleteProperty(k); });
  /* najwyżej 30 aktywnych sesji - najstarsze wylatują */
  const zywe = tok.filter(function (k) { return Number(all[k]) > teraz; }).sort(function (a, b) { return Number(all[a]) - Number(all[b]); });
  while (zywe.length >= 30) p.deleteProperty(zywe.shift());
}

/* ------------------------------------------------------------------ arkusze */
function katSS() {
  const p = PropertiesService.getScriptProperties();
  const id = p.getProperty('KATALOG_SS_ID');
  if (id) { try { return SpreadsheetApp.openById(id); } catch (e) { p.deleteProperty('KATALOG_SS_ID'); } }
  const g = glownyFolder();
  const it = g.getFilesByName('Rejestr wycen');
  let ss;
  if (it.hasNext()) ss = SpreadsheetApp.open(it.next());
  else {
    /* ten sam nagłówek co w rejestr() z wyceny_dysk.gs - kolejne wyceny dopiszą się normalnie */
    ss = SpreadsheetApp.create('Rejestr wycen');
    ss.getActiveSheet().getRange(1, 1, 1, 8)
      .setValues([['Data', 'Klient', 'Telefon', 'Adres', 'm²', 'Kwota netto (zł)', 'Termin', 'Arkusz']])
      .setFontWeight('bold').setBackground('#FE6500').setFontColor('#FFFFFF');
    ss.getActiveSheet().setFrozenRows(1);
    DriveApp.getFileById(ss.getId()).moveTo(g);
  }
  p.setProperty('KATALOG_SS_ID', ss.getId());
  return ss;
}
/* nowa zakładka zawsze NA KOŃCU - Rejestr wycen musi zostać pierwszym arkuszem (rejestr() pisze do getSheets()[0]) */
function katArkusz(ss, nazwa, nagl) {
  let sh = ss.getSheetByName(nazwa);
  if (!sh) {
    sh = ss.insertSheet(nazwa, ss.getSheets().length);
    sh.getRange(1, 1, 1, nagl.length).setValues([nagl]).setFontWeight('bold').setBackground('#14110E').setFontColor('#FFFFFF');
    sh.setFrozenRows(1);
  }
  return sh;
}
function katArkusze(ss) {
  return {
    status: katArkusz(ss, KAT_ARK.status, KAT_NAGL),
    sprawy: katArkusz(ss, KAT_ARK.sprawy, KAT_NAGL),
    grafik: katArkusz(ss, KAT_ARK.grafik, KAT_NAGL),
    ust: katArkusz(ss, KAT_ARK.ust, ['Klucz', 'Wartość (zapis aplikacji)', 'Zmieniono'])
  };
}
function katCzytaj(sh) {
  const n = sh.getLastRow(), o = {};
  if (n < 2) return o;
  sh.getRange(2, 1, n - 1, 3).getValues().forEach(function (r, i) {
    const id = String(r[0] || '');
    if (!id) return;
    try { o[id] = { d: JSON.parse(r[2]), wiersz: i + 2 }; } catch (e) { /* uszkodzony wiersz pomijamy */ }
  });
  return o;
}
function katZapiszRekordy(sh, zmiany) {
  if (!zmiany.length) return;
  const mapa = katCzytaj(sh), usun = [], teraz = new Date();
  zmiany.forEach(function (z) {
    const w = mapa[z.id];
    if (z.d === null) { if (w && usun.indexOf(w.wiersz) < 0) usun.push(w.wiersz); delete mapa[z.id]; return; }
    const wiersz = [z.id, String(z.opis || '').slice(0, 300), JSON.stringify(z.d), teraz];
    if (w) sh.getRange(w.wiersz, 1, 1, 4).setValues([wiersz]);
    else { sh.appendRow(wiersz); mapa[z.id] = { d: z.d, wiersz: sh.getLastRow() }; }
  });
  usun.sort(function (a, b) { return b - a; }).forEach(function (r) { sh.deleteRow(r); });
}
function katUstCzytaj(sh) {
  const n = sh.getLastRow(), o = {};
  if (n < 2) return o;
  sh.getRange(2, 1, n - 1, 2).getValues().forEach(function (r) { if (r[0]) try { o[String(r[0])] = JSON.parse(r[1]); } catch (e) {} });
  return o;
}
function katUstZapisz(sh, klucz, wartosc) {
  const n = sh.getLastRow();
  const v = n >= 2 ? sh.getRange(2, 1, n - 1, 1).getValues() : [];
  for (let i = 0; i < v.length; i++) if (String(v[i][0]) === klucz) { sh.getRange(i + 2, 2, 1, 2).setValues([[JSON.stringify(wartosc), new Date()]]); return; }
  sh.appendRow([klucz, JSON.stringify(wartosc), new Date()]);
}

/* ------------------------------------------------------------------ Rejestr wycen -> zapytania */
function katData(v, txt) {
  if (Object.prototype.toString.call(v) === '[object Date]' && !isNaN(v)) return v.getTime();
  const s = String(txt || v || '');
  let m = s.match(/(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{1,2})[-:.](\d{2}))?/);
  if (m) return new Date(+m[1], +m[2] - 1, +m[3], +(m[4] || 0), +(m[5] || 0)).getTime();
  m = s.match(/(\d{1,2})\.(\d{1,2})\.(\d{4})(?:[ ,]+(\d{1,2}):(\d{2}))?/);
  return m ? new Date(+m[3], +m[2] - 1, +m[1], +(m[4] || 0), +(m[5] || 0)).getTime() : 0;
}
function katLiczba(v) { const n = parseFloat(String(v == null ? '' : v).replace(/\s/g, '').replace(',', '.')); return isFinite(n) ? n : 0; }
/* źródło: kolumna O "Źródło" (od 14.11); starsze wiersze - z numeru zamówienia (koszyk) albo wycena klienta */
function katTyp(zrodlo, nrZam) {
  const z = String(zrodlo || '').toLowerCase();
  if (/analiz|parkieciar/.test(z)) return 'a';
  if (/koszyk|zam/.test(z)) return 'k';
  if (/wycen|klient|stron/.test(z)) return 'w';
  return String(nrZam || '').trim() ? 'k' : 'w';
}
function katZapytania(ss) {
  const sh = ss.getSheets()[0];
  const n = sh.getLastRow();
  if (n < 2) return [];
  const ile = Math.min(n - 1, KAT_MAX_REJESTR);
  const rng = sh.getRange(2, 1, ile, 15);
  const v = rng.getValues(), dv = rng.getDisplayValues(), rt = sh.getRange(2, 8, ile, 2).getRichTextValues();
  const out = [], byly = {};
  for (let i = 0; i < ile; i++) {
    const r = dv[i];
    if (!r[0] && !r[1] && !r[2] && !r[3]) continue;
    const ark = (rt[i][0] && rt[i][0].getLinkUrl()) || (/^https?:/.test(r[7]) ? r[7] : '');
    const anal = (rt[i][1] && rt[i][1].getLinkUrl()) || '';
    const m = String(ark).match(/\/d\/([\w-]{20,})/);
    let id = m ? 'a_' + m[1] : 'h_' + katSha([r[0], r[1], r[2], r[3], r[5]].join('|')).slice(0, 20);
    if (byly[id]) id += '_' + i;
    byly[id] = 1;
    const zakres = [];
    if (/tak/i.test(r[11])) zakres.push('schody');
    if (/tak/i.test(r[12])) zakres.push('listwy');
    out.push({
      id: id, typ: katTyp(r[14], r[9]), ts: katData(v[i][0], r[0]), kiedy: r[0], nr: r[9] || '',
      kl: r[1] || '', tel: r[2] || '', ul: r[3] || '', ds: '', em: '',
      m2: katLiczba(v[i][4]), kwota: katLiczba(v[i][5]), upust: katLiczba(v[i][10]),
      termin: r[6] || '', arkusz: ark, analizator: anal, zakres: zakres, info: r[13] || ''
    });
  }
  return out;
}

/* ------------------------------------------------------------------ stan dla aplikacji */
function katStan() {
  const ss = katSS(), A = katArkusze(ss);
  const st = katCzytaj(A.status), sp = katCzytaj(A.sprawy), gr = katCzytaj(A.grafik), u = katUstCzytaj(A.ust);
  const items = katZapytania(ss).map(function (it) {
    const o = st[it.id] && st[it.id].d;
    it.st = 'luzne'; it.nt = ''; it.dz = null; it.g = ''; it.widz = false; it.hist = [];
    if (o) ['st', 'nt', 'dz', 'g', 'widz', 'hist'].forEach(function (k) { if (o[k] !== undefined) it[k] = o[k]; });
    delete st[it.id];
    return it;
  });
  Object.keys(st).forEach(function (id) { const o = st[id].d; if (o && o.reczne) { o.id = id; items.push(o); } });
  return {
    ok: true, wersja: KAT_WERSJA, rev: Number(u.rev || 0), czas: Date.now(), items: items,
    wpisy: Object.keys(sp).map(function (id) { const o = sp[id].d; o.id = id; return o; }),
    graf: {
      v: 2, br: u.brygady || KAT_BRYGADY, kol: u.statusy || KAT_STATUSY,
      k: Object.keys(gr).map(function (id) { const o = gr[id].d; o.id = id; return o; })
    }
  };
}

/* ------------------------------------------------------------------ zapis (partia zmian z aplikacji) */
function katTxt(v, n) { return String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').slice(0, n); }
function katDzien(v) { return /^\d{4}-\d{2}-\d{2}$/.test(String(v || '')) ? String(v) : null; }
function katGodz(v) { return /^\d{1,2}:\d{2}$/.test(String(v || '')) ? String(v) : ''; }
function katKolor(v) { return /^#[0-9A-Fa-f]{6}$/.test(String(v || '')) ? String(v) : ''; }
function katHist(h) {
  return (Array.isArray(h) ? h : []).slice(-60).map(function (x) { return { ts: Number(x && x.ts) || 0, x: katTxt(x && x.x, 200) }; });
}
function katCzyscZap(d, reczne) {
  const o = {
    st: KAT_ST_ZAP.indexOf(d.st) >= 0 ? d.st : 'luzne', nt: katTxt(d.nt, 4000), dz: katDzien(d.dz), g: katGodz(d.g),
    widz: !!d.widz, hist: katHist(d.hist)
  };
  if (reczne) {
    o.reczne = true; o.typ = 'r'; o.ts = Number(d.ts) || Date.now(); o.nr = katTxt(d.nr, 30);
    o.kl = katTxt(d.kl, 120); o.tel = katTxt(d.tel, 40); o.ul = katTxt(d.ul, 200); o.ds = katTxt(d.ds, 60); o.em = katTxt(d.em, 120);
    o.m2 = katLiczba(d.m2); o.kwota = 0; o.zakres = []; o.info = katTxt(d.info, 300);
  }
  return o;
}
function katCzyscKaf(d) {
  return {
    ul: katTxt(d.ul, 160).toUpperCase(), mies: katTxt(d.mies, 20).toUpperCase(), m2: katTxt(d.m2, 10), info: katTxt(d.info, 200).toUpperCase(),
    tel: katTxt(d.tel, 40), kol: katTxt(d.kol, 40), c: katKolor(d.c), br: katTxt(d.br, 40), od: katDzien(d.od),
    dni: Math.min(30, Math.max(1, Math.round(Number(d.dni) || 1))), zid: d.zid ? katTxt(d.zid, 80) : null
  };
}
function katCzyscSprawa(d) { return { dz: katDzien(d.dz) || Utilities.formatDate(new Date(), 'Europe/Warsaw', 'yyyy-MM-dd'), g: katGodz(d.g), x: katTxt(d.x, 200), prv: !!d.prv }; }
function katCzyscUst(d) {
  const br = (Array.isArray(d.br) ? d.br : []).slice(0, 12).map(function (b) { return { id: katTxt(b.id, 40), n: katTxt(b.n, 24) || 'BRYGADA' }; })
    .filter(function (b) { return KAT_ID.test(b.id); });
  const kol = (Array.isArray(d.kol) ? d.kol : []).slice(0, 20).map(function (c) { return { id: katTxt(c.id, 40), n: katTxt(c.n, 30), c: katKolor(c.c) || '#8A8178' }; })
    .filter(function (c) { return KAT_ID.test(c.id); });
  if (!br.length || !kol.length) throw new Error('Puste brygady albo statusy');
  return { br: br, kol: kol };
}

function katZapisz(ops) {
  if (!Array.isArray(ops)) return { ok: false, blad: 'Brak zmian' };
  if (ops.length > KAT_MAX_OPS) return { ok: false, blad: 'Za dużo zmian naraz' };
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(25000)) return { ok: false, blad: 'Serwer zajęty, spróbuj za chwilę.' };
  try {
    const ss = katSS(), A = katArkusze(ss);
    const u = katUstCzytaj(A.ust);
    const brNaz = {};
    (u.brygady || KAT_BRYGADY).forEach(function (b) { brNaz[b.id] = b.n; });
    const zs = [], zw = [], zg = [];
    let ust = null;
    ops.forEach(function (op) {
      if (!op || typeof op !== 'object') return;
      if (op.t === 'ust') { ust = katCzyscUst(op.d || {}); ust.br.forEach(function (b) { brNaz[b.id] = b.n; }); return; }
      const id = String(op.id || '');
      if (!KAT_ID.test(id)) throw new Error('Złe ID: ' + id.slice(0, 20));
      const d = op.d;
      if (d !== null && (typeof d !== 'object' || JSON.stringify(d).length > 30000)) throw new Error('Złe dane: ' + id);
      if (op.t === 'zap') {
        const reczne = d ? (!!d.reczne || /^r/.test(id)) : true;
        const c = d === null ? null : katCzyscZap(d, reczne);
        if (d === null && !/^r/.test(id)) return; /* zapytań z Rejestru nie usuwamy */
        zs.push({ id: id, d: c, opis: c ? [c.st, c.dz ? c.dz + (c.g ? ' ' + c.g : '') : '', reczne ? c.kl + ' ' + c.tel : '', c.nt.slice(0, 80)].filter(String).join(' | ') : '' });
      } else if (op.t === 'wpis') {
        const c = d === null ? null : katCzyscSprawa(d);
        zw.push({ id: id, d: c, opis: c ? (c.dz + ' ' + (c.g || '') + ' ' + c.x + (c.prv ? ' (prywatne)' : '')).replace(/\s+/g, ' ') : '' });
      } else if (op.t === 'kaf') {
        const c = d === null ? null : katCzyscKaf(d);
        zg.push({ id: id, d: c, opis: c ? [(c.br && c.od) ? (brNaz[c.br] || c.br) + ' ' + c.od + (c.dni > 1 ? ' (' + c.dni + ' dni)' : '') : 'DO ROZPLANOWANIA',
          c.ul + (c.mies ? '/' + c.mies : '') + (c.m2 ? ' (' + c.m2 + ')' : '') + (c.info ? ' / ' + c.info : ''), c.tel].filter(String).join(' | ') : '' });
      } else throw new Error('Nieznana zmiana: ' + String(op.t).slice(0, 20));
    });
    katZapiszRekordy(A.status, zs);
    katZapiszRekordy(A.sprawy, zw);
    katZapiszRekordy(A.grafik, zg);
    if (ust) { katUstZapisz(A.ust, 'brygady', ust.br); katUstZapisz(A.ust, 'statusy', ust.kol); }
    katUstZapisz(A.ust, 'rev', Number(u.rev || 0) + 1);
    SpreadsheetApp.flush();
    return katStan();
  } finally {
    lock.releaseLock();
  }
}

/* ------------------------------------------------------------------ PDF oferty (szukany przy kliknięciu) */
function katPdf(id) {
  if (!/^a_[\w-]{20,}$/.test(id)) return { ok: false, blad: 'Brak PDF dla tego zapytania' };
  const it = katZapytania(katSS()).filter(function (x) { return x.id === id; })[0];
  if (!it) return { ok: false, blad: 'Nie znalazłem zapytania' };
  const ark = DriveApp.getFileById(id.slice(2));
  const par = ark.getParents();
  if (par.hasNext() && it.kiedy) {
    const pliki = par.next().getFilesByType(MimeType.PDF);
    while (pliki.hasNext()) {
      const f = pliki.next();
      if (f.getName().indexOf(String(it.kiedy)) === 0) return { ok: true, url: f.getUrl(), nazwa: f.getName() };
    }
  }
  return { ok: true, url: it.arkusz || ark.getUrl(), brakPdf: true };
}

/* źródło wyceny do kolumny O "Źródło" w Rejestrze (wołane z doPost w wyceny_dysk.gs) */
function katZrodloWyceny(d) {
  if (d.kopiaArtur || d.bezBcc) return 'analizator';
  if (d.zamowienie) return 'koszyk';
  return 'wycena klienta';
}
