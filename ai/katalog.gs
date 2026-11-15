/* SMARTPARKIET - KATALOG ZAPYTAŃ i GRAFIK BRYGAD (backend aplikacji smartparkiet.com.pl/aplikacja/)

   Plik dopisany do TEGO SAMEGO projektu Apps Script co wyceny_dysk.gs (osobny plik w edytorze: katalog.gs).
   Wejście: doPost / doGet z wyceny_dysk.gs przekazują tu tylko zapytania z polem akcja = "katalog_*"
   (jedna linijka na początku obu funkcji). Akcje wycen (zapis PDF, szkice, opinie, numer, lista) działają bez zmian.

   Dane:
   - zapytania czytane z pierwszego arkusza "Rejestr wycen" (tam zapisuje każda wycena i zamówienie ze strony),
   - w tym samym pliku osobne zakładki: Katalog_status (statusy, notatki, terminy, wpisy z ręki),
     Katalog_sprawy (sprawy ogólne i prywatne), Grafik (kafelki brygad), Kalendarz (kafelki godzinowe, od 15.11), Katalog_maile (zapytania e-mail, od 15.11), Ustawienia_katalog (brygady, statusy, kolumny kalendarza).
     Kolumna "Dane" to zapis aplikacji - nie edytować ręcznie (kolumna "Opis" jest do czytania).

   Hasło Artura: tylko skrót (SHA-256 z solą, wielokrotnie) we właściwościach skryptu KATALOG_HASLO.
   Ustawienie: Ustawienia projektu -> Właściwości skryptu -> dodaj KATALOG_NOWE_HASLO = hasło (min. 8 znaków)
   -> w edytorze wybierz funkcję katalogUstawHaslo i Uruchom. Funkcja zapisze skrót i usunie jawne hasło.
   Aplikacja po zalogowaniu dostaje losowy token sesji (ważny 180 dni, na serwerze trzymany tylko jego skrót). */

const KAT_WERSJA = '2026-11-15m';
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
    if (akcja === 'katalog_zal') return katZal(d.id, !!d.mini);   /* 15.11: zdjęcia z zapytań e-mail */
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
  const items = katZapytania(ss).concat(katMaileItems(ss)).map(function (it) {
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

/* ------------------------------------------------------------------ ZAPYTANIA E-MAIL (Artur WA 15.11 20:54)
   Maile pisane przez klientów wprost na smartparkiet@gmail.com. Artur ma w swoim Gmailu filtr
   "Do: smartparkiet@gmail.com -> Przekaż do panbet77@gmail.com" (kopia zostaje u niego). Tu, na koncie panbet77,
   wyzwalacz co 5 min (katalogPobierzMaile) zamienia przekazane maile w pozycje katalogu o źródle "E-mail":
   - jedna pozycja = jeden wątek Gmaila (id m_<id wątku>), kolejne maile klienta w wątku dopisywane do tej samej pozycji,
   - zdjęcia i PDF z załączników zapisane na Dysku: "SMARTPARKIET - wyceny/Zapytania e-mail/RRRR-MM",
   - pomijane: powiadomienia (noreply, Google, Facebook...), newslettery (List-Unsubscribe), autorespondery,
     maile z formularzy strony (formularz@smartparkiet.com.pl - te wyceny są już w Rejestrze) i maile z naszych kont,
   - przetworzone wątki dostają etykietę "katalog-pobrane" (pominięte "katalog-pominiete") i wychodzą z Odebranych panbet77,
   - deduplikacja po Message-ID (i id wiadomości Gmaila), więc ponowne przekazanie tego samego maila nic nie dubluje.
   Dane: zakładka Katalog_maile (ID, Opis, Dane). Status, notatka i termin - jak przy innych zapytaniach (Katalog_status).
   URUCHOMIĆ RAZ W EDYTORZE: katalogMaileUstaw (zakłada wyzwalacz; Google poprosi o zgodę na Gmail). */
const KAT_MAIL_ADR = 'smartparkiet@gmail.com';
const KAT_MAIL_ET = 'katalog-pobrane';
const KAT_MAIL_ET_POM = 'katalog-pominiete';
const KAT_MAIL_FOLDER = 'Zapytania e-mail';
const KAT_MAIL_ARK = 'Katalog_maile';
const KAT_MAIL_DNI = 10;        /* ile dni wstecz szukamy nieprzetworzonych */
const KAT_MAIL_MAXW = 15;       /* wiadomości trzymanych na pozycję */
const KAT_MAIL_ZAL = 12;        /* załączników z jednej wiadomości */
const KAT_MAIL_MIN_B = 12000;   /* mniejsze obrazki = logo/ikony ze stopki */
const KAT_MAIL_MAX_B = 20 * 1024 * 1024;
const KAT_MAIL_POMIN = /(no-?reply|do-?not-?reply|nie-?odpowiadaj|mailer-daemon|postmaster|notification|powiadomieni|newsletter|marketing@|@(?:[\w-]+\.)*(?:google|googlemail|facebook|facebookmail|instagram|linkedin|youtube|olx|allegro|booking|microsoft|paypal|tiktok|twitter)\.(?:com|pl)$|@smartparkiet\.com\.pl$|^panbet77@gmail\.com$|^smartparkiet(?:\.kontakt)?@gmail\.com$)/i;
const KAT_DZIELNICE = ['Bemowo', 'Białołęka', 'Bielany', 'Mokotów', 'Ochota', 'Praga-Południe', 'Praga-Północ', 'Rembertów', 'Śródmieście', 'Targówek', 'Ursus', 'Ursynów', 'Wawer', 'Wesoła', 'Wilanów', 'Włochy', 'Wola', 'Żoliborz', 'Kabaty', 'Gocław', 'Saska Kępa', 'Tarchomin', 'Piaseczno', 'Konstancin', 'Józefów', 'Otwock', 'Ząbki', 'Marki', 'Łomianki', 'Pruszków', 'Piastów', 'Legionowo', 'Wołomin', 'Raszyn', 'Kobyłka', 'Sulejówek', 'Milanówek'];

function katMaileArk(ss) { return katArkusz(ss || katSS(), KAT_MAIL_ARK, KAT_NAGL); }
/* pozycje e-mail do katStan */
function katMaileItems(ss) {
  const sh = ss.getSheetByName(KAT_MAIL_ARK);
  if (!sh) return [];
  const m = katCzytaj(sh);
  return Object.keys(m).map(function (id) {
    const d = m[id].d || {};
    return {
      id: id, typ: 'e', ts: Number(d.ts) || 0, kiedy: '', nr: '', kl: d.kl || '', tel: d.tel || '', ul: d.ul || '', ds: d.ds || '', em: d.em || '',
      m2: Number(d.m2) || 0, kwota: 0, upust: 0, termin: '', arkusz: '', analizator: '', zakres: [], info: '',
      temat: d.temat || '', ost: Number(d.ost) || Number(d.ts) || 0,
      wiad: (Array.isArray(d.wiad) ? d.wiad : []).map(function (w) { return { ts: w.ts, od: w.od, em: w.em, x: w.x, zal: w.zal || [] }; })
    };
  });
}

/* nadawca "Jan Kowalski <jan@x.pl>" -> {n, em} */
function katMailOsoba(s) {
  s = String(s || '').trim();
  const m = s.match(/^\s*"?([^"<]*?)"?\s*<([^>]+)>\s*$/);
  const em = (m ? m[2] : s).trim().toLowerCase();
  let n = m ? m[1].trim() : '';
  if (!n || n.indexOf('@') >= 0) n = em.split('@')[0].replace(/[._-]+/g, ' ').replace(/\d+/g, ' ').replace(/\s+/g, ' ').trim()
    .replace(/(^|\s)\S/g, function (x) { return x.toUpperCase(); });
  return { n: n.slice(0, 120), em: em.slice(0, 120) };
}
/* treść bez cytatów, stopek i podpisów z telefonu */
function katMailTresc(t) {
  const linie = String(t || '').replace(/\r/g, '').split('\n'), out = [];
  const koniec = /^\s*(W dniu .{5,160}(napisał|napisała|napisał\(a\)|pisze):?\s*$|On .{5,200} wrote:?\s*$|-{2,}\s*(Original Message|Wiadomość oryginalna|Oryginalna wiadomość|Forwarded message|Wiadomość przekazana)|_{8,}|(Od|From):\s.+@|Wysłane z (mojego )?(iPhone|iPada|telefonu|urządzenia|Samsung|aplikacji)|Sent from my |Pobierz Outlook|Get Outlook for|-- ?$)/i;
  for (let i = 0; i < linie.length; i++) {
    const l = linie[i];
    if (koniec.test(l)) break;
    if (/^\s*>/.test(l)) continue;
    out.push(l.replace(/\s+$/, ''));
  }
  return out.join('\n').replace(/\n{3,}/g, '\n\n').trim().slice(0, 3000);
}
function katBezPl(s) { return String(s || '').toLowerCase().replace(/[ąćęłńóśźż]/g, function (c) { return 'acelnoszz'['ąćęłńóśźż'.indexOf(c)]; }); }
/* telefon, metraż, adres, dzielnica z tematu i treści (proste reguły - Artur i tak widzi całą treść) */
function katMailDane(temat, tresc) {
  const t = String(temat || '') + '\n' + String(tresc || ''), o = { tel: '', m2: 0, ul: '', ds: '' };
  const tel = t.match(/(?:^|[^\d])(?:\+48|0048|48)?[\s.-]?\(?([1-9]\d{2})\)?[\s.-]?(\d{3})[\s.-]?(\d{3})(?!\d)/);
  if (tel) o.tel = tel[1] + ' ' + tel[2] + ' ' + tel[3];
  const m2 = t.match(/(\d{1,4}(?:[.,]\d{1,2})?)\s*(?:m2|m²|m\^2|mkw|m\.\s?kw|m\s?kw|metr(?:ów|y)?\s*kw)/i);
  if (m2) o.m2 = katLiczba(m2[1]);
  const ul = t.match(/(?:^|[\s,(])(?:ul\.?|ulica|ulicy|al\.|aleja|alei|os\.|osiedle|pl\.|plac)\s*([A-ZŁŚŻŹĆŃÓĘĄ0-9][A-Za-z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ.\- ]{1,40}?\s\d+[a-zA-Z]?(?:\s?\/\s?\d+[a-zA-Z]?)?(?:\s?m\.?\s?\d+)?)(?![\d])/);
  if (ul) o.ul = ul[1].replace(/\s+/g, ' ').trim();
  const bt = ' ' + katBezPl(t).replace(/[^a-z0-9]+/g, ' ') + ' ';
  for (let i = 0; i < KAT_DZIELNICE.length; i++) {
    const d = katBezPl(KAT_DZIELNICE[i]).replace(/[^a-z0-9]+/g, ' ');
    /* odmiana: "na Mokotowie", "z Ursynowa" - rdzeń bez ostatniej litery dla dłuższych nazw */
    const rdzen = d.length >= 6 ? d.slice(0, -1) : d;
    if (bt.indexOf(' ' + d + ' ') >= 0 || (d.length >= 6 && bt.indexOf(' ' + rdzen) >= 0)) { o.ds = KAT_DZIELNICE[i]; break; }
  }
  return o;
}
function katMailPomin(msg, od) {
  if (!od.em || KAT_MAIL_POMIN.test(od.em)) return true;
  const h = function (n) { try { return String(msg.getHeader(n) || ''); } catch (e) { return ''; } };
  if (h('List-Unsubscribe') || h('List-Id')) return true;
  if (/^(bulk|list|junk)$/i.test(h('Precedence').trim())) return true;
  const as = h('Auto-Submitted').trim();
  if (as && !/^no$/i.test(as)) return true;
  if (/^(Automatyczna odpowiedź|Auto(matic)? ?reply|Out of office|Poza biurem|Nieobecność|Undeliverable|Delivery Status|Niedostarczon)/i.test(msg.getSubject() || '')) return true;
  return false;
}
function katMailFolder(kiedy) {
  const g = glownyFolder();
  let it = g.getFoldersByName(KAT_MAIL_FOLDER);
  const z = it.hasNext() ? it.next() : g.createFolder(KAT_MAIL_FOLDER);
  const nazwa = Utilities.formatDate(kiedy || new Date(), 'Europe/Warsaw', 'yyyy-MM');
  it = z.getFoldersByName(nazwa);
  return it.hasNext() ? it.next() : z.createFolder(nazwa);
}
function katMailZalaczniki(msg, kl, kiedy) {
  const out = [];
  let lista = [];
  try { lista = msg.getAttachments({ includeInlineImages: true, includeAttachments: true }) || []; } catch (e) { lista = []; }
  let folder = null, nr = 0;
  for (let i = 0; i < lista.length && out.length < KAT_MAIL_ZAL; i++) {
    const a = lista[i], typ = String(a.getContentType() || '').toLowerCase(), n = String(a.getName() || 'plik'), b = a.getSize();
    const obraz = /^image\/(jpe?g|png|webp|heic|heif|gif)/.test(typ) || /\.(jpe?g|png|webp|heic|heif)$/i.test(n), pdf = typ === 'application/pdf' || /\.pdf$/i.test(n);
    if (!obraz && !pdf) continue;
    if (b > KAT_MAIL_MAX_B || (obraz && b < KAT_MAIL_MIN_B)) continue;
    folder = folder || katMailFolder(kiedy);
    nr++;
    const nazwa = Utilities.formatDate(kiedy, 'Europe/Warsaw', 'yyyy-MM-dd HH-mm') + ' ' + String(kl || 'e-mail').replace(/[\\/:*?"<>|]+/g, ' ').slice(0, 60) + ' - ' + nr + ' - ' + n.replace(/[\\/:*?"<>|]+/g, '_').slice(0, 80);
    const f = folder.createFile(a.copyBlob().setName(nazwa));
    out.push({ id: f.getId(), n: n.slice(0, 80), t: obraz ? 'z' : 'p', b: b });
  }
  return out;
}
function katMailOpis(d) {
  const zal = (d.wiad || []).reduce(function (s, w) { return s + (w.zal || []).length; }, 0);
  return [d.kl, d.em, d.tel, d.temat, (d.wiad || []).length + ' wiad.', zal + ' zał.'].filter(String).join(' | ');
}
/* skraca zapis, gdy przekroczyłby limit komórki arkusza (50 000 znaków) */
function katMailPrzytnij(d) {
  d.wiad = d.wiad.slice(-KAT_MAIL_MAXW);
  let s = JSON.stringify(d), lim = 2500;
  while (s.length > 45000 && lim > 200) { d.wiad.forEach(function (w) { w.x = String(w.x || '').slice(0, lim); }); lim = Math.floor(lim / 2); s = JSON.stringify(d); }
  while (s.length > 45000 && d.wiad.length > 1) { d.wiad.shift(); s = JSON.stringify(d); }
  return d;
}
function katMailZapisz(ss, sh, zmiany) {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(25000)) throw new Error('Arkusz zajęty - spróbuję w następnym przebiegu');
  try {
    katZapiszRekordy(sh, zmiany);
    const A = katArkusze(ss), u = katUstCzytaj(A.ust);
    katUstZapisz(A.ust, 'rev', Number(u.rev || 0) + 1);
    SpreadsheetApp.flush();
  } finally { lock.releaseLock(); }
}

/* WYZWALACZ co 5 min (można też uruchomić ręcznie w edytorze) */
function katalogPobierzMaile() {
  const lockI = LockService.getUserLock();
  if (!lockI.tryLock(1000)) return 'zajęte';
  const t0 = Date.now(), wynik = { nowe: 0, dopisane: 0, pominiete: 0 };
  try {
    const etOk = GmailApp.getUserLabelByName(KAT_MAIL_ET) || GmailApp.createLabel(KAT_MAIL_ET);
    const etPom = GmailApp.getUserLabelByName(KAT_MAIL_ET_POM) || GmailApp.createLabel(KAT_MAIL_ET_POM);
    const q = '{to:' + KAT_MAIL_ADR + ' cc:' + KAT_MAIL_ADR + ' deliveredto:' + KAT_MAIL_ADR + '} -label:' + KAT_MAIL_ET + ' -label:' + KAT_MAIL_ET_POM + ' newer_than:' + KAT_MAIL_DNI + 'd';
    const watki = GmailApp.search(q, 0, 30);
    if (!watki.length) return wynik;
    const ss = katSS(), sh = katMaileArk(ss);
    const byly = katCzytaj(sh), znane = {};
    Object.keys(byly).forEach(function (id) { ((byly[id].d || {}).wiad || []).forEach(function (w) { if (w.mid) znane[w.mid] = 1; if (w.gid) znane[w.gid] = 1; }); });
    const zmiany = [];
    for (let i = 0; i < watki.length; i++) {
      if (Date.now() - t0 > 240000) break;          /* zapas do limitu 6 min - reszta w następnym przebiegu */
      const th = watki[i], id = 'm_' + th.getId();
      const rec = byly[id] ? byly[id].d : null;
      let d = rec ? JSON.parse(JSON.stringify(rec)) : null, zm = false, dodane = 0;
      th.getMessages().forEach(function (msg) {
        const gid = msg.getId();
        let mid = '';
        try { mid = String(msg.getHeader('Message-ID') || '').replace(/[<>\s]/g, '').slice(0, 200); } catch (e) {}
        if (znane[gid] || (mid && znane[mid])) return;
        if (msg.isInTrash()) return;
        const od = katMailOsoba(msg.getFrom());
        if (katMailPomin(msg, od)) return;
        const kiedy = msg.getDate(), x = katMailTresc(msg.getPlainBody());
        const rt = katMailOsoba(msg.getReplyTo() || '');
        const em = rt.em && rt.em.indexOf('@') > 0 && !KAT_MAIL_POMIN.test(rt.em) ? rt.em : od.em;
        if (!d) {
          const dane = katMailDane(msg.getSubject(), x);
          d = { typ: 'e', ts: kiedy.getTime(), kl: od.n, em: em, tel: dane.tel, ul: dane.ul, ds: dane.ds, m2: dane.m2, temat: String(msg.getSubject() || '').slice(0, 200), wiad: [] };
          wynik.nowe++;
        } else {
          dodane++;
          if (!d.tel || !d.m2 || !d.ul || !d.ds) { const dn = katMailDane(msg.getSubject(), x); d.tel = d.tel || dn.tel; d.m2 = d.m2 || dn.m2; d.ul = d.ul || dn.ul; d.ds = d.ds || dn.ds; }
        }
        d.wiad.push({ ts: kiedy.getTime(), od: od.n, em: od.em, x: x, zal: katMailZalaczniki(msg, d.kl, kiedy), mid: mid, gid: gid });
        d.ost = Math.max(Number(d.ost) || 0, kiedy.getTime());
        znane[gid] = 1; if (mid) znane[mid] = 1;
        zm = true;
      });
      if (zm) {
        d.wiad.sort(function (a, b) { return a.ts - b.ts; });
        katMailPrzytnij(d);
        zmiany.push({ id: id, d: d, opis: katMailOpis(d) });
        wynik.dopisane += rec ? dodane : 0;
        th.addLabel(etOk);
      } else if (!d) { th.addLabel(etPom); wynik.pominiete++; }
      else th.addLabel(etOk);                          /* wątek znany, nic nowego (np. ten sam mail drugi raz) */
      th.moveToArchive();
    }
    if (zmiany.length) katMailZapisz(ss, sh, zmiany);
    return wynik;
  } finally {
    lockI.releaseLock();
  }
}

/* URUCHOMIĆ RAZ W EDYTORZE: wyzwalacz co 5 min + pierwsze pobranie */
function katalogMaileUstaw() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'katalogPobierzMaile') ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('katalogPobierzMaile').timeBased().everyMinutes(5).create();
  Logger.log('Wyzwalacz co 5 min założony. Pierwsze pobranie: ' + JSON.stringify(katalogPobierzMaile()));
}
/* wyłączenie (gdyby Artur zrezygnował) */
function katalogMaileWylacz() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'katalogPobierzMaile') ScriptApp.deleteTrigger(t); });
  Logger.log('Wyzwalacz maili usunięty.');
}

/* zdjęcie / PDF z maila dla aplikacji: tylko pliki zapisane przy pozycjach e-mail (lista z arkusza); miniatura albo całość */
function katZal(id, mini) {
  id = String(id || '');
  if (!/^[\w-]{20,80}$/.test(id)) return { ok: false, blad: 'Złe ID pliku' };
  const sh = katSS().getSheetByName(KAT_MAIL_ARK);
  if (!sh) return { ok: false, blad: 'Brak pliku' };
  let z = null;
  const m = katCzytaj(sh);
  Object.keys(m).some(function (k) { return ((m[k].d || {}).wiad || []).some(function (w) { return (w.zal || []).some(function (a) { if (a.id === id) { z = a; return true; } return false; }); }); });
  if (!z) return { ok: false, blad: 'Brak pliku' };
  const f = DriveApp.getFileById(id);
  if (z.t === 'p') return { ok: true, url: f.getUrl(), n: z.n };
  const c = CacheService.getScriptCache(), kc = 'katMini_' + id;
  if (mini) {
    const zc = c.get(kc);
    if (zc) return { ok: true, typ: 'image/jpeg', b64: zc, mini: true };
    let t = null;
    try { t = f.getThumbnail(); } catch (e) { t = null; }
    if (t && t.getBytes().length > 500) {
      const b64 = Utilities.base64Encode(t.getBytes());
      try { if (b64.length < 95000) c.put(kc, b64, 21600); } catch (e) {}
      return { ok: true, typ: t.getContentType() || 'image/jpeg', b64: b64, mini: true };
    }
  }
  const bl = f.getBlob();
  return { ok: true, typ: bl.getContentType() || 'image/jpeg', b64: Utilities.base64Encode(bl.getBytes()), url: f.getUrl(), n: z.n };
}

/* TEST bez wysyłania maili: pozycja przykładowa m_TEST (zdjęcie = kopia pierwszego JPG z Dysku) i jej usunięcie */
function katalogMaileTest() {
  const kiedy = new Date(), ss = katSS(), sh = katMaileArk(ss);
  const temat = 'TEST 48 m² Warszawa Mokotów';
  const x = 'Dzień dobry, proszę o wycenę cyklinowania i lakierowania parkietu, ok. 48 m2, ul. Puławska 182 m. 14, Mokotów. Tel. 512 000 000.\nPozdrawiam';
  const dane = katMailDane(temat, x), zal = [];
  try {
    const pl = DriveApp.searchFiles("mimeType = 'image/jpeg' and trashed = false");
    if (pl.hasNext()) { const f = pl.next().makeCopy('TEST e-mail - do usunięcia.jpg', katMailFolder(kiedy)); zal.push({ id: f.getId(), n: 'test.jpg', t: 'z', b: f.getSize() }); }
  } catch (e) { Logger.log('bez zdjęcia: ' + e); }
  const d = { typ: 'e', ts: kiedy.getTime(), ost: kiedy.getTime(), kl: 'TEST Jan Testowy', em: 'test@example.com', tel: dane.tel, ul: dane.ul, ds: dane.ds, m2: dane.m2, temat: temat,
    wiad: [{ ts: kiedy.getTime(), od: 'TEST Jan Testowy', em: 'test@example.com', x: x, zal: zal, mid: 'test', gid: 'test' }] };
  katMailZapisz(ss, sh, [{ id: 'm_TEST', d: d, opis: katMailOpis(d) }]);
  Logger.log('Dodano pozycję testową m_TEST: ' + JSON.stringify(dane) + ', zdjęć: ' + zal.length);
}
function katalogMaileTestUsun() {
  const ss = katSS(), sh = katMaileArk(ss), m = katCzytaj(sh), A = katArkusze(ss);
  const lock = LockService.getScriptLock(); lock.waitLock(25000);
  try {
    if (m.m_TEST) {
      ((m.m_TEST.d || {}).wiad || []).forEach(function (w) { (w.zal || []).forEach(function (a) { try { DriveApp.getFileById(a.id).setTrashed(true); } catch (e) {} }); });
      katZapiszRekordy(sh, [{ id: 'm_TEST', d: null }]);
    }
    if (katCzytaj(A.status).m_TEST) katZapiszRekordy(A.status, [{ id: 'm_TEST', d: null }]);
    const kal = katCzytaj(A.kal);
    katZapiszRekordy(A.kal, Object.keys(kal).filter(function (k) { return kal[k].d && kal[k].d.zid === 'm_TEST'; }).map(function (k) { return { id: k, d: null }; }));
    const gr = katCzytaj(A.grafik);
    katZapiszRekordy(A.grafik, Object.keys(gr).filter(function (k) { return gr[k].d && gr[k].d.zid === 'm_TEST'; }).map(function (k) { return { id: k, d: null }; }));
    const u = katUstCzytaj(A.ust); katUstZapisz(A.ust, 'rev', Number(u.rev || 0) + 1);
  } finally { lock.releaseLock(); }
  Logger.log('Pozycja testowa usunięta.');
}
