/* SMARTPARKIET - KATALOG ZAPYTAŃ i GRAFIK BRYGAD (backend aplikacji smartparkiet.com.pl/aplikacja/)

   Plik dopisany do TEGO SAMEGO projektu Apps Script co wyceny_dysk.gs (osobny plik w edytorze: katalog.gs).
   Wejście: doPost / doGet z wyceny_dysk.gs przekazują tu tylko zapytania z polem akcja = "katalog_*"
   (jedna linijka na początku obu funkcji). Akcje wycen (zapis PDF, szkice, opinie, numer, lista) działają bez zmian.

   Dane:
   - zapytania czytane z pierwszego arkusza "Rejestr wycen" (tam zapisuje każda wycena i zamówienie ze strony),
   - w tym samym pliku osobne zakładki: Katalog_status (statusy, notatki, terminy, wpisy z ręki),
     Katalog_sprawy (sprawy ogólne i prywatne), Grafik (kafelki brygad), Kalendarz (kafelki godzinowe, od 15.11), Ustawienia_katalog (brygady, statusy, kolumny kalendarza).
     Kolumna "Dane" to zapis aplikacji - nie edytować ręcznie (kolumna "Opis" jest do czytania).

   Hasło Artura: tylko skrót (SHA-256 z solą, wielokrotnie) we właściwościach skryptu KATALOG_HASLO.
   Ustawienie: Ustawienia projektu -> Właściwości skryptu -> dodaj KATALOG_NOWE_HASLO = hasło (min. 8 znaków)
   -> w edytorze wybierz funkcję katalogUstawHaslo i Uruchom. Funkcja zapisze skrót i usunie jawne hasło.
   Aplikacja po zalogowaniu dostaje losowy token sesji (ważny 180 dni, na serwerze trzymany tylko jego skrót). */

const KAT_WERSJA = '2026-11-15';
const KAT_ARK = { status: 'Katalog_status', sprawy: 'Katalog_sprawy', grafik: 'Grafik', ust: 'Ustawienia_katalog', kal: 'Kalendarz' };
const KAT_NAGL = ['ID', 'Opis', 'Dane (zapis aplikacji - nie edytować)', 'Zmieniono'];
const KAT_TOKEN_DNI = 180;
const KAT_ITER = 400;          /* powtórzenia skrótu hasła */
const KAT_PROBY = 5;           /* 14.11: co 5 złych haseł blokada rosnąca (KAT_BLOKADY) */
const KAT_BLOKADY = [1, 15, 30, 300]; /* minuty: 1 min, 15 min, 30 min, potem za każdym razem 5 h */
const KAT_RESET_H = 24;        /* doba bez złych prób = licznik od zera */
const KAT_MAX_REJESTR = 800;   /* tyle najnowszych wierszy Rejestru trafia do katalogu */
const KAT_MAX_OPS = 200;
const KAT_ID = /^[A-Za-z0-9_.:-]{1,80}$/;

const KAT_BRYGADY = [{ id: 'b1', n: 'JARO.2' }, { id: 'b2', n: 'JAREK' }, { id: 'b3', n: 'MACIEK' }, { id: 'b4', n: 'PODWYKONAWCA' }];
const KAT_STATUSY = [
  { id: 'ok', n: 'Potwierdzone', c: '#2E9E3A' }, { id: 'mysli', n: 'Zastanawia się', c: '#FF8A00' },
  { id: 'wst', n: 'Wstępnie', c: '#FFD60A' }, { id: 'ogl', n: 'Oględziny / pomiar', c: '#A8D8F5' },
  { id: 'term', n: 'Termin do potwierdzenia', c: '#1E63D6' }, { id: 'pilne', n: 'Pilne', c: '#E0262B' },
  { id: 'awaria', n: 'Awaria', c: '#6B2A5E' }, { id: 'gotowe', n: 'Zrobione', c: '#B6FF1A' }, { id: 'inne', n: 'Inne', c: '#FF6FAE' }];
/* 15.11 Artur: kalendarz godzinowy (kafelki ruchome, godziny stałe) - kolumny edytowalne */
const KAT_KAL_KOL = [{ id: 'c1', n: 'KONTAKT' }, { id: 'c2', n: 'OGLĘDZINY' }, { id: 'c3', n: 'ZLECENIA' }];
const KAT_ST_ZAP = ['luzne', 'rozmowa', 'ogledziny', 'termin', 'zatw', 'wtoku', 'zrobione', 'odpadlo'];

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
    kal: katArkusz(ss, KAT_ARK.kal, KAT_NAGL),
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
  const st = katCzytaj(A.status), sp = katCzytaj(A.sprawy), gr = katCzytaj(A.grafik), kl = katCzytaj(A.kal), u = katUstCzytaj(A.ust);
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
    },
    kal: {
      kol: u.kalKol || KAT_KAL_KOL,
      k: Object.keys(kl).map(function (id) { const o = kl[id].d; o.id = id; return o; })
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
function katCzyscSprawa(d) {
  const o = { dz: katDzien(d.dz) || Utilities.formatDate(new Date(), 'Europe/Warsaw', 'yyyy-MM-dd'), g: katGodz(d.g), x: katTxt(d.x, 200), prv: !!d.prv };
  if (d.br && KAT_ID.test(String(d.br))) o.br = String(d.br); /* informacja dla brygady (pod kafelkami), opcjonalnie */
  return o;
}
/* kafelek kalendarza: dzień, godzina startu (7:00-19:30 co 30 min), długość w minutach, kolumna, tekst, kolor, powiązane zapytanie */
function katCzyscKal(d) {
  const g = katGodz(d.g) || '8:00', p = g.split(':'), m = Math.min(19 * 60 + 30, Math.max(7 * 60, Math.round((+p[0] * 60 + +p[1]) / 30) * 30));
  return {
    dz: katDzien(d.dz) || Utilities.formatDate(new Date(), 'Europe/Warsaw', 'yyyy-MM-dd'), g: Math.floor(m / 60) + ':' + ('0' + m % 60).slice(-2),
    min: Math.min(780, Math.max(30, Math.round((Number(d.min) || 60) / 30) * 30)), ko: KAT_ID.test(String(d.ko || '')) ? String(d.ko) : '',
    x: katTxt(d.x, 300), c: katKolor(d.c), zid: d.zid && KAT_ID.test(String(d.zid)) ? String(d.zid) : null
  };
}
function katCzyscKalKol(d) {
  const kol = (Array.isArray(d.kol) ? d.kol : []).slice(0, 8).map(function (c) { return { id: katTxt(c.id, 40), n: katTxt(c.n, 24) || 'KOLUMNA' }; })
    .filter(function (c) { return KAT_ID.test(c.id); });
  if (!kol.length) throw new Error('Pusta lista kolumn kalendarza');
  return kol;
}
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
  const t0 = Date.now();
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(25000)) return { ok: false, blad: 'Serwer zajęty, spróbuj za chwilę.' };
  let wynik, ek = null;
  try {
    const ss = katSS(), A = katArkusze(ss);
    const u = katUstCzytaj(A.ust);
    /* stan przed zapisem - do ramki "INFORMACJE DLA EKIPY" (kafelek mógł zmienić zapytanie, info brygadę lub dzień) */
    let przed = null;
    try { if (ops.some(function (o) { return o && (o.t === 'kaf' || o.t === 'wpis'); })) przed = { gr: katCzytaj(A.grafik), sp: katCzytaj(A.sprawy) }; } catch (e) { przed = null; }
    const brNaz = {};
    (u.brygady || KAT_BRYGADY).forEach(function (b) { brNaz[b.id] = b.n; });
    const zs = [], zw = [], zg = [], zk = [];
    let ust = null, kalKol = null;
    const kolNaz = {};
    (u.kalKol || KAT_KAL_KOL).forEach(function (c) { kolNaz[c.id] = c.n; });
    ops.forEach(function (op) {
      if (!op || typeof op !== 'object') return;
      if (op.t === 'ust') { ust = katCzyscUst(op.d || {}); ust.br.forEach(function (b) { brNaz[b.id] = b.n; }); return; }
      if (op.t === 'kalust') { kalKol = katCzyscKalKol(op.d || {}); kalKol.forEach(function (c) { kolNaz[c.id] = c.n; }); return; }
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
        zw.push({ id: id, d: c, opis: c ? (c.dz + ' ' + (c.g || '') + ' ' + (c.br ? (brNaz[c.br] || c.br) + ': ' : '') + c.x + (c.prv ? ' (prywatne)' : '')).replace(/\s+/g, ' ') : '' });
      } else if (op.t === 'kaf') {
        const c = d === null ? null : katCzyscKaf(d);
        zg.push({ id: id, d: c, opis: c ? [(c.br && c.od) ? (brNaz[c.br] || c.br) + ' ' + c.od + (c.dni > 1 ? ' (' + c.dni + ' dni)' : '') : 'DO ROZPLANOWANIA',
          c.ul + (c.mies ? '/' + c.mies : '') + (c.m2 ? ' (' + c.m2 + ')' : '') + (c.info ? ' / ' + c.info : ''), c.tel].filter(String).join(' | ') : '' });
      } else if (op.t === 'kal') {
        const c = d === null ? null : katCzyscKal(d);
        zk.push({ id: id, d: c, opis: c ? (c.dz + ' ' + c.g + ' (' + c.min + ' min) ' + (kolNaz[c.ko] || '') + ': ' + c.x).replace(/\s+/g, ' ') : '' });
      } else throw new Error('Nieznana zmiana: ' + String(op.t).slice(0, 20));
    });
    katZapiszRekordy(A.status, zs);
    katZapiszRekordy(A.sprawy, zw);
    katZapiszRekordy(A.grafik, zg);
    katZapiszRekordy(A.kal, zk);
    if (kalKol) katUstZapisz(A.ust, 'kalKol', kalKol);
    if (ust) { katUstZapisz(A.ust, 'brygady', ust.br); katUstZapisz(A.ust, 'statusy', ust.kol); }
    katUstZapisz(A.ust, 'rev', Number(u.rev || 0) + 1);
    SpreadsheetApp.flush();
    try { ek = katEkipaPrzygotuj(ops, przed, A, ust ? ust.br : (u.brygady || KAT_BRYGADY)); } catch (e) { ek = null; }
    wynik = katStan();
  } finally {
    lock.releaseLock();
  }
  /* arkusze wycen aktualizowane po zwolnieniu blokady; błąd arkusza nigdy nie psuje zapisu aplikacji */
  if (ek && wynik && wynik.ok) { try { wynik.ark = katEkipaPisz(ek, t0); } catch (e) { console.error('ekipa: ' + e); } }
  return wynik;
}

/* ------------------------------------------------------------------ arkusz wyceny: ramka INFORMACJE DLA EKIPY (Artur 15.11)
   Stały blok 7 wierszy (A:E) na końcu zakładki "Wycena", znajdowany po tytule w kolumnie A i nadpisywany przy każdej zmianie.
   Tylko zapytania z arkuszem (a_<id pliku>); treść porównywana skrótem, więc arkusz otwierany tylko, gdy coś się zmieniło. */
const KAT_EK_TYT = 'INFORMACJE DLA EKIPY';
const KAT_EK_MAX = 4;          /* arkuszy na jeden zapis */
const KAT_EK_CZAS = 12000;     /* ms od początku zapisu - aplikacja czeka na odpowiedź max 30 s */
const KAT_DNI_KR = ['niedz.', 'pon.', 'wt.', 'śr.', 'czw.', 'pt.', 'sob.'];
function katIsoD(s) { const a = String(s).split('-'); return new Date(+a[0], a[1] - 1, +a[2]); }
function katDIso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
function katDKr(s) { const d = katIsoD(s); return KAT_DNI_KR[d.getDay()] + ' ' + ('0' + d.getDate()).slice(-2) + '.' + ('0' + (d.getMonth() + 1)).slice(-2); }
/* dni robocze kafelka pn-sb (niedziela pomijana) - jak segi() w aplikacji */
function katDniKaf(k) {
  const r = [];
  if (!k || !k.od) return r;
  let d = katIsoD(k.od);
  if (d.getDay() === 0) d.setDate(d.getDate() + 1);
  for (let i = 0; i < Math.max(1, k.dni || 1); i++) { r.push(katDIso(d)); d.setDate(d.getDate() + 1); if (d.getDay() === 0) d.setDate(d.getDate() + 1); }
  return r;
}
function katTekstKaf(k) { return ((k.ul || '') + (k.mies ? '/' + k.mies : '') + (k.m2 ? ' (' + k.m2 + ')' : '') + (k.info ? ' / ' + k.info : '')).toUpperCase(); }
function katEkipaPrzygotuj(ops, przed, A, br) {
  const gr = katCzytaj(A.grafik), sp = katCzytaj(A.sprawy), st = katCzytaj(A.status);
  const zid = {}, dodaj = function (z) { if (/^a_[\w-]{20,}$/.test(String(z || ''))) zid[z] = 1; };
  const poBryg = function (b, dz) { if (!b || !dz) return; Object.keys(gr).forEach(function (id) { const k = gr[id].d; if (k && k.br === b && katDniKaf(k).indexOf(dz) >= 0) dodaj(k.zid); }); };
  ops.forEach(function (o) {
    if (!o) return;
    if (o.t === 'zap') dodaj(o.id);
    else if (o.t === 'kaf') { dodaj(o.d && o.d.zid); const s = przed && przed.gr[o.id]; if (s && s.d) dodaj(s.d.zid); }
    else if (o.t === 'wpis') { if (o.d) poBryg(o.d.br, o.d.dz); const s = przed && przed.sp[o.id]; if (s && s.d) poBryg(s.d.br, s.d.dz); }
    else if (o.t === 'ust') Object.keys(gr).forEach(function (id) { const k = gr[id].d; if (k && k.br) dodaj(k.zid); });
  });
  const p = PropertiesService.getScriptProperties();
  let kolejka = [];
  try { kolejka = JSON.parse(p.getProperty('KAT_EK_KOLEJKA') || '[]'); } catch (e) { kolejka = []; }
  kolejka.forEach(dodaj);
  const brNaz = {};
  (br || []).forEach(function (b) { brNaz[b.id] = b.n; });
  return Object.keys(zid).map(function (z) { return { zid: z, wiersze: katEkipaTresc(z, gr, sp, st, brNaz) }; });
}
function katEkipaTresc(zid, gr, sp, st, brNaz) {
  const kaf = Object.keys(gr).map(function (id) { return gr[id].d; }).filter(function (k) { return k && k.zid === zid && k.br && k.od; })
    .sort(function (a, b) { return a.od < b.od ? -1 : a.od > b.od ? 1 : 0; });
  const termin = [], opis = [], info = [];
  let tel = '';
  kaf.forEach(function (k) {
    const dni = katDniKaf(k), bn = brNaz[k.br] || k.br;
    termin.push(bn + ': ' + (dni.length > 1 ? katDKr(dni[0]) + ' - ' + katDKr(dni[dni.length - 1]) + ' (' + dni.length + ' dni)' : katDKr(dni[0])) + ' ' + dni[0].slice(0, 4));
    const t = katTekstKaf(k);
    if (t && opis.indexOf(t) < 0) opis.push(t);
    if (!tel && k.tel) tel = k.tel;
    Object.keys(sp).map(function (id) { return sp[id].d; }).filter(function (w) { return w && w.br === k.br && dni.indexOf(w.dz) >= 0; })
      .sort(function (a, b) { return (a.dz + (a.g || '')) < (b.dz + (b.g || '')) ? -1 : 1; })
      .forEach(function (w) { const l = katDKr(w.dz) + ': ' + (w.g ? w.g + ' ' : '') + w.x; if (info.indexOf(l) < 0) info.push(l); });
  });
  const z = st[zid] && st[zid].d;
  return [
    ['Termin realizacji', termin.join('\n')],
    ['Zlecenie (grafik)', opis.join('\n')],
    ['Informacje dla brygady', info.join('\n')],
    ['Notatka', (z && z.nt) || ''],
    ['Telefon klienta', tel]
  ];
}
function katEkipaPisz(lista, t0) {
  const p = PropertiesService.getScriptProperties(), zrobione = [], zostaje = [];
  let ile = 0;
  lista.forEach(function (e) {
    const pusto = e.wiersze.every(function (w) { return !w[1]; });
    const klucz = 'KAT_EK_' + e.zid.slice(2, 60), skrot = katSha(JSON.stringify(e.wiersze)).slice(0, 24), byl = p.getProperty(klucz);
    if (byl === skrot || (!byl && pusto)) return;          /* bez zmian albo nigdy nie było czego wpisać */
    if (ile >= KAT_EK_MAX || Date.now() - t0 > KAT_EK_CZAS) { zostaje.push(e.zid); return; }
    ile++;
    try { katEkipaRamka(e.zid.slice(2), e.wiersze); p.setProperty(klucz, skrot); zrobione.push(e.zid); }
    catch (x) { console.error('ekipa ' + e.zid + ': ' + x); }  /* np. arkusz usunięty - pomijamy */
  });
  if (zostaje.length) p.setProperty('KAT_EK_KOLEJKA', JSON.stringify(zostaje.slice(0, 50))); else p.deleteProperty('KAT_EK_KOLEJKA');
  return zrobione;
}
function katEkipaRamka(plikId, wiersze) {
  const ss = SpreadsheetApp.openById(plikId);
  const sh = ss.getSheetByName('Wycena') || ss.getSheets()[0];
  const n = sh.getLastRow();
  let start = 0;
  if (n > 0) {
    const a = sh.getRange(1, 1, n, 1).getValues();
    for (let i = 0; i < a.length; i++) if (String(a[i][0]).trim() === KAT_EK_TYT) { start = i + 1; break; }
  }
  if (!start) start = n + 2;
  const teraz = Utilities.formatDate(new Date(), 'Europe/Warsaw', 'dd.MM.yyyy HH:mm');
  const dane = [[KAT_EK_TYT, '', '', '', '']].concat(wiersze.map(function (w) { return [w[0], w[1] || '-', '', '', '']; }), [['Zaktualizowano', teraz + ' (aplikacja Katalog)', '', '', '']]);
  const r = sh.getRange(start, 1, dane.length, 5);
  r.setValues(dane).setWrap(true).setVerticalAlignment('top').setFontSize(11).setFontColor('#16120F').setBackground('#FFF4EC').setFontWeight('normal');
  sh.getRange(start, 1, 1, 5).merge().setBackground('#FE6500').setFontColor('#FFFFFF').setFontWeight('bold').setFontSize(12);
  sh.getRange(start + 1, 2, dane.length - 1, 4).mergeAcross();
  sh.getRange(start + 1, 1, dane.length - 1, 1).setFontWeight('bold').setFontColor('#4A5058');
  sh.getRange(start + 1, 2, 3, 1).setFontWeight('bold');      /* termin, zlecenie, info dla brygady */
  sh.getRange(start + dane.length - 1, 1, 1, 5).setFontSize(9).setFontColor('#6B6560');
  r.setBorder(true, true, true, true, false, true, '#FE6500', SpreadsheetApp.BorderStyle.SOLID_MEDIUM);
  SpreadsheetApp.flush();
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
