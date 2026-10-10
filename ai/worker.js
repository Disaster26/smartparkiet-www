/**
 * SMARTEXPERT ONLINE - rozpoznawanie zdjec podlogi.
 *
 * Czemu przez wlasny serwer, a nie wprost z przegladarki: klucz do modelu nie
 * moze lezec w kodzie strony, bo kazdy by go wyciagnal i przepalil limit.
 * Ten worker trzyma klucz u siebie i wpuszcza tylko ruch, ktory przeszedl
 * przez trzy bramki:
 *   1. Turnstile (darmowa kontrola "czy to czlowiek", bez klikania w obrazki),
 *   2. limit na adres IP   - domyslnie 5 analiz na dobe,
 *   3. limit globalny      - domyslnie 200 analiz na dobe, zeby jeden zapalony
 *                            gosc albo bot nie wyczyscil calego darmowego limitu.
 * Do tego twarde sprawdzenie rozmiaru i typu pliku.
 *
 * Model: Gemini 2.5 Flash (darmowy poziom Google AI Studio). Prompt wymusza
 * odpowiedz w JSON i - co najwazniejsze po uwadze Artura z 10.10 - pozwala
 * modelowi powiedziec "nie wiem". Lepiej brak odpowiedzi niz zmyslony gatunek.
 *
 * Wdrozenie: patrz README.md w tym katalogu.
 */

const LIMIT_IP = 5;
const LIMIT_DOBA = 200;
const MAX_BAJTOW = 4 * 1024 * 1024;
const TYPY = ['image/jpeg', 'image/png', 'image/webp'];

const PROMPT = `Jesteś doświadczonym parkieciarzem. Oceniasz zdjęcie podłogi drewnianej
przysłane przez klienta telefonem. Odpowiadasz wyłącznie w formacie JSON, po polsku.

Pola:
  "czy_podloga": true/false  - czy na zdjęciu w ogóle widać podłogę drewnianą
  "gatunek": krótko, np. "dąb", "jesion", "merbau", "deska warstwowa dębowa" lub "nie wiem"
  "uklad": "klepka", "jodełka", "mozaika", "deska" lub "nie wiem"
  "stan": jedno zdanie o tym, co widać: rysy, przetarcia, szczeliny, zacieki, odbarwienia
  "zalecenie": jedno zdanie, co zwykle się w takim wypadku robi
  "pewnosc": "wysoka", "średnia" albo "niska"
  "uwaga": jedno zdanie dla klienta, jeśli zdjęcie jest za ciemne, rozmazane albo zrobione zbyt daleko

Zasady, od których nie wolno odstąpić:
- Jeśli czegoś nie da się stwierdzić ze zdjęcia, wpisz "nie wiem" i ustaw pewnosc na "niska".
  Zmyślona odpowiedź jest gorsza niż jej brak.
- Nie podawaj cen ani terminów.
- Nie pisz nic poza obiektem JSON.`;

function dzis() {
  return new Date().toISOString().slice(0, 10);
}

function odp(dane, status = 200) {
  return new Response(JSON.stringify(dane), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'no-store',
    },
  });
}

async function licznik(env, klucz, limit) {
  const teraz = parseInt((await env.LIMITY.get(klucz)) || '0', 10);
  if (teraz >= limit) return false;
  // doba z sekundowym zapasem, zeby klucz sam znikal
  await env.LIMITY.put(klucz, String(teraz + 1), { expirationTtl: 60 * 60 * 26 });
  return true;
}

async function czlowiek(env, token, ip) {
  if (!env.TURNSTILE_SECRET) return true; // tryb bez Turnstile, tylko do testow
  const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST',
    body: new URLSearchParams({ secret: env.TURNSTILE_SECRET, response: token || '', remoteip: ip }),
  });
  const j = await r.json();
  return !!j.success;
}

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
        },
      });
    }
    if (request.method !== 'POST') return odp({ blad: 'tylko POST' }, 405);

    const ip = request.headers.get('CF-Connecting-IP') || '0.0.0.0';
    let ciało;
    try {
      ciało = await request.json();
    } catch (e) {
      return odp({ blad: 'zly format zgloszenia' }, 400);
    }

    if (!(await czlowiek(env, ciało.turnstile, ip))) {
      return odp({ blad: 'weryfikacja nie przeszla, prosze odswiezyc strone' }, 403);
    }
    if (!(await licznik(env, `g:${dzis()}`, LIMIT_DOBA))) {
      return odp({ blad: 'dzienny limit analiz wyczerpany, prosze wyslac zdjecia mailem' }, 429);
    }
    if (!(await licznik(env, `ip:${ip}:${dzis()}`, LIMIT_IP))) {
      return odp({ blad: `na dzis limit ${LIMIT_IP} analiz z tego urzadzenia` }, 429);
    }

    const obraz = String(ciało.obraz || '');
    const m = obraz.match(/^data:(image\/[a-z+]+);base64,(.+)$/);
    if (!m || !TYPY.includes(m[1])) return odp({ blad: 'dozwolone sa pliki JPG, PNG i WEBP' }, 415);
    const bajtow = Math.floor((m[2].length * 3) / 4);
    if (bajtow > MAX_BAJTOW) return odp({ blad: 'zdjecie wieksze niz 4 MB' }, 413);

    const url = `https://generativelanguage.googleapis.com/v1beta/models/${
      env.MODEL || 'gemini-2.5-flash'
    }:generateContent?key=${env.GEMINI_KEY}`;

    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              { text: PROMPT },
              { inline_data: { mime_type: m[1], data: m[2] } },
            ],
          },
        ],
        generationConfig: { temperature: 0.2, responseMimeType: 'application/json' },
      }),
    });

    if (!r.ok) {
      return odp({ blad: 'model chwilowo nie odpowiada, parkieciarz obejrzy zdjecia recznie' }, 502);
    }
    const j = await r.json();
    const tekst = j?.candidates?.[0]?.content?.parts?.[0]?.text || '{}';
    let wynik;
    try {
      wynik = JSON.parse(tekst);
    } catch (e) {
      return odp({ blad: 'nie udalo sie odczytac odpowiedzi modelu' }, 502);
    }
    if (wynik.czy_podloga === false) {
      return odp({ blad: 'na zdjeciu nie widac podlogi drewnianej, prosze o inne ujecie' }, 422);
    }
    return odp({ ok: true, wynik });
  },
};
