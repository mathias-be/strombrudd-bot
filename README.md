# Strømbrudd-bot – Fredrikstad, Hvaler og Råde

En liten bot som varsler i Slack når det er strømbrudd i Fredrikstad, Hvaler eller Råde, og som samtidig lagrer alle brudd i en historikk slik at du kan se **hvor det er mest strømbrudd** over tid.

Boten kjører gratis på **GitHub Actions** (hvert 10. minutt), så du trenger ingen server og ingen maskin som må stå på.

## Hva den gjør

- Henter pågående strømbrudd fra nettselskapenes egne kart hvert 10. minutt.
- Sender en Slack-melding når et **nytt** brudd oppstår, og en «strøm tilbake»-melding når det er over (med varighet).
- Varsler kun om **faktiske** brudd som standard – planlagte stanser logges, men spammer deg ikke (kan skrus på).
- Logger hvert brudd til `data/events.csv` (sted, kommune, antall kunder, start/slutt, varighet).
- Sender en **ukentlig statistikk** til Slack: antall brudd per kommune og de mest utsatte stedene.

## Dekning – viktig å vite

De tre kommunene er delt mellom to nettselskap:

| Område | Nettselskap | Status i boten |
|---|---|---|
| Fredrikstad (unntatt Onsøy), Hvaler | **Norgesnett** | ✅ Ferdig og verifisert |
| Råde, Onsøy (del av Fredrikstad) | **Elvia** | ⏳ Mangler API-endepunkt (se under) |

Norgesnett dekker kjernen av området. Elvia-delen (`sources/elvia.py`) er klargjort, men trenger at vi fanger API-adressen fra strømbruddskartet deres først. Inntil da kjører boten fint på Norgesnett alene.

## Oppsett (ca. 10 minutter)

### 1. Lag en Slack Incoming Webhook
1. Gå til https://api.slack.com/apps → **Create New App** → *From scratch*.
2. Velg workspace, gi appen et navn (f.eks. «Strømbrudd»).
3. I menyen: **Incoming Webhooks** → skru på → **Add New Webhook to Workspace**.
4. Velg kanalen varslene skal til (f.eks. `#strombrudd`) → **Allow**.
5. Kopier webhook-URL-en (starter med `https://hooks.slack.com/services/...`).

### 2. Legg koden i et GitHub-repo
1. Lag et nytt (gjerne privat) repo på GitHub.
2. Last opp alle filene i denne mappa (behold mappestrukturen).

### 3. Legg inn webhook-en som en «secret»
I repoet: **Settings → Secrets and variables → Actions → New repository secret**
- **Name:** `SLACK_WEBHOOK_URL`
- **Value:** webhook-URL-en fra steg 1.

### 4. Skru på Actions
- Gå til **Actions**-fanen og bekreft at workflows kan kjøre.
- Åpne **«Sjekk strømbrudd»** → **Run workflow** for å teste med én gang (ellers starter den av seg selv innen 10 min).

Det er alt. Boten begynner å overvåke og fylle opp `data/events.csv`.

## Justering

Alt som er greit å endre ligger i `config.py`:
- `TARGET_KOMMUNER` – hvilke kommuner som overvåkes.
- `NOTIFY_PLANNED` – sett til `true` (som secret/variabel) hvis du også vil varsles om planlagte stanser.
- Cron-intervall endres i `.github/workflows/poll.yml` (linja med `cron:`).
- Tidspunkt for ukesstatistikk endres i `.github/workflows/stats.yml`.

## Filene

```
bot.py                     Hovedløkka: hent → sammenlign → varsle → logg
config.py                  Innstillinger
models.py                  Felles datamodell (Outage)
geocode.py                 Koordinat → kommune (Kartverkets API)
slack.py                   Slack-meldinger
store.py                   state.json + events.csv
stats.py                   Ukentlig statistikk
sources/
  norgesnett.py            ✅ Norgesnett (ArcGIS)
  elvia.py                 ⏳ Elvia (mangler endepunkt)
data/                      state.json, events.csv, cache (fylles automatisk)
.github/workflows/         GitHub Actions (poll + statistikk)
```

## Kjøre lokalt (valgfritt, for testing)

```bash
pip install -r requirements.txt
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
python bot.py        # én sjekk
python stats.py 7    # statistikk siste 7 dager
```

Uten `SLACK_WEBHOOK_URL` skrives meldingene til skjermen i stedet for Slack – nyttig for testing.

## Datakilder
- Norgesnett strømstans-kart (ArcGIS-tjeneste bak norgesnett.no/stromstans/)
- Kartverkets kommuneinfo-API (koordinat → kommune)
