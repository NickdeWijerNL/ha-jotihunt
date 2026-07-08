# Jotihunt voor Home Assistant

Een HACS custom integration die de publieke [Jotihunt](https://jotihunt.nl) API
uitleest en per gebied (area) een sensor-entiteit aanmaakt, zodat je er
automatiseringen op kunt bouwen tijdens de jaarlijkse vossenjacht in oktober.

## Wat het doet

- Haalt `https://jotihunt.nl/api/2.0/areas` op via één API-call per update.
- Maakt per area (Alpha, Bravo, Charlie, ...) een sensor-entiteit aan, bijv.
  `sensor.alpha`, met:
  - **state**: de status van het gebied (`green`, `orange`, `red`)
  - **attribuut** `updated_at`: laatste update-tijdstip van die area
- Nieuwe areas die gedurende het evenement verschijnen worden automatisch
  als nieuwe entiteit toegevoegd, zonder herstart nodig.

## Rate limiting

De Jotihunt API staat maximaal 30 calls/minuut toe; bij overschrijding krijg
je eerst een `429`, en bij aanhoudend misbruik een volledige blokkade. Deze
integratie:

- doet **1 API-call per update-cyclus** (alle areas in één keer), niet per
  entiteit;
- gebruikt standaard een **update-interval van 60 seconden** (instelbaar,
  met een harde ondergrens van 30 seconden) — dus 1 call/minuut, ruim onder
  de limiet;
- vangt `429`-responses op, respecteert een eventuele `Retry-After` header,
  en bouwt anders een exponentiële backoff op (60s → 120s → ... tot max.
  15 minuten) voordat er opnieuw een call wordt gedaan;
- gaat na 3 opeenvolgende `429`'s uit van een (bijna) volledige blokkade en
  koelt dan voor de maximale periode af.

## Installatie via HACS

1. Ga in HACS naar **Integrations** → menu (⋮) → **Custom repositories**.
2. Voeg deze repository-URL toe met categorie **Integration**.
3. Zoek naar "Jotihunt" en installeer.
4. Herstart Home Assistant.
5. Ga naar **Instellingen → Apparaten & services → Integratie toevoegen**
   en zoek naar "Jotihunt". Er is geen account of API-sleutel nodig.

## Handmatige installatie

Kopieer de map `custom_components/jotihunt` naar de `custom_components`
map van je Home Assistant configuratie en herstart Home Assistant.

## Voorbeeldautomatisering

```yaml
automation:
  - alias: "Jotihunt: Alpha is rood"
    trigger:
      - platform: state
        entity_id: sensor.alpha
        to: "red"
    action:
      - service: notify.mobile_app_iphone
        data:
          message: "Gebied Alpha staat nu op rood!"
```

## Let op

- Deze integratie is niet officieel gelieerd aan Jotihunt of Scouting
  Nederland.
