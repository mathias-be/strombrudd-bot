# Planlagt kjøring og pålitelighet

## Hva GitHub Actions garanterer

Workflowen er satt opp med en tieminutters cron, men GitHub Actions schedule-hendelser er «best effort». GitHub opplyser at slike kjøringer kan bli forsinket ved høy belastning, og at planlagte hendelser kan droppes. Minste støttede intervall er fem minutter. En grønn kjøring viser bare at akkurat den kjøringen lyktes; den viser ikke at alle planlagte kjøringer ble startet.

Cronen starter derfor på minutt 3 (3, 13, 23, 33, 43, 53) i stedet for ved timeskiftet. Det unngår et kjent høylasttidspunkt, men kan ikke hindre lange opphold. Se [GitHubs dokumentasjon om schedule-hendelser](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

## Legg til en ekstern trigger

For en ekstra uavhengig scheduler kan en ekstern cron-tjeneste kalle GitHubs workflow_dispatch-API. Den eksisterende poll.yml støtter allerede denne hendelsen. Kjør tjenesten hvert tiende minutt, forskjøvet til minutt 8 (8, 18, 28, 38, 48, 58) for å unngå samme starttid som GitHub-cronen.

1. Opprett et finmasket GitHub-token begrenset til mathias-be/strombrudd-bot, med repository-tillatelsen Actions: write.
2. Lagre tokenet som en hemmelighet i cron-tjenesten. Ikke legg tokenet i repoet eller i en URL.
3. Konfigurer en HTTP POST til:
   https://api.github.com/repos/mathias-be/strombrudd-bot/actions/workflows/poll.yml/dispatches
4. Send headerne Accept: application/vnd.github+json, Authorization: Bearer <token> og Content-Type: application/json, med JSON-kroppen:
   {"ref":"main"}
5. Varsle hvis API-kallet feiler, og kontroller at dispatchene faktisk gir workflow-kjøringer i Actions-historikken.

GitHub dokumenterer at dispatch-endepunktet krever Actions: write for finmaskede tokens. Et vellykket API-svar betyr at kjøringen er sendt inn, ikke at boten allerede har fullført kontrollen. Denne løsningen gir en separat planlegger, men GitHub-hostede runners og workflow_dispatch kan fortsatt ha forsinkelser eller være utilgjengelige.

## Hvis ti minutter er et krav

Hvis overvåkningen må holde en strengere tidsfrist, bør boten kjøres som en planlagt jobb hos en ekstern skytjeneste (for eksempel en containerjobb eller serverless scheduler) i stedet for å være avhengig av GitHub Actions. Det krever en valgt tjeneste, lagring av Slack-hemmeligheten og varig lagring av botens tilstand/historikk. Disse tjeneste- og kontovalgene må settes opp separat.
