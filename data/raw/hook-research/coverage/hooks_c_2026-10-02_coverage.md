# Hook research coverage: hooks_c, 2026-10-02

## Searches (2 of 5 used)

- Q1/5: "Selian Lutheran Hospital" Arusha Hospital Director (Selian: the lead has no website and its source page returned 404).
- Q2/5: "Livingstone's Africa" Arusha safari (Livingstone's Africa: the site returns 404).
- Q3 to Q5: not used.

## Pages read per organisation (all through scripts/contacts/read_page.py)

- Selian Lutheran Hospital (O98e535c184cf), status partial:
  - https://elcthealth.tz/selian-hospital-2/ (HTTP 404)
  - https://elcthealth.tz/ (home)
  - https://elcthealth.tz/selian-lutheran-hospital/ (HTTP 404)
  - https://www.ghm.org/blog/interview-with-dr-amon
  - https://www.ghm.org/blog/selian-lutheran-hospital
  - https://selianlh.or.tz/ (SSL certificate hostname mismatch: not read)
- Africa Dream Safaris (O624575550ed4), status found:
  - https://africadreamsafaris.com/about-us/
- Afroriginal Tours & Safaris Ltd (Od55a251feb55), status partial:
  - https://afroriginaltours.com/about-us/afroriginal/
- Babji Tours & Safari Ltd (O387cf2af29cf), status partial:
  - https://babjisafaris.com/
- Blue Lotus Travel & Tours Ltd (O59a1de3f78bf), status found:
  - https://bluelotus.co.tz/about-us/
- BUSHBUCK SAFARIS LIMITED (O8e2124eb99e3), status found:
  - https://www.bushbuckltd.com/managing-director
  - https://www.bushbuckltd.com/ (home)
  - https://www.bushbuckltd.com/company-profile
  - https://www.bushbuckltd.com/our-drivers
- Destiny Explorers Limited (O46d07ec685eb), status found:
  - https://destinyexplorers.com/destiny-explorers/
- Eyes Of Tanzania Limited (O96691b5cc950), status partial:
  - https://eyes-of-tanzania.com/about-us/
- Golos of Africa (O220baf9b6782), status partial:
  - https://golos.africa/o-nas/
- HP Safaris (T) Limited (Of97bcc50b8b4), status found:
  - https://www.hors-pistes-en-tanzanie.fr/agence-de-voyage-tanzanie/
- JM Tours Ltd (Oed0d744628cc), status found:
  - https://jmtours.com/best-tanzania-safari-company/
- K&K Safaris (O97e95eaae0be), status partial:
  - https://kandksafaris.com/agence-locale-tanzanie/
- Kilimanjaro Adventure Safari Club (KASC) (O691bf1115e5b), status partial:
  - https://www.kilimanjarotrekk.com/meet-our-team/
- Kukua Tours And Safaris Limited (Ob20dfab2e570), status partial:
  - https://kukuasafaris.com/about-us/
- Livingstone's Africa Ltd (Of5bbe1d9b42c), status blocked:
  - https://www.livingstonesafrica.net/ (HTTP 404)
  - https://www.livingstonesafrica.net/about-1 (HTTP 404)
  - https://livingstonesafrica.net and /about-1, https://www.livingstonesafrica.net/about-us and /about (all HTTP 404)
  - https://livingstonesafaritanzania.com/ (home; possible related operator, not confirmed, nothing recorded)
- Makini Tanzania (Oc0e8837d2496), status partial:
  - https://makinitanzaniasafaris.com/about-us/
- Mshele Tanzania Adventures (O3e7639b222fd), status partial:
  - https://msheleadventures.com/en/our-experts (names not rendered)
  - https://www.msheleadventures.com/ru/our-experts (names shown)
  - https://www.msheleadventures.com/ (home)
  - /en/about, /en/about-us, /en/our-story (HTTP 404)
- Parks East Africa Ltd (O59ec53702e66), status found:
  - https://parkeastafrica.com/about-us
- Safari Crew Tanzania (O6ca0b7c8b95f), status blocked:
  - https://www.safaricrewtanzania.com/chi-siamo/ and https://www.safaricrewtanzania.com/ (robots.txt disallows: not read)
- Safari.Africa (O3ef6297075e2), status partial:
  - https://www.safari.africa/our-story
- Serengeti Balloon Safaris (O108f9c734a63), status found:
  - https://www.balloonsafaris.com/our-story
- Tandala Expeditions Limited (Oc01d9612e3c1), status found:
  - https://www.tandala.com/tandala-expeditions/
- Tanzania Safari Bug Ltd. (O7b205e374ee6), status found:
  - https://tanzania-safari-bug.com/about-us/
- Translen Investments and Trading Ltd (O0dc73adc45e1), status found:
  - https://transleninvestments.com/about-us/
- Wild Pride Safaris (O894cfb463c23), status found:
  - https://wildpridesafaris.com/mds-message/
- Wise Safari Tanzania Limited (O05b1c06eaeaa), status found:
  - https://www.travelwisesafari.com/about-us

## Blocked or unreadable sources

- Selian Lutheran Hospital: contact source page returns HTTP 404; the hospital's own site selianlh.or.tz has an invalid SSL certificate for its hostname (not bypassed).
- Livingstone's Africa: the whole site returns HTTP 404 on every page tried; the three contacts are unreachable.
- Safari Crew Tanzania: robots.txt disallows the contact page and the home page, so nothing was read (not worked around; the user's browser route for robots-disallowed sites is for a person or the coordinator to decide).
- Mshele Tanzania Adventures: the /en/our-experts page rendered without names under read_page; the /ru/ version of the same page was used for the role check.

## Role checks

- confirmed: 39 contacts. unreachable: 5 contacts (Selian 1, Livingstone's Africa 3, Safari Crew 1). changed: 0. not_found: 0.
- Confirmed with a note (the page names the person but does not state the exact title): Eyes Of Tanzania (2), K&K Safaris (2), Parks East Africa, Tanzania Safari Bug, Travel Wise Safari (first name only), HP Safaris Jonathan (first name only).

## Hooks written (13)

- Africa Dream Safaris, Blue Lotus, Bushbuck Safaris, Destiny Explorers, HP Safaris, JM Tours, Parks East Africa, Serengeti Balloon Safaris, Tandala Expeditions, Tanzania Safari Bug, Translen, Wild Pride Safaris, Wise Safari.

## Organisations without a hook, and why

- Selian Lutheran Hospital: its pages are unreadable; partner-page facts give no staff programme or size.
- Afroriginal, Babji, Eyes Of Tanzania, K&K Safaris, Kilimanjaro Adventure Safari Club, Kukua, Makini, Safari.Africa: small owner-run sites with no published workforce size, staff programme or community programme.
- Golos of Africa: Moscow-registered sole proprietor serving Russian-speaking travellers; no staff size; a person should check whether it employs staff in Arusha.
- Mshele Tanzania Adventures: team section says 'Team members coming soon'.
- Livingstone's Africa and Safari Crew Tanzania: sources blocked or down.

## Not finished

- None. Every organisation has a line in hooks_c_2026-10-02.jsonl; Livingstone's Africa and Safari Crew Tanzania are marked blocked.
