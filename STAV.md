# Stav rozpracovanej práce — 30. 8. 2026

Prenos medzi session. Prečítaj to na začiatku novej session; keď je položka
vybavená, zmaž ju odtiaľto.

## Ako sa to má robiť

Pravidlá pre prácu proti produkcii sú v `CLAUDE.md`. Platia bez výnimky —
najmä čítanie celého kódu pred spustením, census pred každou operáciou, ktorá
môže ubrať riadky, a overovanie zmien cez `get_diff` a SQL namiesto dôvery
v hlásenie agenta.

Povolenia pre Lovable sú v `.claude/settings.json`. **Nespoliehaj sa na ne** —
30. 8. bolo overené, že súbor bol prítomný už pri štarte procesu a napriek tomu
sa neuplatnil: každé volanie do Lovable končilo na „requires approval", a to aj
volania, ktoré predtým v tej istej session bežali. Zlom nastal po odpojení a
opätovnom pripojení MCP servera Lovable. Ak sa to zopakuje, netreba to
diagnostikovať znova — zadanie sa napíše sem a Peter ho vloží do Lovable ručne;
overovanie odpovede agenta funguje aj bez prístupu.

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
pred odoslaním očami overiť, či to tak naozaj vyzerá, a doplniť presný názov
tej karty. Appka je z tejto session nedostupná, takže overiť sa to odtiaľto nedá.

Peter k mailu dopĺňa dva screenshoty (dashboard s kartou na
odovzdanie appky, obrazovka zadávania PIN-u) — **z testovacieho konta, nie
so skutočnými fotkami jeho detí**.

Adresy si Peter vytiahne sám v Supabase. Najprv over názov stĺpca
(`select column_name from information_schema.columns where table_name = 'children'`),
potom:

```sql
select u.email,
       u.created_at                              as registracia,
       u.raw_app_meta_data->>'provider'          as sposob,
       count(c.id)                               as pocet_deti,
       count(c.id) filter (where c.pin_hash is not null) as deti_s_pinom,
       case when count(c.id) = 0 then 'nepridal dieta'
            else 'dieta sa neprihlasilo' end     as zasekol_sa
from auth.users u
join profiles p on p.user_id = u.id
left join children c on c.parent_id = u.id
where coalesce(p.is_demo, false) = false
group by u.id, u.email, u.created_at, u.raw_app_meta_data
having max(c.last_login_at) is null
order by u.created_at desc;
```

Z výsledku vyhodiť Petrove vlastné testovacie kontá a rodiny registrované pred
pár hodinami — mail „ostáva posledný krok" po dvadsiatich minútach je predčasný.

Ďalšie dva maily v sekvencii (T+3 dni: odstránenie prekážky — dieťa nemá
zariadenie / rodič nepozná PIN; T+7 dní: osobná otázka „Čo vás zastavilo?")
zatiaľ nie sú napísané. Automatizovať až po overení textu na prvom kole.

Doména je čerstvo napárovaná — pred väčším objemom overiť SPF, DKIM, DMARC.

## Zadania pripravené na vloženie do Lovable

Projekt v Lovable: `763a3681-341b-4f9b-933b-2a4fbda89ff3`.
Supabase: `ckzdovblacamaxaovgpe`.

Zdrojový kód appky nie je v žiadnom GitHub repozitári — ani v `amos-kids`,
ani v `pietro18/pietro18`. Žije výhradne v Lovable. Cez git sa opraviť nedá.

Obe zadania nižšie sú hotové a doslovné. Pošli ich cez `send_message`, alebo
ich Peter vloží do Lovable chatu ručne. Po každom si vyžiadaj `get_diff` a
odpoveď over sám — hlásenie agenta nie je dôkaz.

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
> 1. **Banner „dieťa sa ešte neprihlásilo".** Naprieč všetkými rodinami
>    z platenej kampane je nula prihlásení dieťaťa — appka rieši úlohy detí,
>    ktoré sa do nej ani raz nedostali, a ani jeden typ notifikácie tú situáciu
>    nepomenúva. Keď má rodič aspoň jedno dieťa, ktoré sa ešte ani raz
>    neprihlásilo, ukáž na jeho dashboarde navrchu jednu výraznú kartu s touto
>    informáciou a s tlačidlom, ktoré vedie priamo na odovzdanie appky dieťaťu.
>    Kým tam tá karta je, potlač bežné nagovanie o nesplnených úlohách toho
>    dieťaťa — je bezpredmetné. Karta zmizne po prvom prihlásení dieťaťa.
>
> 2. **Žiadosť o povolenie push notifikácií presuň z registrácie na okamih po
>    prvom prihlásení dieťaťa.** Pri registrácii sa povolenie udelí alebo
>    odmietne naprázdno, lebo ešte nie je čo oznamovať; keď príde prvá skutočná
>    vec, je už spálené.
>
> 3. **Zjednoť dve počítadlá.** Zvonček v hlavičke ukazuje počet neprečítaných
>    notifikácií, odznak na položke „Domov" v spodnej navigácii ukazuje
>    `pendingWork` (bez zastaraných, bez tých určených dieťaťu). Rodič teda vidí
>    na jednej obrazovke dve rôzne čísla o tom istom — napr. 6 a 1 — a nemá ako
>    vedieť, čo znamenajú. Nechaj jediné číslo, a to to, ktoré hovorí, koľko vecí
>    naozaj čaká na jeho akciu.
>
> 4. **„Najlepší deň" v karte týždňa nahraď.** Pri štyroch splnených úlohách za
>    týždeň ten údaj rozlišuje deň s dvomi od dňa s jednou — je to šum. Navyše je
>    hneď nad tlačidlom „Naplánovať ďalší týždeň", takže má pomáhať plánovať, a
>    nepomáha. Nahraď ho dňom s najvyššou mierou nesplnených úloh („v piatok sa
>    to najčastejšie nestihne"), a zobraz ho až keď je z čoho — aspoň tri týždne
>    dát a skutočný rozdiel medzi dňami. Do vtedy tam nemá byť nič.
>
> V odpovedi chcem: zoznam nových i18n kľúčov s potvrdením, že sú v oboch
> locale súboroch, a potvrdenie, že žiadna zmena nepridáva mazanie dát.

## Prostredie

`amos.kids` aj `*.lovable.app` vracajú 403 na CONNECT — overené 30. 8. 2026.
Screenshoty ani vizuálnu kontrolu z tejto session spraviť nedá; robí ich Peter.
