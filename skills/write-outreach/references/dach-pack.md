# DACH pack

Conventions for German-speaking markets (Germany, Austria, Switzerland). Most of it transfers to any market where the default rules were written for another language.

## Formal or informal address

| Vertical | Address | Note |
|---|---|---|
| insurance, tax advisory, legal, medical practices, property management, hotels, IT services | Sie plus `{{salutation}} {{lastName}}` | formal wins; informal address in these verticals triggers spam complaints |
| hospitality (restaurants, cafés, bars) | Sie | feels informal, is not; formal address has beaten informal by a wide margin in our tests |
| trades (plumbing, heating, roofing, electrical, painting) | Du plus `{{firstName}}` can work | test both; the owner-operator often prefers Du |
| e-commerce owners | Du is common | check the shop's own tone on its site |
| enterprise, public sector | Sie | always |

Rules:
- One address form per pool and per sequence. "Hi Thomas" followed by "kennen Sie das?" reads as a template.
- Formal address requires a salutation column ("Herr", "Frau") with 100 percent fill. Do not infer it from first names.
- Switzerland: no ß (write ss), Swiss German phrasing differs; have a Swiss reader check.
- Austria: titles matter more (Mag., Dr., Ing.). Include them in the salutation column when known.

## Natural German, not translated marketing

"Wir bieten den führenden KI-Assistenten für KMU im DACH-Raum" is not German anyone speaks. Test: would you write this sentence to an acquaintance in a chat message? No: rewrite.

| Instead of | Write |
|---|---|
| effektiv, effizient | funktioniert, spart, geht schneller |
| Lösung | das Ding, das X macht |
| implementieren | einrichten, anschließen |
| Herausforderung | Problem, Ärger, Stress |
| Potenzial | was liegen bleibt |
| kontaktieren | anrufen, melden |
| verpasste Opportunitäten | Anrufe, die keiner abnimmt |
| Kundenzufriedenheit steigern | Leute nicht in der Warteschleife hängen lassen |
| Terminvereinbarung | Termin ausmachen |

Translating copy that worked in English has produced zero positive replies in every attempt we measured. Write native or do not ship.

## Burned phrases with alternatives

Thirty phrases that mark a mail as template, and what to do instead.

| Burned | Instead |
|---|---|
| Ich hoffe, es geht Ihnen gut | delete the line; start with the observation |
| Ich hoffe, meine Mail erreicht Sie gut | delete |
| Ich wollte mich kurz melden | delete; say why you write |
| Mir ist aufgefallen, dass ... (generic) | keep only if the detail is real and rare |
| innovativ, führend, marktführend, zukunftsweisend | say what happens when they use it |
| revolutionär, einzigartig, nahtlos | delete the adjective |
| Synergien | say what each side gets |
| Pain Points | the concrete problem in their words |
| skalieren, optimieren | more of X, less of Y |
| Mehrwert | what they save or gain, in numbers they can check |
| kurz abstimmen | "Passt Dienstag 10 Uhr, zehn Minuten?" |
| Ich wollte nochmal nachhaken | a new angle, or nothing |
| nur eine freundliche Erinnerung | a new angle, or nothing |
| falls Sie meine letzte Mail übersehen haben | delete |
| vertraut von, genutzt von führenden Unternehmen | one nameable peer in their city |
| Branchenführer, Fortune 500 | delete |
| nur für kurze Zeit, verpassen Sie nicht, jetzt handeln | tie urgency to their real trigger |
| 10x mehr Umsatz, garantierter Erfolg | a sourced figure or no figure |
| Ich habe gesehen, Sie stellen ein (generic) | name the role and why it matters |
| Glückwunsch zum Wachstum | delete |
| Lassen Sie uns kurz telefonieren | a question they can answer with one word |
| 15 Minuten in Ihrem Kalender | delete; no calendar ask in touch 1 |
| I hope this finds you well | delete |
| just checking in, touching base, circling back | a new angle, or nothing |
| leverage, best-in-class, cutting-edge, seamless | plain verb |
| trusted by, industry leader | one local peer |
| don't miss out, limited time | real trigger or nothing |
| game-changer, 10x | sourced figure or nothing |
| I noticed you're hiring (generic) | name the role, link it to the problem |
| loved your post, congrats on the raise | delete unless you can quote it |

## Disarming and human phrases (German)

- Openers: "Kurze Sache." "Bin über was gestolpert." "Ist ein Schuss ins Blaue, aber:" "Ich mach's kurz."
- Softeners: "Kann gut sein, dass ich hier danebenliege." "Vielleicht habt ihr das längst gelöst." "Reine Vermutung von außen."
- Transitions: "Und jetzt der eigentliche Punkt:" "Nebenbei:"
- Closers: "Wenn's passt, sag einfach Bescheid." "Kein Stress, wenn nicht." "Wenn ich danebenliege, tun Sie einfach so, als wäre die Mail nie angekommen."
- Hooks: "Kurze Frage:" "Sagen Sie mir, wenn ich falsch liege." "Schon mal drüber nachgedacht?"

Adjust to Sie or Du per pool.

## Pattern interrupts that work in DACH

The swearing, bragging style from English-language cold email destroys trust with a painter or a tax practice. What breaks the pattern without losing authority:

1. The self-verifiable proof: "Rufen Sie Freitag um 18:10 mal Ihre eigene Nummer an."
2. We did it, we did not claim it: "Wir haben Dienstag 9:12 bei Ihnen angerufen. Niemand dran, kein Rückruf."
3. Radical brevity: one line and a question in an inbox of 120-word blocks.
4. The anti-sales frame: "Wenn Sie genug Aufträge haben, ist die Mail Unsinn. Dann einfach löschen."
5. Format break: three short lines, one question.
6. The number they can recompute: "Bei 4,7 Sternen und 300 Bewertungen rufen Sie am Tag etwa 20 Leute an. Wenn zwei davon rausfallen ..."

## Local number rule

- A sender phone number must match the market: German number with country code for Germany, Austrian for Austria, Swiss for Switzerland. A foreign number or a number without dialling code reads as a call centre.
- Always write the full international format, e.g. `+49 30 0000000`. Never a bare local number.
- If the CTA is a phone call, use a dedicated number for the CTA that is different from the number in the signature. Otherwise you cannot attribute calls to the campaign.
- Do not put the number in every variant. Some variants ask for a reply, some for a call. Then you can compare.

## Legal awareness note (not legal advice)

This is an operating note, not legal advice. Get a lawyer's view per market before sending.

- In Germany, unsolicited commercial email is restricted by §7 UWG (the unfair competition act). The B2B exception is narrow. Recipients and competitors can send cease-and-desist letters with costs attached. Some professions are known to litigate; treat legal and medical verticals as high-risk or exclude them.
- Austria (§174 TKG) and Switzerland (UWG Art. 3) have their own rules. Do not assume the German reading transfers.
- GDPR applies to business contact data. Document the legitimate-interest basis, keep a suppression list, honour opt-outs immediately, and keep the sender identity and imprint reachable.
- Every message carries an explicit opt-out that costs one word. Process it the same day. Never write "silence means I will stop"; silence is not consent to continue.
- Use public, professional contact data (company listings, registries, company websites). Personal addresses are out.
- LinkedIn has no equivalent email restriction, which is one reason LinkedIn-first sequences are attractive in DACH. Its platform rules still apply.
