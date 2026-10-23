# CLAUDE.md

Repozitorij sadrži **dvije odvojene stvari**:

## 1. `jalics/` — gotova statička PWA aplikacija (glavni artefakt)
Interaktivni vodič kroz kontemplativne duhovne vježbe (Franz Jalics), svih 10
vremena. Na hrvatskom. Ovo je **funkcionalna aplikacija koja se deploya**, ne
maketa. Puni opis (ekrani, stanje, dizajn tokeni, podatkovni model) je u
`jalics/README.md`.

Ključno:
- `jalics/index.html` — cijela aplikacija (Design Component: template + logika).
  Ranije se zvala `Vodič kroz kontemplacije.dc.html`.
- `jalics/support.js` — DC runtime (potreban; ne mijenjati).
- `jalics/data/vremena.json` — sav tekstualni sadržaj (~730 KB).
- `jalics/manifest.webmanifest`, `jalics/sw.js`, `jalics/icons/` — PWA
  (instalacija na početni zaslon + offline).

**Bitna pravila:**
- Sve datoteke u `jalics/` moraju ostati **zajedno u istoj mapi** — manifest i
  service worker koriste relativni `scope`/`start_url` (`./`).
- Aplikacija koristi `fetch('data/vremena.json')`, pa mora ići preko **HTTP-a**,
  ne `file://`. Lokalno: `cd jalics && npx serve .` (ili `python3 -m http.server`).
- **PWA install** (`beforeinstallprompt` na Chrome/Androidu, upute na iOS-u) i
  service worker rade **samo preko HTTPS-a** (ili `localhost`).

- Nakon **svake promjene** `index.html`, `support.js` ili `data/vremena.json`
  podići verziju za 0.1 (2.3 → 2.4) na **dva mjesta**: `appVersion` u
  `index.html` (broj + datum, prikazuje se na dnu početnog zaslona:
  „Verzija 2.3 · 23. 10. 2026.“) i `CACHE` u `jalics/sw.js` (`kontempl-2.3`).
  Promjena `CACHE` briše staru predmemoriju. Service worker je *network-first* za
  vlastite datoteke (offline pada na predmemoriju), pa korisnici novu verziju
  dobiju već pri sljedećem učitavanju.
- **Tamni okvir (trake sustava):** `theme-color` meta (svijetla/tamna po
  `prefers-color-scheme`, JS ih usklađuje s ručno odabranom temom), tamna
  varijanta u `manifest.webmanifest` (`user_preferences`) i skripta u `<head>`
  koja prepozna Chrome Auto Dark (klasa `auto-tamno` → tamna pozadina
  `#14120f`). Isto rješenje kao u projektu behealed_tree.
  `theme_color` u manifestu **namjerno nema**: donja traka instalirane
  aplikacije uzima ga iz manifesta (samo jedna vrijednost), a bez njega prati
  temu mobitela. Promjena manifesta do instalirane aplikacije stiže tek kad
  Chrome osvježi WebAPK (do nekoliko dana; najbrže: deinstalirati i ponovno
  instalirati). U CSS komentarima ne pisati oznake tagova (npr. `</style>`).

### Poveznice (dijeljenje)
Svaki ekran ima adresu u `#` dijelu URL-a (npr.
`https://kmagdic.github.io/ktpl/jalics/#/uvod/8`):
`#/uvod[/N]`, `#/prirucnik`, `#/vrijeme/N[/nagovor|vjezba|razgovori|osvrt]`,
`#/vrijeme/N/nagovor/K` (odjeljak nagovora), `#/vrijeme/N/razgovori/K`
(otvoren razgovor), `#/vjezba/N` (= vježba vremena N), `#/oznake`. Logika je u
`routeHash`/`applyHash`/`syncHash` u `index.html`: adresa se ažurira dok se
korisnik kreće (novi ekran = novi unos u povijesti, pa radi Natrag), a pri
otvaranju se skače na sidro (`uvod-N`, `nag-K`, `razg-K`). Gumbi s ikonom
lanca dijele poveznicu (mobitel: sustavni izbornik za dijeljenje; računalo:
kopira u međuspremnik). `#app` je rezerviran za testiranje standalone načina.

### Oznake teksta (highlight)
Korisnik odabere dio teksta → plutajući gumb *Označi* (dodir na oznaku →
*Ukloni oznaku*); odabir se proširuje na cijele riječi, može preko više
odlomaka. Spremanje: `localStorage.jalics_highlights` =
`{ [id]: [[od, do, "isječak"], …] }`. ID odlomka: nagovor `v2.n4.p0`
(vrijeme 0-indeks, odjeljak, odlomak), smjernice `v9.n1.l2[.s3]`, razgovor
`v2.r1.t0` (replika), osvrt `v2.o.p0|q0|a0`, Uvod `u.i0` / `u.s8.p3`.
Odlomak u DOM-u ima `id="hl-<id>"`, označeni dio `class="hl-mark"` (**DC
predložak ne propušta `data-*` atribute** na običnim elementima — koristiti
`id`/`class`). Ako se tekst promijeni (nova lektura → novi indeksi ili riječi),
oznaka se traži po isječku; ako ga nema, ne prikazuje se u tekstu, a u
„Moje oznake“ (`#/oznake`) piše da se tekst promijenio. Zato pri novom uvozu
teksta ne mijenjati redoslijed odlomaka bez potrebe.

### Sadržaj knjige → `vremena.json`
Izvor teksta je **lektorirano izdanje** knjige (Zaklada biskup Josip Lang,
2026.), PDF u `nagovori/` (InDesign izvoz, tekst se čisto izvlači).
`vremena.json` se **generira skriptom**, ne uređuje se ručno:

```sh
python3 scripts/pdf_to_vremena.py "nagovori/<knjiga>.pdf" --report /tmp/report.txt
```
- Treba `pdftotext` (poppler: `brew install poppler`). Zadano čita i piše
  `jalics/data/vremena.json` (`--old`, `--out` za druge putanje).
- Ista skripta piše i **`jalics/data/uvod.json`** (`--uvod-out`): Uvod knjige
  (str. 17–34) — `{title, intro[], introNotes?[], sections[{num, heading,
  paras, notes?[{n, text}]}]}`. Naslovi odjeljaka provjeravaju se prema
  sadržaju (TOC); fusnote se skupljaju s dna stranica, a oznake u tekstu
  (`vježbi1`) postaju superskript (`vježbi¹`) redom 1, 2, 3… Prikazuje se na
  ekranu Uvod (sitna poveznica „Uvod u knjigu“ ispod gumba Priručnik i u
  izborniku — namjerno neupadljivo); na vrhu je sadržaj uvoda s poveznicama
  na odjeljke, a ispod svakog odjeljka „↑ Sadržaj uvoda“.
- Skripta prepoznaje strukturu knjige: `PRVO … DESETO VRIJEME`, `I. NAGOVOR:`
  + naslov, odjeljci `N. Naslov`, `II. UPUTE ZA …`, `III. (OPROŠTAJNI)
  RAZGOVORI` s `N.M. IME`, replike `Govornik: …` (i `Ime (napomena): …`),
  `IV. OSVRT …` s pitanjima `• …`. Odlomci se prepoznaju po uvlaci prvog retka
  (`pdftotext -layout`); riječi rastavljene na kraju retka se spajaju; navodnici
  se ujednačuju na hrvatske „…“.
- Iz postojećeg JSON-a (`--old`) zadržava polja kojih **nema u knjizi**:
  `key/index/title`, `summary` odjeljaka nagovora, naslove `numbered` smjernica
  (10. vrijeme, koriste se i u Priručniku), cijeli `osvrt` 10. vremena.
  `display` i `summary` razgovora generiraju se iz novog teksta.
- **Uvijek pregledati izvještaj** (`--report` ili stdout): promjene naslova,
  imena i broja razgovora, ispravljeni tipfeleri govornika (npr. „Helana“ →
  „Helena“), neuravnoteženi navodnici. Skripta je vezana uz izgled ovog PDF-a;
  novo izdanje drugačijeg prijeloma može zahtijevati doradu regexa.
- Poznate greške u PDF-u (2026.): tipfeleri govornika Helana, Luitz, Kaehe,
  Voditele (skripta ih ispravlja); nedostaje zatvoreni navodnik u citatu
  Mk 10 („Zašto me zoveš dobrim?, reče mu Isus.“, 7. vrijeme) — ostavljeno.

### Podatkovni model (sažetak; puni opis u `jalics/README.md`)
- `nagovor[]`: `{heading, paras, summary?, numbered?}`; `upute[]`:
  `{heading, paras}` (trenutno se ne prikazuju — Vježba koristi `flows` iz
  `index.html`).
- `razgovori[]`: `{name, display, summary, turns[{speaker, text}]}`; replika
  može imati više odlomaka odvojenih `\n\n` (prikaz `white-space:pre-line`).
- `osvrt`: `{paras, questions, parasAfter?}` — `parasAfter` je tekst koji u
  knjizi slijedi nakon pitanja i prikazuje se ispod njih.
- U `index.html` su ručno pisani i nisu iz knjige: `flows` (vođene vježbe),
  `summaries`, `osvrtSummaries`, `essences`, slike — pri promjeni sadržaja
  provjeriti jesu li još u skladu s tekstom.

### Višejezičnost
Nije napravljena. Aplikacija je samo na hrvatskom; UI tekstovi i `flows` su
tvrdo kodirani u `index.html`. Za drugi jezik: izdvojiti UI tekstove, dodati
`vremena.<jezik>.json` (ista struktura) i prekidač jezika, proširiti `sw.js`.

## 2. `src/` + `package.json` + `tsconfig.json` — TypeScript reimplementacija
Mjesto za reimplementaciju Jalics aplikacije u TypeScriptu (opcija 2 iz
`jalics/README.md`: koristiti DC datoteke kao high-fidelity referencu). Zasad je
**prazan scaffold** (`src/index.ts` samo logira poruku), rad još nije započet.
- Build: `npm run build` (`tsc` → `dist/`).
- Pri reimplementaciji, sadržaj i logika se preslikavaju iz `jalics/` (finalne
  boje/tipografija/interakcije + `jalics/data/vremena.json`).
