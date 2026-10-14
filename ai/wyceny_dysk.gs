/* SMARTPARKIET - kazda oferta z kalkulatora zapisuje sie na Dysku Google
   i klient dostaje krotkie potwierdzenie z konta SMARTPARKIET (bez cen).

   Wdrozenie (raz, na koncie Gmail SMARTPARKIET, najlepiej na komputerze):
   1. script.google.com -> Nowy projekt -> usun wszystko i wklej ten plik -> zapisz.
   2. Wdroz -> Nowe wdrozenie -> typ: Aplikacja internetowa,
      Wykonaj jako: Ja, Kto ma dostep: Kazdy -> Wdroz.
   3. Zezwol na dostep (Dysk i wysylanie maili z tego konta).
   4. Skopiuj adres konczacy sie na /exec i przeslij go Lukaszowi. */

const FOLDER = 'SMARTPARKIET - wyceny';
const POTWIERDZENIE = true;   // false = klient nie dostaje maila z potwierdzeniem

function folderMiesiaca() {
  const it = DriveApp.getFoldersByName(FOLDER);
  const glowny = it.hasNext() ? it.next() : DriveApp.createFolder(FOLDER);
  const nazwa = Utilities.formatDate(new Date(), 'Europe/Warsaw', 'yyyy-MM');
  const pod = glowny.getFoldersByName(nazwa);
  return pod.hasNext() ? pod.next() : glowny.createFolder(nazwa);
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
    const mail = String(d.mailKlienta || '').trim();
    if (POTWIERDZENIE && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(mail)) {
      MailApp.sendEmail({
        to: mail,
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
