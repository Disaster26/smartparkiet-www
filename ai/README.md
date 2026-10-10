# SMARTEXPERT ONLINE - rozpoznawanie zdjec

Rozpoznawanie gatunku i stanu podlogi ze zdjecia klienta. Model siedzi za wlasnym
serwerem (Cloudflare Worker), zeby klucz nie lezal w kodzie strony i zeby dalo sie
ograniczyc zuzycie.

## Co jest potrzebne (jednorazowo, po stronie wlasciciela konta)

1. **Klucz do modelu** - Google AI Studio, darmowy poziom: aistudio.google.com/apikey
   Gemini 2.5 Flash ma darmowy limit dzienny wystarczajacy na kilkaset zdjec.
2. **Konto Cloudflare** (darmowe) i `npm i -g wrangler`.
3. **Turnstile** (darmowe, w panelu Cloudflare) - klucz publiczny do strony
   i sekret do workera. To zamiast captchy: klient zwykle nic nie klika.

## Wdrozenie

```
cd ai
wrangler login
wrangler kv namespace create LIMITY        # ID wkleic do wrangler.toml
wrangler secret put GEMINI_KEY
wrangler secret put TURNSTILE_SECRET
wrangler deploy
```

Po wdrozeniu adres workera (np. `https://smartexpert-analiza.<konto>.workers.dev`)
wpisac w `wycena.html` w stalej `ANALIZA_URL`, a klucz publiczny Turnstile
w `TURNSTILE_KEY`. Dopoki `ANALIZA_URL` jest puste, strona dziala bez modelu:
zdjecie sie pokazuje, wycena liczy sie z cennika, a podloge oglada parkieciarz.

## Zabezpieczenia (to byla osobna prosba)

| Co | Gdzie | Wartosc domyslna |
| --- | --- | --- |
| limit na jedno urzadzenie | `LIMIT_IP` w worker.js | 5 analiz na dobe |
| limit calego serwisu | `LIMIT_DOBA` | 200 analiz na dobe |
| maksymalny plik | `MAX_BAJTOW` | 4 MB |
| dozwolone typy | `TYPY` | JPG, PNG, WEBP |
| kontrola "czy czlowiek" | Turnstile | wymagana, jesli ustawiony sekret |

Liczniki leza w KV i same wygasaja po dobie. Po przekroczeniu limitu klient
dostaje komunikat, a nie bialy ekran: "prosze wyslac zdjecia mailem".

## Dlaczego model moze powiedziec "nie wiem"

Prompt wprost na to pozwala i kaze obnizyc pewnosc. Po uwadze Artura z 10.10.2026
("czesciej sie myli niz mowi prawde") lepiej pokazac "nie wiem" niz zmyslony
gatunek, bo klient i tak dostaje ocene czlowieka w ciagu dwoch godzin.
