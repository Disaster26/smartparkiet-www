/* SMARTPARKIET Katalog - service worker: powloka aplikacji z pamieci (praca bez internetu w trybie podgladu).
   Dane (Apps Script) nie ida przez cache - aplikacja trzyma ostatni stan sama. Zmiana wersji = nowa nazwa C. */
var C = 'spk-aplikacja-v1';
var PLIKI = ['./', './manifest.webmanifest', './img/logo-96.png', './img/favicon.png', './img/apple-touch-icon.png', './img/ikona-192.png'];
self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(C).then(function (c) { return c.addAll(PLIKI); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (k) {
    return Promise.all(k.filter(function (x) { return x.indexOf('spk-aplikacja-') === 0 && x !== C; }).map(function (x) { return caches.delete(x); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var req = e.request, u = new URL(req.url), baza = new URL('./', self.registration.scope).pathname;
  if (req.method !== 'GET' || u.origin !== location.origin || u.pathname.indexOf(baza) !== 0) return;
  /* strona: najpierw siec (zawsze najnowsza wersja), bez sieci - kopia */
  if (req.mode === 'navigate' || u.pathname === baza || /\.html$/.test(u.pathname)) {
    e.respondWith(fetch(req).then(function (r) {
      if (r.ok) { var k = r.clone(); caches.open(C).then(function (c) { c.put('./', k); }); }
      return r;
    }).catch(function () { return caches.match('./'); }));
    return;
  }
  /* ikony, manifest: z pamieci, w tle odswiezane */
  e.respondWith(caches.match(req).then(function (hit) {
    var siec = fetch(req).then(function (r) { if (r.ok) { var k = r.clone(); caches.open(C).then(function (c) { c.put(req, k); }); } return r; });
    return hit || siec;
  }));
});
