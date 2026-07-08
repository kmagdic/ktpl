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

## 2. `src/` + `package.json` + `tsconfig.json` — TypeScript reimplementacija
Mjesto za reimplementaciju Jalics aplikacije u TypeScriptu (opcija 2 iz
`jalics/README.md`: koristiti DC datoteke kao high-fidelity referencu). Zasad je
**prazan scaffold** (`src/index.ts` samo logira poruku), rad još nije započet.
- Build: `npm run build` (`tsc` → `dist/`).
- Pri reimplementaciji, sadržaj i logika se preslikavaju iz `jalics/` (finalne
  boje/tipografija/interakcije + `jalics/data/vremena.json`).
