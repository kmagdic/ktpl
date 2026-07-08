# Handoff: Interaktivni vodič — Kontemplativne duhovne vježbe (Franz Jalics)

## Pregled
Web-aplikacija koja korisnika vodi kroz duhovne vježbe iz knjige Franza Jalicsa
»Kontemplativne duhovne vježbe« — svih **10 vremena** (poglavlja). Za svako
vrijeme: sažetak, nagovor (poučni tekst), **vođena vježba** korak-po-korak s
tajmerom tišine i zvučnim signalom, razgovori (dijalozi voditelj ↔ egzercitant),
i osvrt s pitanjima + osobnim bilješkama. Sve na hrvatskom. Miran, kontemplativan
vizualni ton.

## O datotekama u ovom paketu
Ovo je **gotova, funkcionalna statička web-aplikacija** (nije samo maketa).
Napisana je kao **Design Component (DC)** — jedan `.dc.html` koji pokreće mali
runtime (`support.js`) i sadržaj učitava iz `data/vremena.json`.

Developer ima dvije mogućnosti:
1. **Deploy kakva jest** (najbrže) — vidi »Pokretanje i deploy« niže. Radi na
   bilo kojem statičkom hostingu.
2. **Reimplementacija u postojećem codebaseu** (React/Vue/SwiftUI/…) — koristi
   ove datoteke kao *high-fidelity referencu* (finalne boje, tipografija, raspored,
   interakcije) i podatke iz `data/vremena.json`. Logika i sadržaj su ovdje
   potpuni i mogu se preslikati.

## Fidelity
**High-fidelity.** Boje, tipografija, razmaci i interakcije su finalni.

## Pokretanje i deploy
Aplikacija koristi `fetch('data/vremena.json')`, pa mora ići preko HTTP-a
(ne `file://`). Lokalno:
```
cd design_handoff_kontemplacije
npx serve .        # ili: python3 -m http.server
```
Otvori prikazani URL. Datoteka s dijakritikom u imenu (`Vodič…`) radi, no radi
jednostavnijih URL-ova preporuka je preimenovati ulaznu datoteku u npr.
`index.html` prije deploya.

**Deploy:** upload cijele mape na bilo koji statički host (Netlify, Vercel,
GitHub Pages, Cloudflare Pages, S3…). Sve tri datoteke (`.dc.html`, `support.js`,
`data/vremena.json`) moraju ostati zajedno u istom relativnom rasporedu.
Slike se dohvaćaju s Unsplasha (hotlink, besplatna licenca) — potreban je internet.

## Struktura / Ekrani
Aplikacija je jedno-stranična; `state.view` bira ekran.

### 1. `home` — Naslovnica
- **Hero** (puna širina, `min(64vh,600px)`): fotografija (zora nad planinom),
  tamni gradijent preko nje, centrirani naslov »Kontemplativne duhovne vježbe«
  (Cormorant Garamond 600, `clamp(40px,7.5vw,68px)`, `#fbf7ee`), podnaslov
  »Franz Jalics · Deset vremena« (italic).
- **Uvodni odlomak** (max-width 760, centriran, `#544d42`, 18px).
- **10 kartica** (stack, gap 14px). Svaka: lijevo slika 120px (cover) s brojem
  01–10 preko nje (Cormorant, bijelo), desno naslov (Cormorant 24) + esencija
  (`#7a7161`, 15px, clamp 2 retka). Fiksna visina **110px**, hover: podizanje +
  sjena + blagi zoom slike. Oznaka »dovršeno« (žalfija `#6d795c`) ako je vrijeme
  označeno gotovim.
- Gumb **»Priručnik — sve vježbe na jednom mjestu«** (isprekidani obrub, akcent).
- Preklopnik zvučnog signala; napomena o spremanju na uređaju.

### 2. `vrijeme` — Pojedino vrijeme
- **Banner** (`min(46vh,420px)`): tematska fotografija + gradijent; gore lijevo
  gumb »Sadržaj« (staklasti), dolje »VRIJEME 0X« (eyebrow) + naslov (Cormorant 600).
- **Ljepljiva traka** (sticky, papirnata, blur): red s brojem+naslovom vremena
  (uvijek vidljivo u kojem si vremenu) i ispod tabovi:
  **Nagovor · Vođena vježba · Razgovori · Osvrt** (aktivni: tinta + akcentna donja crta).
- **Nagovor:** diskretan »Sažetak« (lijevi obrub, mali italic `#7a7161`), zatim
  numerirani pododjeljci — broj (akcent) + naslov (Cormorant 600 `#8a4e2d`) +
  odlomci (18px, `#3f3930`).
- **Vođena vježba:** uvod (italic), kartice pripreme, »Nakana« (lijevi akcentni
  obrub), tamni panel s biračem trajanja tišine (− / +) i gumbima »Započni vođenu
  vježbu« / »Preskoči na samu tišinu«, te napomena o ponavljanjima.
- **Razgovori:** akordeoni; zaglavlje = ime osobe (Cormorant, VELIKA) + diskretan
  sažetak o čemu priča (`#a59a86`, 12.5px). Otvaranjem: izmjena govornika
  (Voditelj / ime), akcentna oznaka govornika + tekst.
- **Osvrt:** diskretan sažetak, prozni tekst, pitanja (kartice s točkom),
  textarea za bilješke (spremaju se), gumb »Označi kao dovršeno« i »Prijeđi na
  sljedeće vrijeme«.

### 3. `prirucnik` — Priručnik (uvijek dostupan)
Pregled svih 10 vježbi za praćenje bez čitanja. Po vremenu kartica: broj+naslov+
trajanje, esencija, »Priprema« i »Fokus«, glavna uputa (italic), gumbi »Vježbaj«
(pokreće session odmah) i »Otvori vrijeme«.

### 4. `session` — Vođena meditacija (tamni način)
- Pozadina: `#1c1a16` + zamućena tematska slika (opacity 0.16) + radijalni gradijent.
- Faze: **guide** (korak-po-korak, auto-tempo; naslov koraka + veliki tekst
  Cormorant), **silence** (veliki tajmer mm:ss; kod višeblokovnih vremena »Termin
  1/2« + pauza 5 min), **done** (zvonce + poziv na osvrt).
- Ambijentalni »orb« (pulsirajući radijalni akcent, 9s) — NIJE naredba za disanje
  (Jalics: disanje se ne kontrolira).
- Kontrole: traka napretka, prev / play-pause / next, »Preskoči vođenje — u tišinu«.
- Na kraju termina/pauze nježan **WebAudio zvon** (poštuje postavku zvuka).

## Interakcije i stanje
- **Tajmer:** jedan `setInterval(1s)` → `tick()`; grananje po fazi (guide auto-advance
  / silence odbrojavanje / pauza). `guidePace` (prop) skalira trajanje koraka.
- **Napredak & bilješke:** `localStorage`
  - `jalics_progress` = `{ [key]: { done:boolean, note:string, practiced:boolean } }`
  - `jalics_settings` = `{ sound:boolean }`
- **Slike (bitno za reimplementaciju):** DC streama markup prije hidracije, pa je
  hero URL tvrdo kodiran, a kartice/banner/session koriste prozirni 1×1 GIF u
  `src` + pravu adresu u `data-src`, koju `syncImgs()` prebaci u `src` nakon
  rendera. U React/Vue codebaseu ovo nije potrebno (nema tog streaminga) — samo
  postavi `src` normalno.

## Podatkovni model — `data/vremena.json`
Niz od 10 objekata (redoslijed = redoslijed poglavlja):
```jsonc
{
  "key": "prvo", "index": 1, "title": "Prvo vrijeme",
  "nagovorTitle": "Što su to duhovne vježbe?",
  "nagovor":  [ { "heading": "Snaga prirode"|null, "paras": ["…"] } ],
  "upute":    [ { "heading": "…", "paras": ["…"] } ],
  "razgovori":[ { "name": "BARBARA", "display": "Barbara",
                  "summary": "Još nisam došla k sebi.",
                  "turns": [ { "speaker": "Voditelj"|"Barbara", "text": "…" } ] } ],
  "osvrt":    { "paras": ["…"], "questions": ["…"] }
}
```
Vođene vježbe (koraci, tempo, trajanja, tekst tišine) NISU u JSON-u — kurirane su
u logici DC-a kao `this.flows[]` (jedan po vremenu, indeks odgovara JSON-u).
`summaries[]`, `osvrtSummaries[]`, `essences[]`, `imgs[]`, `imgsCard[]` također su
u logici, poravnati po indeksu.

## Dizajnerski tokeni
Boje:
- Papir/pozadina: `#efe8da`; površina/kartica: `#fbf7ee`
- Tinta (tekst): `#2b2620`; tamniji naslov: `#3a342b` / `#8a4e2d`; tijelo: `#3f3930`
- Mutna: `#7a7161`; vrlo mutna: `#a59a86` / `#8a7f6d`
- Akcent (terakota): `#a8623a` (hover `#b56d43`, svjetliji `#e6a071`, eyebrow `#f2c9a6`)
- Žalfija (dovršeno): `#6d795c`
- Tamni »session«: pozadina `#1c1a16`, tekst `#ece5d6` / `#f4ecdc`, mutno `#a89e8b`/`#8f8676`
- Obrubi: `rgba(43,38,32,0.10–0.14)`

Tipografija (Google Fonts):
- Display/naslovi: **Cormorant Garamond** (500/600, italic 500)
- Tekst/UI: **Spectral** (300/400/500/600, italic 400)
- Skale: hero `clamp(40px,7.5vw,68px)`; naslov vremena `clamp(30px,5.5vw,46px)`;
  session korak `clamp(26px,5vw,38px)`; tajmer `clamp(64px,17vw,112px)`; tijelo 18px.

Ostalo: border-radius 4–6px; kartica-sjena `0 14px 36px -20px rgba(43,38,32,0.5)`;
prijelazi 0.2–0.6s; animacije `fadeUp`, `softIn`, `orbPulse` (9s).

## Props (tweakovi na root DC-u)
- `ambientOrb` (boolean, default true) — prikaz pulsirajućeg orba u sessionu.
- `soundDefault` (boolean, default true) — početno stanje zvučnog signala.
- `guidePace` (enum `spor`|`uobičajen`|`brz`, default `uobičajen`) — skalira
  trajanje koraka vođenja (×1.4 / ×1 / ×0.7).
- `appChrome` (enum `auto`|`uvijek`|`nikad`, default `auto`) — mobilni okvir
  (gornja traka + donja navigacija). `auto` = uključen samo u standalone/PWA modu.

## PWA — instalabilna aplikacija (kao kadigrahrvatska.hr)
Paket sadrži `manifest.webmanifest`, `sw.js` i `icons/` pa se aplikacija može
**instalirati na početni zaslon** (mobitel i desktop) i radi offline.
- Naslovnica ima gumb **»Instaliraj aplikaciju«**. Na Androidu/Chromeu koristi
  `beforeinstallprompt` (native dijalog); na iOS-u/Safariju prikaže kratke upute
  (Podijeli → Dodaj na početni zaslon).
- Kad se pokrene kao instalirana app (`display-mode: standalone`), UI se prebaci
  u **mobilni okvir**: gornja traka (hamburger izbornik + naslov + zvuk), donja
  navigacijska traka (Početna / Priručnik / Vremena) i bočni ladica-izbornik sa
  svim vremenima. Isto se može forsirati propom `appChrome:'uvijek'` ili URL-om
  `…#app` (korisno za demo u browseru).
- **Bitno za hosting:** service worker i manifest rade samo preko **HTTPS-a**
  (ili `localhost`) i s ispravnim `scope`/`start_url` (`./`). Drži sve datoteke
  u istoj mapi. Ikone su placeholder (motiv: prsten + terakota točka) —
  zamijeni pravima po želji (192, 512, 512-maskable, apple-touch 180).
- SW se registrira samo izvan iframe-a i na `https:`, da ne smeta u editor-pregledu.

## Napomena o standalone HTML-u
Zbog veličine sadržaja (`vremena.json` ~730 KB) aplikacija se poslužuje kao mala
mapa (fetch preko HTTP-a), a ne kao jedna .html datoteka. PWA instalacija ionako
zahtijeva zaseban `manifest`+`sw.js` na hostu, pa je »mapa na statičkom hostu«
ispravan format za web i za instalaciju.

## Asseti
- Fotografije: **Unsplash** (besplatna licenca), hotlinkane u logici
  (`heroImg`, `imgs[]`, `imgsCard[]`). Za produkciju razmisli o preuzimanju i
  posluživanju s vlastitog CDN-a (+ optimizacija veličina).
- Zvuk: generiran u kodu (WebAudio, sinusni zvon) — nema audio datoteka.
- Ikone: inline SVG (stroke = currentColor).
- Fontovi: Google Fonts (`Cormorant Garamond`, `Spectral`).

## Datoteke u paketu
- `Vodič kroz kontemplacije.dc.html` — cijela aplikacija (template + logika).
- `support.js` — DC runtime (potreban; ne mijenjati).
- `data/vremena.json` — sav tekstualni sadržaj (nagovori, upute, razgovori, osvrti).
- `manifest.webmanifest`, `sw.js`, `icons/` — PWA (instalacija + offline).

## Izvor sadržaja
Tekst je izvučen iz PDF-a knjige. Ako se u nekom nagovoru pojavi sitna
tipografska pogreška iz izvornika, ispravlja se u `data/vremena.json`
(polje `nagovor[].paras`).
