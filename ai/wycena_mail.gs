/* SMARTPARKIET - wysylka zgloszen z kalkulatora (Google Apps Script).
   Wdrozenie: script.google.com -> Nowy projekt -> wklej -> Wdroz -> Nowe wdrozenie
   -> Aplikacja internetowa, Wykonaj jako: ja, Dostep: kazdy -> skopiuj adres /exec
   do stalej APPS_URL w wycena.html. */
const DO = 'artur.trembinski@gmail.com';
const KOPIA = 'odrobimy@gmail.com';   // kopia na czas testow, potem usunac

function esc(t) {
  return String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents);
    const inline = {};
    const zal = [];
    let kom = '';
    (d.zdjecia || []).slice(0, 6).forEach(function (z, i) {
      const b = Utilities.newBlob(Utilities.base64Decode(z.dane), 'image/jpeg', 'zdjecie_' + (i + 1) + '.jpg');
      inline['z' + i] = b;
      zal.push(b);
      kom += '<td style="padding:4px;width:50%;vertical-align:top">' +
        '<img src="cid:z' + i + '" alt="Zdjęcie ' + (i + 1) + '" style="width:100%;max-width:330px;border-radius:6px;display:block"></td>' +
        (i % 2 ? '</tr><tr>' : '');
    });
    if (d.karta) zal.unshift(Utilities.newBlob(Utilities.base64Decode(d.karta), 'image/jpeg', 'KARTA_WYCENY.jpg'));

    const wiersze = (d.pola || []).map(function (p, i) {
      return '<tr style="background:' + (i % 2 ? '#ffffff' : '#F6F1EA') + '">' +
        '<td style="padding:10px 14px;color:#6B5E52;width:120px;vertical-align:top;font-size:14px">' + esc(p[0]) + '</td>' +
        '<td style="padding:10px 14px;color:#14110E;font-size:15px;font-weight:600">' + esc(p[1]) + '</td></tr>';
    }).join('');

    const wierszeKl = (d.pola || []).filter(function (p) { return p[0] !== 'Zlecenie' && p[0] !== 'Zdjęcia'; }).map(function (p, i) {
      return '<tr style="background:' + (i % 2 ? '#ffffff' : '#F6F1EA') + '"><td style="padding:8px 12px;color:#6B5E52">' + esc(p[0]) +
        '</td><td style="padding:8px 12px;font-weight:600">' + esc(p[1]) + '</td></tr>';
    }).join('');

    const html =
      '<div style="font-family:Arial,Helvetica,sans-serif;max-width:680px;margin:0 auto;color:#14110E">' +
      '<div style="background:#E8671F;color:#ffffff;padding:16px 20px;font-size:20px;font-weight:bold;border-radius:6px 6px 0 0">' +
      'SMARTPARKIET · nowa prośba o wycenę</div>' +
      '<table style="width:100%;border-collapse:collapse">' + wiersze + '</table>' +
      (kom ? '<div style="padding:18px 0 6px;font-size:16px;font-weight:bold">Zdjęcia od klienta</div>' +
        '<table style="width:100%;border-collapse:collapse"><tr>' + kom + '</tr></table>' : '') +
      '<p style="font-size:13px;color:#6B5E52;margin-top:18px">W załącznikach: karta wyceny do wydruku i zdjęcia w pełnym rozmiarze. ' +
      'Odpowiedź na tego maila trafi prosto do klienta.</p></div>';

    const opcje = {
      to: DO, subject: d.temat || 'Nowa wycena', htmlBody: html,
      inlineImages: inline, attachments: zal, name: 'SMARTPARKIET kalkulator'
    };
    if (KOPIA) opcje.cc = KOPIA;
    if (d.mailKlienta) opcje.replyTo = d.mailKlienta;
    MailApp.sendEmail(opcje);

    if (d.mailKlienta) {
      MailApp.sendEmail({
        to: d.mailKlienta, name: 'SMARTPARKIET',
        subject: 'Otrzymaliśmy Państwa zdjęcia do wyceny - SMARTPARKIET',
        htmlBody: '<div style="font-family:Arial,Helvetica,sans-serif;max-width:620px;color:#14110E;font-size:15px;line-height:1.6">' +
          '<p>Dzień dobry,</p><p>dziękujemy za przesłanie zdjęć podłogi. Parkieciarz obejrzy je i odezwie się z wyceną w ciągu dwóch godzin roboczych.</p>' +
          '<table style="border-collapse:collapse;margin:10px 0">' + wierszeKl + '</table>' +
          '<p>W razie pytań: 602 242 815.</p><p>Pozdrawiamy,<br>SMARTPARKIET</p></div>'
      });
    }
    return ContentService.createTextOutput(JSON.stringify({ ok: true })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, blad: String(err) })).setMimeType(ContentService.MimeType.JSON);
  }
}
