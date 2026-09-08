# Amos.Kids — pracovné pravidlá

Projekt beží v Lovable (`763a3681-341b-4f9b-933b-2a4fbda89ff3`), databáza je Supabase
`ckzdovblacamaxaovgpe`. Marketingový funnel je samostatný projekt
(`a2113fbb-c877-4f70-a841-019a01731bf6`).

## Toto je produkcia bez záchrannej siete

Appku používajú skutočné rodiny a smeruje do nej platená reklama. Databáza má **len
denné zálohy cez Lovable a žiadne PITR**. Obnoviť sa dá výhradne celá databáza na
ranný stav — čím sa zmažú všetky registrácie a zmeny od vtedy. Záloha sa nedá stiahnuť.

**Zmazané dáta sú preto zmazané navždy.** Podľa toho sa treba správať.

### Čo sa už raz stalo

27. 8. 2026 som dal naplánovať edge funkciu `process-daily-tasks`, aby konečne
generovala opakované úlohy. Jej krok 4 s názvom „Archive cleanup" mazal natvrdo
(bez akéhokoľvek archívu) úlohy staršie než sedem dní. Funkcia dovtedy nikdy nebežala,
takže jej prvý beh zmazal **sedem mesiacov histórie splnených úloh** — 183 schválených
úloh troch rodín.

Zlyhal som na dvoch miestach naraz:

- **Nečítal som celú funkciu**, len som sa agenta spýtal, čo prvý beh spraví. Odpovedal
  na to, na čo som ho navádzal — na lavínu notifikácií, ktorú som predvídal. Krok 4
  nespomenul ani jeden z nás.
- **Overoval som len to, čo som čakal, že sa zmení** — počet expirovaných úloh a počet
  notifikácií. Nikdy som nespočítal celkový počet riadkov. Jediný `count(*)` pred a po
  by to odhalil okamžite.

## Pravidlá, ktoré z toho platia

1. **Kód, ktorý má bežať bez dozoru proti produkcii, si prečítaj celý sám** — do
   posledného riadku, pred spustením. Nie súhrn od agenta, nie tú časť, ktorej sa
   zadanie týka.

2. **Prvý beh dovtedy nespustenej úlohy narazí na celú nazbieranú históriu naraz.**
   Vždy si najprv odpovedz, čo to spraví s existujúcimi dátami, nie len s budúcimi.

3. **Pred každou operáciou, ktorá môže ubrať riadky, urob census** — `count(*)` na
   dotknutých tabuľkách. Po nej ho zopakuj a rozdiel porovnaj. Kontrolovať len
   očakávané efekty nestačí; chyba je typicky v tom, čo si nečakal.

4. **`DELETE` proti dátam používateľov si pýtaj výslovne**, s pomenovaním tabuľky a
   počtu riadkov. Aj keď to zadanie nepriamo implikuje.

5. **Názvy klamú.** „Cleanup", „archive", „prune", „housekeeping" — nič z toho
   nezaručuje, že sa dá niečo vrátiť.

6. Nič nesmie automaticky mazať `tasks`, `allocations`, `goals`, `goal_payouts`
   ani `app_events`. História splnených úloh je produkt, nie odpad.

## Overovanie práce agenta

Hlásenie agenta nie je dôkaz. Každú zmenu overuj priamo — `get_diff` na kód, SQL na
databázu. Opakovane to odhalilo veci, ktoré hlásenie nespomenulo: nezmenený komponent
pri pozastavenej fronte, anglické reťazce natvrdo v kóde, chýbajúce prekladové kľúče.

Pri i18n vždy over, že kľúč naozaj existuje v `sk.json` — inak sa v UI zobrazí surový
názov kľúča.

## Prostredie

`amos.kids` ani `*.lovable.app` nie sú z tejto session dostupné — sieťová politika
blokuje CONNECT. Appku teda neotestuješ v prehliadači; over ju cez kód a databázu
a vizuálnu kontrolu nechaj na Petra.

`send_message` do Lovable po 60 s vyprší, ale správa sa spravidla doručí a beží ďalej.
**Nikdy nepredpokladaj, že prešla** — over cez `list_edits`. Raz sa správa poslaná,
kým bol agent zaneprázdnený, stratila úplne.
