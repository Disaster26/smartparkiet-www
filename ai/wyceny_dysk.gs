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
  try { f.addEditor(ARTUR); } catch (e) {}
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
function rejestr(a, kiedy, url) {
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
  sh.getRange(2, 1, 1, 8).setValues([[kiedy, a.imie || '', a.tel || '', a.adres || '', a.m2 || '',
    Math.round((a.suma || 0) * 100) / 100, a.termin || '', url]]);
}

function czysc(t) {
  return String(t || '').replace(/[\/:*?"<>|\n\r]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120);
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
    if (d.arkusz) {
      const a = d.arkusz;
      const tytul = String.fromCodePoint(0x1F4CD) + ' ' + czysc((a.ulica || a.imie || a.tel || 'wycena') + ' ' + kiedy.slice(0, 10));
      const url = arkuszWyceny(folder, tytul, a, kiedy);
      rejestr(a, kiedy, url);
    }
    const mail = String(d.mailKlienta || '').trim();
    const mailOk = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(mail);
    if (d.ofertaKlientowi && mailOk && d.pdf) {
      MailApp.sendEmail({
        to: mail,
        replyTo: ARTUR,
        name: 'SMARTPARKIET',
        subject: 'Oferta renowacji parkietu - SMARTPARKIET',
        body: 'Dzień dobry,\n\nw załączniku przesyłamy ofertę renowacji parkietu przygotowaną na podstawie przesłanych informacji i zdjęć. ' +
          'Na ostatniej stronie znajdą Państwo zasady renowacji.\n\n' +
          'W razie pytań albo chęci ustalenia terminu prosimy o kontakt: 602 242 815 lub odpowiedź na tę wiadomość.\n\n' +
          'Pozdrawiamy\nSMARTPARKIET\nCyklinowanie SMART™',
        attachments: [Utilities.newBlob(Utilities.base64Decode(d.pdf), 'application/pdf', d.nazwaPdf || 'Oferta_SMARTPARKIET.pdf')]
      });
    } else if (POTWIERDZENIE && mailOk) {
      MailApp.sendEmail({
        to: mail,
        replyTo: ARTUR,
        name: 'SMARTPARKIET',
        subject: 'Otrzymaliśmy Państwa zgłoszenie do wyceny - SMARTPARKIET',
        body: 'Dzień dobry,\n\ndziękujemy za przesłanie zgłoszenia do bezpłatnej wyceny SMARTPARKIET. ' +
          'Parkieciarz obejrzy zdjęcia i odezwie się z wyceną w ciągu dwóch godzin roboczych.\n\n' +
          'W razie pytań: 602 242 815.\n\nPozdrawiamy\nSMARTPARKIET\nCyklinowanie SMART™'
      });
    }
    return ContentService.createTextOutput(JSON.stringify({ ok: true, plik: nazwa }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, blad: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  return ContentService.createTextOutput('SMARTPARKIET wyceny - dziala');
}

/* uruchomic raz recznie w edytorze (Uruchom -> start): pyta o wszystkie uprawnienia i zaklada folder */
function start() {
  const f = glownyFolder();
  try { f.addEditor(ARTUR); } catch (e) {}
  Logger.log('Folder: ' + f.getUrl() + ' | limit maili: ' + MailApp.getRemainingDailyQuota());
}
