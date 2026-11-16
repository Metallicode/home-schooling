# Plan: turning the activity library into a product for schools

Status: planning, nothing implemented yet. Last updated 2026-10-28.

## Decisions so far

- **Hosted, not an on-site box** (decided 2026-10-28). The user first considered an Intel NUC
  on each school's network (Ubuntu 24.04, local hostname, outbound tunnel for maintenance,
  auto-updating containers) as a selling point: no outbound traffic, no security worries.
  A hosted setup can make nearly the same promise (see Hosting below) without hardware.
  The same build must still run on a box unchanged, so an on-site option can be sold later.
- **New project for schools.** This repo stays the family home-schooling site. The user will
  go through the activities, drop the ones not needed, and start a separate repo for the
  schools product. Copy this plan into that repo.
- **Leave `potato_head.html` exactly as it is** in this repo. The user's children like it the
  way it is.

## Goal

Formalise the current collection of activities into a product that can be pitched to
local UK schools (England and Wales), including Welsh-medium schools. Two features
drive the work:

1. **Language selection**: full Welsh interface, with Welsh reading and phonics content.
2. **School theming**: each school can apply its own colours (uniform colours), name and
   logo to the index and activity pages.

Both need the same groundwork: a shared core that every activity loads. Today there is none.

## Current state (reviewed 2026-10-27)

- 66 standalone HTML files, no build step, no shared JS or CSS. Every file has its own
  inline `<style>` and `<script>`.
- English text is hard-coded in the HTML and the JS. Every file has `<html lang="en">`.
  Most activities have only 5-25 visible strings; `index.html` has about 290 (card titles
  and descriptions).
- Colours are hard-coded: 2,599 hex values (285 unique). Only 6 files use CSS variables.
- Fonts are mostly Comic Sans MS / Courier New system fonts. Comic Sans is not installed on
  Chromebooks, so what pupils see varies by device.
- Audio is static files in `sounds/` (letter sounds, `nato/`, `googol/`, `globe/`). The NATO
  clips used edge-tts with a US voice (`en-US-JennyNeural`); UK schools should get en-GB.
- `localStorage` is used only for index favourites and recent activities, plus one level in
  `skyline_equalizer`. No accounts and no data sent to a server.
- External calls: three.js, MediaPipe and Tone MIDI from public CDNs, plus `globe.html`
  fetches map data from GitHub via jsDelivr. `quantum_conductor.html` uses the camera
  for hand tracking, processed on the device.
- 64 of 66 activities link back to `index.html`.

## How each group of activities is affected by Welsh

| Group | Examples | Welsh effort |
|---|---|---|
| Little language (maths art, music, most maths) | `pi`, `pascal`, `harp`, `rhythm_blocks`, `fibonacci`, `volume`, `geometry_*` | Translate labels only |
| Generated sentences | `comprehension*`, `fruit_count`, `clock`, `time` | One whole-sentence template per language; no gluing fragments (Welsh mutations and plural rules) |
| Number words | `googol_engine`, `add_and_mul` | Welsh number-to-words (modern decimal counting, e.g. *un deg un*) plus Welsh audio |
| Phonics and early reading | `letters`, `astro_letters`, `consonants`, `pop_phonics`, `vowel_validator`, `word_families*`, `first_reading`, `story_reading`, `verbs` | **Rewrite, not translate.** 29-letter alphabet with digraphs (ch, dd, ff, ng, ll, ph, rh, th), no k/q/v/x/z, w and y as vowels. Needs a Welsh-medium phonics specialist |
| English-specific | `NATO`, `type` | Keep the content in English; translate instructions only |

## Target architecture

A small shared core, loaded by every page, with no build step (so pages still open
straight from disk or from any static host).

```
core/
  config.js        school settings: name, logo, colours, default language, enabled activities
  i18n.js          language detection (?lang= > saved choice > school default > en), t(), data-i18n
  theme.js         applies school colours as CSS variables, checks text contrast
  theme.css        design tokens (--color-primary, --color-surface, --font-body, ...) and shared
                   chrome: header, back link, buttons
  activities.js    activity registry: id, file, subject, age range, which languages it supports
locales/
  en.js, cy.js     interface strings, as JS files (window.LOCALES.cy = {...}); fetch() of JSON
                   fails when a page is opened from disk
content/
  en/, cy/         stories, word lists, phonics sets; same shape per language
sounds/
  en/, cy/         audio per language
schools/
  example.js       one config file per school (colours, logo, language, activity list)
```

Key decisions:

- **Activity registry drives the index.** The index is generated from `activities.js`
  instead of 290 hand-written strings. That gives one place for translations, lets a school
  hide activities (e.g. the camera one), and lets the index show only activities that
  support the chosen language.
- **Theme the chrome, not the activities' inner palettes.** School colours apply to the
  index, headers, buttons, back links and backgrounds. Colours inside activities that carry
  meaning (maths art, colour-coded feedback, correct/wrong) stay fixed.
- **Contrast safety.** School colours are often low-contrast (e.g. yellow). `theme.js`
  picks black or white text automatically and keeps WCAG 2.2 AA contrast; public sector
  buyers expect it.
- **One bundled font** with full Welsh glyphs (ŵ, ŷ) and child-friendly letterforms,
  replacing Comic Sans, so every device shows the same thing. Candidates: Andika (SIL,
  built for early readers) or Lexend. To decide.
- **Use the browser's built-in language tools**: `Intl.PluralRules('cy')`, `Intl.NumberFormat`.
- **Audio**: number and word clips via edge-tts with `cy-GB-NiaNeural` / `cy-GB-AledNeural`
  and `en-GB` voices, checked by a native speaker. Single phonics sounds recorded by a
  Welsh speaker.

## Hosting

The pitch the hosted setup must make true:

> UK-hosted. One web address to allow through your filter. No logins, no pupil data,
> no tracking, no adverts, and no calls to any third-party service.

- **UK hosting**: a small UK-region server (e.g. AWS London, Azure UK South, or a UK host).
  Host not chosen yet.
- **Caddy** serves the files and handles HTTPS certificates automatically.
- **One subdomain per school** (e.g. `ysgol-x.yourco.co.uk`), all served from the same build
  plus that school's file in `schools/`. Domain not bought yet.
- **No third-party calls**: self-host three.js, MediaPipe, Tone MIDI and the globe map data.
- **Access logs off or anonymised**: IP addresses count as personal data under UK GDPR.
- **One domain to allow**: school IT adds `*.yourco.co.uk` to the web filter.
- **Deploys**: automatic on push to the main branch, with a staging subdomain checked first.
  A deploy is a set of static files, so rollback is redeploying the previous version.
- **Onboarding pack per school**: domain to allow, DPIA template, privacy notice, one-page
  safeguarding statement.

## Order of work

0. **Audit (user)**: go through the activities in this repo, choose which go into the schools
   product, and create the new repo.
1. **Hosting groundwork**: domain, UK server, Caddy, per-school subdomains, automatic
   deploys, staging. Needs the user to choose the host and buy the domain.
2. **Shared core**: `core/` (config, i18n, theme, registry), generated index with a language
   switch and theming, one maths activity converted end to end. Does not depend on the host,
   so it can start first.
3. **No third-party calls**: self-host libraries and map data; decide whether the camera
   activity stays, and if so make it opt-in per school (it needs HTTPS, which hosting gives).
4. **Onboarding pack**, and update the executive summary with the UK-hosted,
   no-third-party wording.
5. **Convert the remaining activities**: maths art, music and maths first (labels and colour
   tokens, mostly mechanical), then generated-sentence and number activities (sentence
   templates, Welsh number words).
6. **Welsh reading and phonics content**, with a Welsh-medium specialist.
7. **Polish**: accessibility pass, bundled font, en-GB audio.

## Open questions for planning the use case

- **Who is the first customer?** English primary vs Welsh-medium primary changes the order
  of phases (Welsh-medium needs phase 4 before a pilot is credible).
- **Who sets the theme**: we configure each school, or a simple settings page a teacher can use?
- **Curriculum mapping**: tag activities against the England National Curriculum and the
  Curriculum for Wales (Areas of Learning and Experience). Needed for the pitch.
- **Progress tracking**: none today, which keeps the privacy story simple but means no
  evidence for schools. Any tracking must stay on the device or come with a DPIA.
- **Bilingual mode**: Welsh only, or Welsh and English side by side (common in English-medium
  schools in Wales)?
- **Pricing and licensing**: per school, per trust, or free pilot then annual licence?

## Related

- Executive summary pitch for UK schools (Claude Docs):
  https://claude.ai/artifact/6qjc4QPBcsfkQFkVYd124v. Its "validated scheme" wording is
  England-specific; a Welsh version needs Curriculum for Wales language.
