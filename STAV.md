# Stav rozpracovanej práce — 30. 8. 2026

Prenos medzi session. Prečítaj to na začiatku novej session; keď je položka
vybavená, zmaž ju odtiaľto.

## Ako sa to má robiť

Pravidlá pre prácu proti produkcii sú v `CLAUDE.md`. Platia bez výnimky —
najmä čítanie celého kódu pred spustením, census pred každou operáciou, ktorá
môže ubrať riadky, a overovanie zmien cez `get_diff` a SQL namiesto dôvery
v hlásenie agenta.

Povolenia pre Lovable sú v `.claude/settings.json` a v novej session sa načítajú
pri štarte, takže `query_database` a `send_message` už nemajú pýtať súhlas.
`deploy_project` ostáva mimo povolení — publikuje výhradne Peter.

## Kontext

Beží platená Meta kampaň (`SK | Amos Leads Campaign | 2026-08-25`), appku
používajú skutočné rodiny. Naprieč všetkými rodinami z kampane je **nula
prihlásení dieťaťa**. Rodičia dokončia onboarding za 30–90 sekúnd a tým to
končí. To je jediná brána, o ktorú ide; všetko ostatné je druhoradé.

## Otvorené — v poradí

### 1. Súhrnná karta pripomienky pre viac detí (publikované, zobrazuje sa zle)

Commit `70983ad558dc148366b2d66d834bcec7524b355b` je publikovaný a obsahuje
chybu. V `send-parent-reminders` sa pri rodičovi s viacerými deťmi vkladá
`params: { variant: "multi", count, names }` bez `name`.

- Nadpis sa berie vždy z `notificationTypes.<typ>.title` a `variant` ovplyvňuje
  len telo. `reminder_chores.title` je „{{name}} má ešte úlohy" → rodič uvidí
  nadpis s prázdnym menom. Treba podporu `title_multi` s plurálmi v `sk.json`
  aj `en.json`.
- `const bodyKey = variantKey && i18n.exists(variantKey) ? variantKey : ...`
  volá `i18n.exists('...body_multi')` bez `count`, pričom v JSON-e je len
  `body_multi_one` / `_few` / `_many` / `_other`. Ak `exists` vráti false,
  spadne to na `${base}.body`, ktorý pri `reminder_chores` neexistuje ako holý
  kľúč. Overovať existenciu s rovnakými options, s akými sa prekladá.
- Poistka: pridať do multi params aj `name: lead.name`.
- Skontrolovať kľúče `reminder_chores` / `reminder_streak` /
  `reminder_empty_tomorrow` pridané mimo sekcie `notificationTypes`
  (~riadok 2226 `en.json`, 2264 `sk.json`) — ak ich nič nepoužíva, preč.

Týka sa rodín s tromi deťmi: Anna/Peter/Marie a Mario/Demir/František.

### 2. In-browser zmeny (zadanie pripravené, neodoslané)

- **Banner „dieťa sa ešte neprihlásilo"** na dashboarde rodiča namiesto
  nagovania o úlohách. Dnes appka rieši úlohy dieťaťa, ktoré sa do nej ani raz
  nedostalo — ani jeden typ notifikácie túto situáciu nepomenúva.
- **Žiadosť o push až po prvom prihlásení dieťaťa**, nie pri registrácii.
  Pri registrácii sa povolenie spáli naprázdno.
- **Zjednotiť počítadlá.** Zvonček ukazuje neprečítané notifikácie, odznak na
  „Domov" ukazuje `pendingWork` (bez zastaraných, bez detských). Dve rôzne
  čísla o tom istom na jednej obrazovke. Nechať len to, čo čaká na akciu.
- **„Najlepší deň: St"** v karte týždňa nedáva hodnotu — pri 4 úlohách za
  týždeň je to šum, a nad tlačidlom „Naplánovať ďalší týždeň" má stáť údaj,
  ktorý pomôže plánovať. Nahradiť dňom s najvyššou mierou nesplnenia a
  zobraziť až pri dostatku dát (aspoň tri týždne a skutočný rozdiel).

### 3. `send-weekly-report-sunday-local` nemá ani jeden úspešný beh

`last_success` je NULL. Týždenný report má rodiny držať; kým nefunguje, nemá
zmysel stavať na tom istom základe akvizičnú sekvenciu.

### 4. Mail pre zaseknuté rodiny (text hotový, posiela Peter ručne)

Text je nižšie. Peter k nemu dopĺňa dva screenshoty (dashboard s kartou na
odovzdanie appky, obrazovka zadávania PIN-u) — **z testovacieho konta, nie
so skutočnými fotkami jeho detí**.

Adresy si vytiahne sám cez SQL: rodiny, kde `max(children.last_login_at)` je
NULL, bez demo kont, bez jeho vlastných testovacích, a bez tých, čo sa
registrovali pred pár hodinami.

Ďalšie dva maily v sekvencii (T+3 dni: odstránenie prekážky — dieťa nemá
zariadenie / rodič nepozná PIN; T+7 dní: osobná otázka „Čo vás zastavilo?")
zatiaľ nie sú napísané. Automatizovať až po overení textu na prvom kole.

Doména je čerstvo napárovaná — pred väčším objemom overiť SPF, DKIM, DMARC.

## Prostredie

`amos.kids` aj `*.lovable.app` vracajú 403 na CONNECT — overené 30. 8. 2026.
Screenshoty ani vizuálnu kontrolu z tejto session spraviť nedá; robí ich Peter.
