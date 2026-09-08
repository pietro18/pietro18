# Stav rozpracovanej práce — 31. 8. 2026

Prenos medzi session. Prečítaj to na začiatku novej session; keď je položka
vybavená, zmaž ju odtiaľto.

## Ako sa to má robiť

Pravidlá pre prácu proti produkcii sú v `CLAUDE.md`. Platia bez výnimky —
najmä čítanie celého kódu pred spustením, census pred každou operáciou, ktorá
môže ubrať riadky, a overovanie zmien cez `get_diff` a SQL namiesto dôvery
v hlásenie agenta. **Session 31. 8. dvakrát chytila vlastnú chybu presne takto**
— pozri bod 0 nižšie: prvá migrácia aj prvý fallback boli neúplné/chybné a
odhalilo sa to až nezávislým overením, nie hlásením agenta.

Povolenia pre Lovable sú v `.claude/settings.json`. Session 30. 8. zaznamenala,
že súbor bol prítomný, ale volania končili na „requires approval", až kým sa
MCP server Lovable neodpojil a znova pripojil. **Session 31. 8. tento problém
nemala** — `query_database`, `send_message`, `get_diff` fungovali celý čas bez
schvaľovania. Ak sa problém vráti, netreba ho diagnostikovať znova: zadanie sa
napíše sem a Peter ho vloží do Lovable ručne; overovanie odpovede agenta
funguje aj bez priameho prístupu.

`deploy_project` ostáva mimo povolení — publikuje výhradne Peter.

Zdrojový kód appky nie je v žiadnom GitHub repozitári — ani v `amos-kids`, ani
v `pietro18/pietro18`. Žije výhradne v Lovable (`list_files`/`read_file` cez
Lovable MCP naň dosiahnu bez gitu; `get_diff` funguje na commit/message_id
z Lovable, nie na git commit).

## Kontext

Beží platená Meta kampaň (`SK | Amos Leads Campaign | 2026-08-25`), appku
používajú skutočné rodiny. Pôvodný odhad „nula prihlásení dieťaťa naprieč
kampaňou" (30. 8.) bol nepresný — **koreňová príčina je nájdená a čiastočne
už opravená v produkcii**, pozri bod 0. Presné čísla k 31. 8. ráno:

- 26 reálnych rodičov (bez demo/test/Petrových kont), 30 pridaných detí
- Zo 47 reálnych pokusov o prihlásenie dieťaťa od 25. 8. (`login_attempts`)
  uspelo 7 — **všetkých 7 z Petrovho vlastného testovacieho konta** (deti
  „lukas"/„simon"). Zo skutočných kampaňových rodín neprešiel ani jeden
  z 40 pokusov.
- 1 dieťa z 30 má záznam úspešného prihlásenia cez `app_events` (`child_login`,
  Juliana Gulášová/Štefan, 30. 8. 09:54) — ale to je iný signál než
  `login_attempts` a nesedí s ním úplne, pozri poznámku v bode 0.

To je jediná brána, o ktorú ide; všetko ostatné je druhoradé.

## Otvorené — v poradí

### 0. [NOVÉ, 31. 8.] Prihlásenie dieťaťa zlyhávalo takmer vždy — príčina nájdená, DB fix live, UI čaká na publish

**Toto je teraz najvyššia priorita, nad bodom 1** — je to príčina javu z
"Kontext", nie ďalší symptóm.

**Diagnóza:** `verify_child_pin` (Postgres funkcia) vyžadovala presnú zhodu
CELÉHO mena dieťaťa. Formulár na `/auth` (child tab, `src/pages/Auth.tsx`) je
prázdne textové pole bez nápovedy na formát. `login_attempts` ukazuje rodiny
reálne hádajúce varianty: dieťa "Lucas Dominik" → skúšali "dominik", "dominik
kovac", "lucas dominik" (9 pokusov za 2 min); dieťa pravdepodobne "Bartolomej
niekto" → "horvath bartolomej", "bartolomej", "horvath" (meno sa v `children`
nenašlo vôbec — buď iný pravopis, alebo dieťa ešte nebolo pridané).

**Oprava (Lovable, commity `7610d42` → oprava `39fcc5a`, obe overené priamo
v DB, nie len z hlásenia agenta):**

- `verify_child_pin`: k presnej zhode pribudol word-level fallback —
  `v_normalized_name = ANY(string_to_array(lower(name),' '))` a opačne. Zadané
  meno teda nemusí byť celé, stačí ktorékoľvek slovo z uloženého mena (aj
  naopak). PIN kontrola cez `extensions.crypt` nezmenená, ostáva jediná
  skutočná autentifikácia.
- Lockout zvýšený z 5 na 10 zlyhaní/15 min (rodina si nesmie zamknúť samu seba
  počas hádania variantu mena).
- **Prvá verzia migrácie bola neúplná** — porovnávala len PRVÉ slovo, čo by
  "dominik" pri mene "Lucas Dominik" stále odmietlo (Dominik je druhé slovo).
  Vlastným overením (`SELECT 'dominik' = ANY(string_to_array(lower('Lucas
  Dominik'),' '))`) sa to chytilo pred nahlásením Petrovi a Lovable to
  opravil na word-level match kdekoľvek v mene.
- **Prvá verzia migrácie mala aj preklep** (`currentStreak` namiesto
  `current_streak`) — chytil ho Lovable agent sám v druhom kroku, nezávisle
  overené v `information_schema.columns`.
- **DB časť je live v produkcii ihneď** (Supabase migrácie sa aplikujú mimo
  frontend publish cyklu) — child, ktorý teraz skúsi len krstné meno, by mal
  prejsť. UI časť (nápoveda pod poľom mena, lepšia chybová hláška s odkazom na
  QR) je len v Lovable preview, čaká na Petrov `get_diff` a publish.

**Neoverené/vedľajšie zistenia, netreba riešiť teraz:**
- `child_login_tokens` (QR flow) má anomáliu: jeden token mal `used_at` 23 min
  PO vlastnom `expires_at` — podľa `redeem_child_login_token` (vyžaduje
  `expires_at > now()`) by to nemalo byť možné. `create_child_login_token`
  used_at nikdy nenastavuje. Príčina nejasná, mimo rozsahu dnešnej opravy.
- `client_errors` má opakovaný React DOM crash (`removeChild`/`insertBefore
  ... is not a child of this node`), ~30+ výskytov za týždeň naprieč
  `/parent`, `/parent/tasks`, `/parent/goals`, aj `/child`. Nesúvisí s bodom 0,
  ale je to najčastejšia chyba v appke — kandidát na ďalšiu prioritu.
- Anonymní používatelia (najmä na `/auth`) hádžu `Error invoking postMessage:
  Java exception` — 75 % návštevnosti ide z Facebooku/Instagramu, podozrenie
  na FB in-app browser (Android WebView) quirk práve na vstupnom bode pred
  registráciou.
- Onboarding funnel: 41× zobrazené → 19× dokončené (46 %), 15 tichých odchodov
  bez signálu prečo.
- `profiles.email` je `NULL` pre reálnych používateľov — email sa musí ťahať
  z `auth.users`. Ak má byť `profiles.email` zdroj pravdy pre automatizované
  maily (T+3/T+7 nižšie), zistiť prečo sa nezapisuje.

**Ďalší krok:** Peter otestuje reálne (napr. rodina Kováčová/Lucas Dominik),
alebo počká na prirodzený pokus niektorej z 18 rodín z bodu 4. Po potvrdení
zmazať tento bod.

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

Zadanie pre Lovable je hotové, pozri „Zadanie A" nižšie — ešte neodoslané.

### 2. In-browser zmeny (zadanie pripravené, neodoslané)

- **Banner „dieťa sa ešte neprihlásilo"** na dashboarde rodiča namiesto
  nagovania o úlohách.
- **Žiadosť o push až po prvom prihlásení dieťaťa**, nie pri registrácii.
- **Zjednotiť počítadlá.** Zvonček vs. odznak na „Domov" (`pendingWork`) —
  dve rôzne čísla o tom istom.
- **„Najlepší deň: St"** nahradiť dňom s najvyššou mierou nesplnenia, zobraziť
  až pri dostatku dát (aspoň tri týždne).

Zadanie pre Lovable je hotové, pozri „Zadanie B" nižšie — ešte neodoslané.

### 3. Týždenný report — VYRIEŠENÉ 30. 8., ale odhalil tvrdé číslo

`send-weekly-report-sunday-local` prebehol prvýkrát úspešne 30. 8. o 17:00 UTC
(`last_success` vyplnené, `failures_7d = 0`). Funkcia je v poriadku.

Odišiel však **jednej jedinej rodine z 32**, ktoré majú týždenný report zapnutý.
Nie je to chyba — funkcia zámerne preskočí rodinu bez splnenej úlohy
(„Never send an empty scoreboard", vetva `empty_week`). Census za týždeň
24.–30. 8.: **9 schválených úloh dokopy, všetky v jednej rodine z 33.**

To je zatiaľ najostrejšie vyjadrenie hlavného problému. Nula prihlásení dieťaťa
sa tu premieta do nula obsahu: 31 rodín nemá čo dostať. Žiadny e-mailový kanál
tento stav nevyrieši, kým sa appka nedostane deťom do rúk. *(Poznámka zo session
31. 8.: presne toto je dôvod, prečo bod 0 — oprava prihlásenia — musí zabrať
skôr, než sa tento kanál znovu skúma.)*

### 4. Mail pre zaseknuté rodiny (text hotový, posiela Peter ručne)

**Cieľová skupina, prepočítaná 31. 8. — použiť namiesto SQL nižšie, je rýchlejšia
a už vylučuje testovacie kontá:**

18 rodín má dieťa pridané, ale nikdy neúspešne prihlásené (`child_login`
event chýba): Lakatoš, Dančurová, Štajerová, Ľubomír, Dužda, Kováčová,
Sitková, Kujovská, Čatová, Tatai, Evka, Lenka ×2, Lomnička84, Horňák,
Daniheľová, Ferko, Mlynárovičová. Kompletný zoznam s emailami je v transkripte
session 31. 8. (alebo sa dá prepočítať cez `app_events`/`children`/`profiles`
join popísaný nižšie).

Samostatná skupina — 3 rodiny bez pridaného dieťaťa vôbec (Teglášová,
Horníková, Janová) — potrebujú iný text (najprv pridať dieťa), a sú príliš
čerstvé na to, aby to bol "problém".

Vylúčiť z oboch skupín natrvalo: `test@gmail.com`, `jana.kmoskova@hotmail.com`,
`kmoskolukas@gmail.com`, `parkovaniecv@gmail.com` (Peter Kmoško, iný mail),
`klaraturcanova@gmail.com` (ABC ABC, placeholder dáta pred kampaňou) — všetko
potvrdené Petrom ako vlastné/testovacie kontá 31. 8.

**Dôležité:** keďže bod 0 je teraz čiastočne opravený (DB fix live), zváž
počkať s odoslaním tohto mailu, kým sa neoverí, či niektorá z 18 rodín už
prejde prihlásením sama — mail môže byť zbytočný, ak fix stačí.

**Opravená SQL na adresy** (pôvodná verzia odkazovala na neexistujúci stĺpec
`children.last_login_at` — `children` taký stĺpec nemá; reálny signál
úspešného prihlásenia je `app_events.event_type = 'child_login'`):

```sql
with logins as (
  select distinct child_id from app_events where event_type = 'child_login'
)
select
  au.email,
  p.name,
  p.created_at as registracia,
  p.signup_campaign,
  count(c.id) as pocet_deti,
  count(c.id) filter (where l.child_id is not null) as deti_prihlasene
from profiles p
join auth.users au on au.id = p.user_id
left join children c on c.parent_id = p.user_id
left join logins l on l.child_id = c.id
where coalesce(p.is_demo, false) = false
  and p.user_id <> '60491167-4961-426e-81ce-39b2e7b000d3' -- Petrovo testovacie konto
group by p.id, au.email, p.name, p.created_at, p.signup_campaign
having count(c.id) filter (where l.child_id is not null) = 0
order by p.created_at desc;
```

Z výsledku ešte ručne vyhodiť known-test emaily vyššie a rodiny registrované
pred pár hodinami.

Text mailu:

> **Predmet:** Ostáva posledný krok
>
> Dobrý deň,
>
> ďakujem, že ste Amosa vyskúšali.
>
> Píšem preto, že väčšina rodičov sa zasekne na tom istom mieste: appku si
> nastavia, ale nikdy sa nedostane k dieťaťu. A kým sa dieťa neprihlási, Amos
> nemá čo robiť — celé to stojí na tom, že si úlohy odškrtáva ono, nie vy.
> Preto to posielam rovno, nech to nemusíte hľadať.
>
> Trvá to dve minúty:
>
> 1. Prihláste sa do Amosa na svojom telefóne.
> 2. Na hlavnej obrazovke nájdite kartu na odovzdanie appky dieťaťu — je hneď navrchu.
> 3. Dajte dieťaťu naskenovať kód jeho telefónom alebo tabletom.
> 4. Dieťa zadá svoj PIN — ten, ktorý ste mu nastavili, keď ste ho pridávali.
>
> PIN sa z bezpečnostných dôvodov nedá nikde zobraziť. Ak si ho nepamätáte,
> dá sa nastaviť nový v profile dieťaťa.
>
> Keby čokoľvek nefungovalo alebo vyzeralo inak, než píšem, odpíšte prosím
> rovno na tento mail. Sme úplne na začiatku a každú novú rodinu si prechádzam
> osobne — vaša spätná väzba mi teraz pomôže viac než čokoľvek iné.
>
> Peter

Kroky 2 a 3 sú napísané podľa toho, čo je známe o `ChildHandoffCard`. Peter má
pred odoslaním očami overiť, či to tak naozaj vyzerá.

Peter k mailu dopĺňa dva screenshoty (dashboard s kartou na odovzdanie appky,
obrazovka zadávania PIN-u) — **z testovacieho konta, nie so skutočnými
fotkami jeho detí**.

Ďalšie dva maily v sekvencii (T+3 dni: odstránenie prekážky — dieťa nemá
zariadenie / rodič nepozná PIN; T+7 dní: osobná otázka „Čo vás zastavilo?")
zatiaľ nie sú napísané. Automatizovať až po overení textu na prvom kole.

Doména je čerstvo napárovaná — pred väčším objemom overiť SPF, DKIM, DMARC.

## Zadania pripravené na vloženie do Lovable

Projekt v Lovable: `763a3681-341b-4f9b-933b-2a4fbda89ff3`.
Supabase: `ckzdovblacamaxaovgpe`.

Obe zadania nižšie sú hotové a doslovné, ešte neodoslané (na rozdiel od
opravy v bode 0, ktorá už bola odoslaná a je live). Pošli ich cez
`send_message`, alebo ich Peter vloží do Lovable chatu ručne. Po každom si
vyžiadaj `get_diff` a odpoveď over sám priamo v kóde/DB — hlásenie agenta
nie je dôkaz (pozri bod 0, kde to dvakrát zachránilo pred neúplným fixom).

### Zadanie A — súhrnná karta pripomienky (položka 1, publikovaná chyba)

> Súhrnná karta pripomienky pre viac detí je publikovaná a zobrazuje sa zle.
> Oprav ju prosím. Nič nemazať, žiadne DELETE nad databázou.
>
> V `supabase/functions/send-parent-reminders/index.ts` sa pri rodičovi
> s viacerými deťmi vkladá `params: { variant: "multi", count, names }` — bez
> `name`. Z toho plynú tri veci:
>
> 1. **Nadpis ignoruje variant.** V `src/lib/notificationText.ts` sa nadpis
>    berie vždy z `notificationTypes.<typ>.title` a `variant` ovplyvňuje iba
>    telo. Nadpis `reminder_chores.title` je „{{name}} má ešte úlohy", ale
>    `name` v multi params nie je — rodič uvidí nadpis s prázdnym menom, teda
>    „ má ešte úlohy". Priveď nadpis na rovnakú logiku ako telo (podpora
>    `title_multi`) a doplň kľúče `title_multi_one` / `_few` / `_many` /
>    `_other` do `src/i18n/locales/sk.json` aj `en.json`.
>
> 2. **Telo môže spadnúť na zlý kľúč.** Riadok
>    `const bodyKey = variantKey && i18n.exists(variantKey) ? variantKey : ${base}.body;`
>    volá `i18n.exists('...body_multi')` bez `count`. V JSON-e existujú len
>    `body_multi_one` / `_few` / `_many` / `_other`, holý `body_multi` nie.
>    Over, či `exists` bez `count` na plurálovom kľúči vráti true. Ak nie,
>    spadne to na `${base}.body`, ktorý pri `reminder_chores` tiež neexistuje
>    ako holý kľúč, i18next by cez `count` vyskladal `body_few` a rodičovi by
>    sa zobrazilo „ má dnes ešte 3 nesplnené úlohy" namiesto „3 deti
>    potrebujú tvoju pozornosť: Anna, Peter, Marie". Existenciu variantu
>    overuj s rovnakými options, s akými sa potom prekladá, teda vrátane `count`.
>
> 3. Ako poistku pridaj do multi params aj `name: lead.name`, nech ani pri
>    zlyhaní fallbacku nevznikne veta s prázdnym menom.
>
> 4. Skontroluj kľúče `reminder_chores`, `reminder_streak` a
>    `reminder_empty_tomorrow`, ktoré pribudli na najvyššej úrovni (okolo
>    riadku 2226 v `en.json`, 2264 v `sk.json`) mimo sekcie
>    `notificationTypes`. Ak ich nič nepoužíva, odstráň ich; ak ich používa
>    push payload, nechaj ich a napíš mi kde.
>
> V odpovedi chcem konkrétny výsledok, nie tvrdenie: (a) presný nadpis aj telo
> v slovenčine pre rodiča s tromi deťmi, (b) to isté pre rodiča s jedným
> dieťaťom, nech sa nepokazila doterajšia cesta, (c) potvrdenie, že každý
> kľúč, na ktorý sa kód odvoláva, existuje v oboch locale súboroch,
> (d) potvrdenie, že v `send-parent-reminders` nie je žiadny `.delete()`.

### Zadanie B — in-browser zmeny (položka 2)

> Štyri zmeny v rodičovskom rozhraní. Nič nemazať, žiadne DELETE nad databázou.
> Všetky texty cez i18n kľúče, žiadne reťazce natvrdo v kóde, a každý nový kľúč
> musí existovať v `sk.json` aj `en.json`.
>
> 1. **Banner „dieťa sa ešte neprihlásilo".** Keď má rodič aspoň jedno dieťa,
>    ktoré sa ešte ani raz neprihlásilo, ukáž na jeho dashboarde navrchu jednu
>    výraznú kartu s touto informáciou a s tlačidlom, ktoré vedie priamo na
>    odovzdanie appky dieťaťu. Kým tam tá karta je, potlač bežné nagovanie
>    o nesplnených úlohách toho dieťaťa. Karta zmizne po prvom prihlásení.
>
> 2. **Žiadosť o povolenie push notifikácií presuň z registrácie na okamih po
>    prvom prihlásení dieťaťa.**
>
> 3. **Zjednoť dve počítadlá.** Zvonček (neprečítané notifikácie) vs. odznak
>    na „Domov" (`pendingWork`, bez zastaraných, bez detských). Nechaj jediné
>    číslo — to, čo naozaj čaká na akciu.
>
> 4. **„Najlepší deň" v karte týždňa nahraď** dňom s najvyššou mierou
>    nesplnených úloh, zobraz až pri aspoň troch týždňoch dát.
>
> V odpovedi chcem: zoznam nových i18n kľúčov s potvrdením, že sú v oboch
> locale súboroch, a potvrdenie, že žiadna zmena nepridáva mazanie dát.

## Prostredie

`amos.kids` aj `*.lovable.app` vracajú 403 na CONNECT z niektorých sessions
(overené 30. 8.) — v session 31. 8. toto obmedzenie nebránilo prístupu cez
Lovable MCP (`read_file`, `query_database`, `send_message`, `get_diff`
fungovali celý čas). Priamu vizuálnu kontrolu v prehliadači stále robí Peter.


---

## Kontrolné meranie 8. 9. 2026 — oprava z bodu 0 zabrala

Overené priamo v produkčnej databáze, nie z hlásenia agenta.

**Prihlásenia detí — signál `app_events.event_type = 'child_login'`:**

| | pred 31. 8. | od 31. 8. do 8. 9. |
|---|---|---|
| detí s aspoň jedným prihlásením | 1 (z toho Petrove testy) | **29** |
| prihlásení spolu | — | **67** |
| rodín s prihláseným dieťaťom | 1 | **25** |

Prvé prihlásenie prišlo 31. 8. o 10:24, teda v to isté ráno, keď šla oprava
`verify_child_pin` do produkcie. Posledné 8. 9. o 13:40. Bod 0 sa dá zavrieť.

**Používanie:** 153 schválených úloh v 18 rodinách za 31. 8. – 8. 9., oproti
9 úlohám v jedinej rodine za predošlý týždeň. 62 nových snov.

**Rast:** 172 reálnych rodičov (+143 za týždeň), 177 detí (+145). Všetkých 177
detí má nastavený PIN. 18 rodičov zatiaľ nepridalo dieťa.

**Bod 1 (súhrnná karta) je vyriešený.** Všetky karty s `variant = "multi"` majú
v `params` aj `name`, takže nadpis s prázdnym menom už nevzniká.

**Zastavenie otravovania funguje.** Z 132 rodičov, ktorí za toto obdobie dostali
pripomienku, ani jeden nemá viac než 3 a všetky neprečítané; maximum na rodiča
je 6, priemer 2,4.

**Čo ostáva nepríjemné:** z 319 pripomienok bolo prečítaných 8, teda 2,5 %.
`reminder_empty_tomorrow` má 63 odoslaní a **nula** prečítaní. Nezastavuje ich
to (poistka funguje), ale ako kanál to nefunguje — stojí za zváženie, či
`reminder_empty_tomorrow` vôbec posielať.

**Cielenie win-back mailu z bodu 4 treba prepočítať.** Zoznam 18 rodín je z 31. 8.,
spred opravy; časť z nich sa medzitým prihlásila. Použi `child_login` join
z bodu 4, nie starý zoznam mien.


---

## 8. 9. 2026 — vyplácanie a rodičovský zámok (VYRIEŠENÉ, publikované)

Publikoval Peter 8. 9. večer. Všetko nižšie je overené v diffe, nie z hlásenia agenta.

**Objaviteľnosť vyplácania** (`543a40b2`). Podnet: reálny zákaznícky dotaz „ako
môžem dať peniaze za úlohy na účet v banke". Príčina bola v UI, nie v logike —
platobný tok funguje (52 vyplatení, z toho 37 vybavených), ale viedli k nemu
len dve nenájditeľné cesty: karta „Na vyplatenie" na dashboarde sa objaví až keď
je sen na 100 % (`if (outstanding.length === 0) return null;`), a na `/parent/goals`
bola pri aktívnom sne len **ikona `HandCoins` bez textu**, s popisom iba v `title`.

Opravené: nový kľúč `parent.goals.payOut` („Vyplatiť" / „Pay out") v oboch locale
súboroch, tlačidlo má viditeľný text, riadok je `flex-wrap` s `min-w-[120px]`.
`payout.noIbanHint` je teraz odkaz na `/parent/children/:childId/edit` (route
overená v `App.tsx`) a text prepísaný na výzvu.

**Rodičovský zámok** (`0214180d`). Dve chyby, obe vedeli vyhodiť rodiča z konta:

- `ParentPinGate.forgotPin` volal `signOut()` bez potvrdenia, a zámok nemal cestu
  späť k dieťaťu — dieťa sa naň dostalo omylom a jedným klepnutím odhlásilo rodiča.
  Opravené: `AlertDialog` s konkrétnym dôsledkom + tlačidlo „Späť k dieťaťu", ktoré
  **nevolá `unlockParent()`** (overené).
- `AppHeader` volal na detskej strane `lockParent()` **bezpodmienečne**, aj bez
  existujúceho PIN-u. Rodič potom musel zadať štyri náhodné číslice, kým mu appka
  ponúkla PIN vytvoriť — a tie pokusy sa počítali do `too_many_attempts`.
  Opravené: `handleBackToParent` zisťuje stav cez `getParentProfile`; zamyká len
  keď PIN existuje, neznámy stav zamyká (konzervatívne).

**Vedomý kompromis:** bez nastaveného PIN-u vedie detská šípka do rodičovskej časti
**odomknutej**, s okamžitou výzvou PIN si nastaviť. Dieťa sa teda pri rodine bez
PIN-u vie preklikať k rodičovi. Je to lepšie než zamknúť rodiča z vlastného konta,
ale ochrana začína platiť až po vytvorení PIN-u.

**Drobnosť na neskôr:** `markPinResetPending` sa teraz používa aj pre stav „PIN ešte
neexistuje", hoci jeho komentár hovorí o obnove po zabudnutí. Funguje, len názov klame.

**Tretie hlásenie z tej istej dávky** — „deťom sa tvrdí, že ich vlastný sen je od
rodiča" — v kóde k 8. 9. neplatí. `ChildDashboard` má poistku `hasOwnDream ||
!authorskipKnown`, ktorá mlčí aj pri neznámom autorstve (`created_by` je NULL pri
64 z 89 snov). Podľa znenia komentára pri tej poistke šlo pravdepodobne o opravu
práve tohto hlásenia. Zdroj hlásení je spoľahlivý — dve z troch sedeli do písmena.
