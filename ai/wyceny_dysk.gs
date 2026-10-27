/* SMARTPARKIET - kazda oferta z kalkulatora zapisuje sie na Dysku Google:
   PDF + osobny arkusz Google z wycena + wiersz w zbiorczym arkuszu "Rejestr wycen"
   (Artur 15.10: "zeby miec latwy przeglad"). Klient dostaje krotkie potwierdzenie
   z konta SMARTPARKIET (bez cen), a gdy wycene wysyla parkieciarz z zaznaczonym
   "Wyslij klientowi oferte PDF" - mail z oferta PDF w zalaczniku (Artur 20.10 18:05).

   Wdrozenie (raz, na koncie Gmail SMARTPARKIET, najlepiej na komputerze):
   1. script.google.com -> Nowy projekt -> usun wszystko i wklej ten plik -> zapisz.
   2. Wdroz -> Nowe wdrozenie -> typ: Aplikacja internetowa,
      Wykonaj jako: Ja, Kto ma dostep: Kazdy -> Wdroz.
   3. Zezwol na dostep (Dysk, Arkusze i wysylanie maili z tego konta).
   4. Skopiuj adres konczacy sie na /exec i przeslij go Lukaszowi. */

const FOLDER = 'SMARTPARKIET - wyceny';
const POTWIERDZENIE = true;   // false = klient nie dostaje maila z potwierdzeniem
/* 21.10: skrypt dziala na koncie pomocniczym (panbet77) - odpowiedzi klientow ida do Artura,
   a folder z wycenami jest mu udostepniony do edycji */
const ARTUR = 'smartparkiet.kontakt@gmail.com';
/* 21.10 Artur oglada rejestr z konta smartparkiet@gmail.com - dostep dla obu adresow */
const ARTUR_WSZYSTKIE = ['smartparkiet.kontakt@gmail.com', 'smartparkiet@gmail.com'];

/* Artur 22.10: folder wszystkich wyslanych ofert w "otwartej formie" - kazda wycena zapisuje
   sie tez jako komplet pol formularza + zdjecia, zeby mozna ja bylo wczytac w analizatorze
   (z telefonu albo laptopa), zmienic jedna kwote i wyslac klientowi poprawiona. */
const FOLDER_POPRAWKI = 'Oferty do poprawki (nie usuwac)';
/* PIN analizatora we wlasciwosciach skryptu (Ustawienia projektu -> Wlasciwosci skryptu: PIN), nie w kodzie */
function pinAnalizatora() { return PropertiesService.getScriptProperties().getProperty('PIN') || ''; }
/* 22.10 Artur: haslo slowne (BORYS / KROL), kilka hasel po przecinku, wielkosc liter bez znaczenia */
function hasloOk(h) {
  const lista = pinAnalizatora().split(',').map(function (x) { return x.trim().toUpperCase(); }).filter(String);
  return lista.length > 0 && lista.indexOf(String(h || '').trim().toUpperCase()) >= 0;
}

function folderPoprawek() {
  const g = glownyFolder();
  const it = g.getFoldersByName(FOLDER_POPRAWKI);
  return it.hasNext() ? it.next() : g.createFolder(FOLDER_POPRAWKI);
}

/* klucz do listy ofert trzymany we wlasciwosciach skryptu, nie w kodzie strony */
function kluczListy() {
  const p = PropertiesService.getScriptProperties();
  let k = p.getProperty('KLUCZ_LISTY');
  if (!k) { k = Utilities.getUuid().replace(/-/g, ''); p.setProperty('KLUCZ_LISTY', k); }
  return k;
}

function json(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function folderMiesiaca() {
  const glowny = glownyFolder();
  const nazwa = Utilities.formatDate(new Date(), 'Europe/Warsaw', 'yyyy-MM');
  const pod = glowny.getFoldersByName(nazwa);
  return pod.hasNext() ? pod.next() : glowny.createFolder(nazwa);
}

function glownyFolder() {
  const it = DriveApp.getFoldersByName(FOLDER);
  if (it.hasNext()) return it.next();
  const f = DriveApp.createFolder(FOLDER);
  ARTUR_WSZYSTKIE.forEach(function (m) { try { f.addEditor(m); } catch (e) {} });
  return f;
}

/* osobny arkusz Google na kazda wycene, w tym samym folderze miesiaca co PDF */
function arkuszWyceny(folder, nazwa, a, kiedy) {
  const ss = SpreadsheetApp.create(nazwa);
  const sh = ss.getActiveSheet();
  sh.setName('Wycena');
  const dane = [
    ['SMARTPARKIET - wstępna oferta renowacji parkietu', ''],
    ['Data', kiedy],
    ['Klient', a.imie || ''],
    ['Telefon', a.tel || ''],
    ['E-mail', a.mail || ''],
    ['Adres', a.adres || ''],
    ['Obiekt', a.obiekt || ''],
    ['Podłoga', a.rodzaj || ''],
    ['Wykończenie', a.technika || ''],
    ['Termin', a.termin || ''],
    ['Uwagi', a.uwagi || '']
  ];
  sh.getRange(1, 1, dane.length, 2).setValues(dane);
  sh.getRange(1, 1).setFontWeight('bold').setFontSize(14).setFontColor('#FE6500');
  sh.getRange(2, 1, dane.length - 1, 1).setFontWeight('bold').setFontColor('#4A5058');
  const start = dane.length + 2;
  sh.getRange(start, 1, 1, 4).setValues([['Pozycja', 'Ilość', 'Cena jedn. (zł)', 'Wartość (zł)']])
    .setFontWeight('bold').setBackground('#FE6500').setFontColor('#FFFFFF');
  const poz = (a.poz || []).filter(p => p[1] !== 0 && p[1] !== '0');
  poz.forEach((p, i) => {
    const w = start + 1 + i;
    sh.getRange(w, 1, 1, 3).setValues([[p[0], p[1], p[2] === null ? '' : p[2]]]);
    sh.getRange(w, 4).setFormula('=IF(AND(ISNUMBER(B' + w + '),ISNUMBER(C' + w + ')),B' + w + '*C' + w + ',"")');
  });
  const wSuma = start + 1 + poz.length;
  sh.getRange(wSuma, 3).setValue('Razem netto').setFontWeight('bold');
  sh.getRange(wSuma, 4).setFormula('=SUM(D' + (start + 1) + ':D' + (wSuma - 1) + ')').setFontWeight('bold');
  sh.getRange(start + 1, 3, poz.length + 1, 2).setNumberFormat('#,##0.00');
  sh.setColumnWidth(1, 330); sh.setColumnWidth(2, 90); sh.setColumnWidth(3, 130); sh.setColumnWidth(4, 130);
  SpreadsheetApp.flush();
  DriveApp.getFileById(ss.getId()).moveTo(folder);
  return ss.getUrl();
}

/* jeden zbiorczy arkusz: wiersz na kazda wycene, najnowsze na gorze */
function rejestr(a, kiedy, url, idStanu) {
  const g = glownyFolder();
  const it = g.getFilesByName('Rejestr wycen');
  let ss;
  if (it.hasNext()) ss = SpreadsheetApp.open(it.next());
  else {
    ss = SpreadsheetApp.create('Rejestr wycen');
    ss.getActiveSheet().getRange(1, 1, 1, 8)
      .setValues([['Data', 'Klient', 'Telefon', 'Adres', 'm²', 'Kwota netto (zł)', 'Termin', 'Arkusz']])
      .setFontWeight('bold').setBackground('#FE6500').setFontColor('#FFFFFF');
    ss.getActiveSheet().setFrozenRows(1);
    DriveApp.getFileById(ss.getId()).moveTo(g);
  }
  const sh = ss.getSheets()[0];
  sh.insertRowAfter(1);
  /* 21.10 Artur: nowe wiersze dziedziczyly pomaranczowy naglowek, a gole adresy nie otwieraly sie w aplikacji Arkusze */
  const w = sh.getRange(2, 1, 1, 9);
  w.setBackground(null).setFontColor('#1A1A1A').setFontWeight('normal');
  w.setValues([[kiedy, a.imie || '', a.tel || '', a.adres || '', a.m2 || '',
    Math.round((a.suma || 0) * 100) / 100, a.termin || '', '', '']]);
  /* 22.10: formula HYPERLINK z przecinkiem dawala #ERROR! w arkuszu z polskimi ustawieniami - link wpisany w tekst komorki */
  sh.getRange(2, 8).setRichTextValue(link('Otwórz arkusz', url));
  if (idStanu) {
    if (!sh.getRange(1, 9).getValue()) sh.getRange(1, 9).setValue('Popraw i wyślij ponownie')
      .setFontWeight('bold').setBackground('#FE6500').setFontColor('#FFFFFF');
    sh.getRange(2, 9).setRichTextValue(link('Otwórz w analizatorze', 'https://smartparkiet.com.pl/analizator.html#oferta=' + idStanu));
  }
}

/* jednorazowo: poprawia stare wiersze rejestru (kolor + klikalne linki). Uruchomic recznie z edytora. */
function naprawRejestr() {
  const it = glownyFolder().getFilesByName('Rejestr wycen');
  if (!it.hasNext()) return;
  const sh = SpreadsheetApp.open(it.next()).getSheets()[0];
  const n = sh.getLastRow();
  if (n < 2) return;
  sh.getRange(2, 1, n - 1, 9).setBackground(null).setFontColor('#1A1A1A').setFontWeight('normal');
  /* stare wiersze: gole adresy albo formuly HYPERLINK (#ERROR! przy polskich ustawieniach) -> link w tekscie */
  [8, 9].forEach(function (k) {
    if (sh.getLastColumn() < k) return;
    const zakres = sh.getRange(2, k, n - 1, 1);
    const f = zakres.getFormulas(), v = zakres.getValues();
    for (let i = 0; i < n - 1; i++) {
      const m = String(f[i][0] || '').match(/HYPERLINK\("([^"]+)"[,;]\s*"([^"]*)"\)/i);
      const u = m ? m[1] : String(v[i][0] || '');
      if (/^https?:\/\//.test(u)) sh.getRange(i + 2, k).setRichTextValue(link(m ? m[2] : 'Otwórz arkusz', u));
    }
  });
  const g = glownyFolder();
  ARTUR_WSZYSTKIE.forEach(function (m) { try { g.addEditor(m); } catch (e) {} });
}

function link(tekst, url) {
  return SpreadsheetApp.newRichTextValue().setText(tekst).setLinkUrl(url).build();
}

function czysc(t) {
  return String(t || '').replace(/[\/:*?"<>|\n\r]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120);
}

/* 21.10 Artur: mail w stylistyce stopki strony (czarny, pomaranczowy, bialy), numer do klikniecia */
function mailHtml(akapity) {
  const p = akapity.map(t => '<p style="margin:0 0 14px">' + t.replace('602 242 815',
    '<a href="tel:+48602242815" style="color:#FE6500;font-weight:700;text-decoration:none">602 242 815</a>') + '</p>').join('');
  return '<div style="background:#F4EFE9;padding:24px 12px;font-family:Arial,Helvetica,sans-serif">' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;border-collapse:collapse">' +
    '<tr><td style="background:#14110E;padding:18px 24px;border-bottom:3px solid #FE6500">' +
      '<img src="https://smartparkiet.com.pl/img/logo-znak.png" width="30" height="30" alt="" style="vertical-align:middle;border:0">' +
      '<span style="vertical-align:middle;margin-left:10px;color:#fff;font-size:18px;font-weight:800;letter-spacing:.06em">SMART<span style="color:#FE6500">PARKIET</span></span></td></tr>' +
    '<tr><td style="background:#ffffff;padding:26px 24px 12px;color:#1F2328;font-size:15px;line-height:1.6">' +
      '<p style="margin:0 0 14px">Dzień dobry,</p>' + p +
      '<p style="margin:18px 0 0">Pozdrawiamy</p></td></tr>' +
    '<tr><td style="background:#ffffff;padding:6px 24px 26px">' +
      '<a href="tel:+48602242815" style="display:inline-block;background:#FE6500;color:#ffffff;font-weight:700;font-size:15px;text-decoration:none;padding:12px 22px;border-radius:4px">Zadzwoń: 602 242 815</a></td></tr>' +
    '<tr><td style="background:#14110E;padding:20px 24px;color:#DDD5CB;font-size:13px;line-height:1.6">' +
      '<div style="color:#ffffff;font-weight:800;letter-spacing:.08em;font-size:14px">SMARTPARKIET TREMBIŃSKI</div>' +
      '<div>Artur | <a href="tel:+48602242815" style="color:#FE6500;font-weight:700;text-decoration:none">602 242 815</a></div>' +
      '<div><a href="https://smartparkiet.com.pl" style="color:#DDD5CB;text-decoration:none">smartparkiet.com.pl</a> &middot; Cyklinowanie SMART&trade;</div>' +
    '</td></tr></table></div>';
}

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents);
    const kiedy = Utilities.formatDate(new Date(), 'Europe/Warsaw', 'yyyy-MM-dd HH-mm');
    const nazwa = czysc(kiedy + ' ' + (d.opis || 'wycena')) + '.pdf';
    const folder = folderMiesiaca();
    if (d.pdf) {
      folder.createFile(Utilities.newBlob(Utilities.base64Decode(d.pdf), 'application/pdf', nazwa));
    }
    let idStanu = '';
    if (d.stan) try {
      const opisStanu = czysc(kiedy + ' ' + (d.opis || 'wycena'));
      const plikStanu = folderPoprawek().createFile(opisStanu + '.json',
        JSON.stringify({ kiedy: kiedy, opis: d.opis || '', mailKlienta: d.mailKlienta || '', stan: d.stan, zdjecia: d.zdjecia || [] }),
        'application/json');
      plikStanu.setDescription(opisStanu);
      idStanu = plikStanu.getId();
    } catch (e) { console.error('folder poprawek: ' + e); }
    /* 22.10: blad arkusza/rejestru nie moze zablokowac maila do klienta (tak bylo 16:01-16:20) */
    if (d.arkusz) {
      try {
        const a = d.arkusz;
        const tytul = String.fromCodePoint(0x1F4CD) + ' ' + czysc((a.ulica || a.imie || a.tel || 'wycena') + ' ' + kiedy.slice(0, 10));
        const url = arkuszWyceny(folder, tytul, a, kiedy);
        rejestr(a, kiedy, url, idStanu);
      } catch (e) { console.error('arkusz/rejestr: ' + e); }
    }
    const mail = String(d.mailKlienta || '').trim();
    const mailOk = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(mail);
    if (d.ofertaKlientowi && mailOk && d.pdf) {
      const akapity = ['w załączniku przesyłamy ofertę renowacji parkietu przygotowaną na podstawie przesłanych informacji i zdjęć. Na ostatniej stronie znajdą Państwo zasady renowacji.',
        'W razie pytań albo chęci ustalenia terminu prosimy o kontakt telefoniczny lub odpowiedź na tę wiadomość.'];
      MailApp.sendEmail({
        to: mail,
        bcc: ARTUR, /* Artur 22.10: kopia maila do klienta w jego skrzynce */
        replyTo: ARTUR,
        name: 'SMARTPARKIET',
        subject: d.temat || 'Oferta renowacji parkietu - SMARTPARKIET', /* Artur 26.10 21:57: temat od adresu (budowany w wycena.html) */
        body: 'Dzień dobry,\n\n' + akapity.join('\n\n') + '\n\nPozdrawiamy\nSMARTPARKIET TREMBIŃSKI\nArtur | 602 242 815',
        htmlBody: mailHtml(akapity),
        attachments: [Utilities.newBlob(Utilities.base64Decode(d.pdf), 'application/pdf', d.nazwaPdf || 'Oferta_SMARTPARKIET.pdf')]
      });
    } else if (POTWIERDZENIE && mailOk) {
      /* 21.10 Artur: jego tresc, w zalaczniku karta z kalkulacja */
      const akapity = ['dziękujemy za zainteresowanie ofertą naszej firmy. W załączniku przesyłamy naszą wstępną kalkulację online.',
        'Prosimy o potwierdzenie otrzymania i zapraszamy do kontaktu telefonicznego pod numerem 602 242 815.'];
      /* 27.10 Artur: zamowienie online (zamow-online.html) - dopisek o preferowanych terminach do potwierdzenia */
      if (d.zamowienie) akapity.splice(1, 0, 'Państwa preferowany termin' + (d.terminy ? ' (' + d.terminy + ')' : '') + ' został przesłany do centrali SMARTPARKIET. Potwierdzimy jego dostępność SMS-em lub e-mailem w ciągu maksymalnie 2 godzin roboczych. Termin staje się wiążący dopiero po potwierdzeniu przez centralę SMART.');
      MailApp.sendEmail({
        to: mail,
        bcc: ARTUR, /* Artur 22.10: kopia maila do klienta w jego skrzynce */
        replyTo: ARTUR,
        name: 'SMARTPARKIET',
        subject: d.temat || 'Wstępna wycena renowacji parkietu - SMARTPARKIET', /* Artur 26.10 21:57: temat od adresu */
        body: 'Dzień dobry,\n\n' + akapity.join('\n\n') + '\n\nPozdrawiamy\nSMARTPARKIET TREMBIŃSKI\nArtur | 602 242 815',
        htmlBody: mailHtml(akapity),
        attachments: d.pdf ? [Utilities.newBlob(Utilities.base64Decode(d.pdf), 'application/pdf', d.nazwaPdf || 'Wstepna_wycena_SMARTPARKIET.pdf')] : []
      });
    }
    return json({ ok: true, plik: nazwa, id: idStanu });
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, blad: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/* analizator: ?a=klucz&pin=..  ->  klucz do listy (po 20 blednych PIN-ach blokada na godzine)
               ?a=lista&k=..   ->  wszystkie zapisane oferty, najnowsze na gorze
               ?a=wczytaj&id=..&k=..  ->  pola formularza i zdjecia jednej oferty */
function doGet(e) {
  const p = (e && e.parameter) || {};
  if (p.a === 'klucz') {
    const c = CacheService.getScriptCache();
    const bledy = Number(c.get('bledyPin') || 0);
    if (bledy >= 20) return json({ ok: false, blad: 'Za dużo prób, spróbuj za godzinę.' });
    if (!hasloOk(p.pin)) { c.put('bledyPin', String(bledy + 1), 3600); return json({ ok: false, blad: 'Zły PIN' }); }
    return json({ ok: true, k: kluczListy() });
  }
  if (p.a === 'lista' || p.a === 'wczytaj') {
    if (String(p.k || '') !== kluczListy()) return json({ ok: false, blad: 'Brak dostępu' });
    if (p.a === 'wczytaj') {
      const f = DriveApp.getFileById(String(p.id || ''));
      if (f.getParents().next().getName() !== FOLDER_POPRAWKI) return json({ ok: false, blad: 'Brak dostępu' });
      return json({ ok: true, oferta: JSON.parse(f.getBlob().getDataAsString()) });
    }
    const lista = [];
    const it = folderPoprawek().getFiles();
    while (it.hasNext()) {
      const f = it.next();
      lista.push({ id: f.getId(), opis: f.getDescription() || f.getName().replace(/\.json$/, ''), t: f.getDateCreated().getTime() });
    }
    lista.sort(function (x, y) { return y.t - x.t; });
    return json({ ok: true, lista: lista.slice(0, 300) });
  }
  return ContentService.createTextOutput('SMARTPARKIET wyceny - dziala');
}

/* uruchomic raz recznie w edytorze (Uruchom -> start): pyta o wszystkie uprawnienia i zaklada folder */
function start() {
  const f = glownyFolder();
  try { f.addEditor(ARTUR); } catch (e) {}
  Logger.log('Folder: ' + f.getUrl() + ' | limit maili: ' + MailApp.getRemainingDailyQuota());
}
