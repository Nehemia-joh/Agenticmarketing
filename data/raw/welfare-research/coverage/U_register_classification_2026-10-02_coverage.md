# Slice U coverage: register-only child-focused NGOs (welfare12_U)

Research date 2026-10-02 (work ran past midnight into 2026-10-03; `accessed_on` kept as 2026-10-02 per the brief).
Targets: 153 from `runtime/contacts/slices/welfare12_U.json`. All 153 reached; every one has an organisation record.
Output: `data/raw/welfare-research/research_U_register_classification_2026-10-02.jsonl` (all lines parse; `slice` = "U").

## Counts

- Records: 153 organisation, 7 contact, 7 relationship.
- Segments: Welfare family-based programme 85; Out of scope 49; Welfare funder 11; Welfare specialised centre 6; Welfare residential care 2.
- Verification: unverified 88; needs_review 34; verified 30; historical 1.
  `unverified` = classified from the register mission only (no own site, no dated projects that confirm the activity).
  `needs_review` = register projects or a partial site support the class but scale, route or identity is unconfirmed.

## Method

1. Read every target's NIS register profile (`https://nis.jamii.go.tz/ngo_profile/<id>`) with `scripts/contacts/read_page.py` (153/153 HTTP 200).
2. Read every website listed for a target (46 sites), then contact/about/programme pages where the homepage linked them (via `contact_lib.fetch`, cached, spaced, robots honoured).
3. Location: NIS map pin and nearest-campus distance from `data/raw/welfare-research/nis_catchment_2026-09-22.json` (geocode_basis says so).
4. Searches only for the most promising residential or programme candidates without a site (8 of 8 used).
5. Child stories and sponsorship profiles seen on some sites (New Stars, Pippi House, Kipepeo, Asante Africa) were not recorded.

## Searches (8 allowed, 8 used)

| # | Query | Result |
|---|---|---|
| Q1/8 | "Happy Childhood Foundation" Arusha Tanzania Canaan Children's Home village | No own site. Found Canaan Children's Center (fetched): probable home funded per the register. |
| Q2/8 | "Usa River Children Centre" Tanzania | No match. Incidental names (snippet only, not recorded): Tabasamu Foundation Tanzania (Usa River, Leganga), Ngarasero Community Organization (about 75 children schooled, early learning for 50), Tumaini Children's Foundation, Good Hope Centre orphanage (Usa River), Usa River Rehabilitation and Training Center (ELCT Meru Diocese); Daily News story "20 vulnerable children in Usa River seek education sponsorship". Worth checking against the master. |
| Q3/8 | "Seeds of Kindness" Moshi Tanzania children home | Volunteer organisation supporting Msamaria Children's Home; own site seedsofkindness.or.tz failed DNS. |
| Q4/8 | "Stable Life for Tanzania Kids" Arusha | No match. Incidental: Themi Orphanage, One More Child Compassion House (near Arusha), Future for Kids (Arusha), SOS Children's Village Arusha. |
| Q5/8 | "Bandari ya Maendeleo" Arusha sponsorship children school | Found The Bandari Project (Mto wa Mbu), probable match (pages fetched). Incidental: Selfless Solutions (private-school sponsorship, Arusha), Arusha Kids Trust (20 primary scholarships), Arusha Kids. |
| Q6/8 | "Furahia Mtoto Foundation" Arusha | Snippets: free daycare/pre-school since 2018; own site 403 so not read. |
| Q7/8 | "Help for the Maasai" organization Arusha education needy children | No match. Incidental: Maasai Education Foundation (boarding school scholarships), Maasai Children Education, Nashipay Maasai Initiatives (Makuyuni). |
| Q8/8 | TRMEGA Arumeru "Training, Research, Monitoring and Evaluation on Gender and AIDS" | Snippet: MVC programme since 2011 pays school costs; Netzkraft partner page timed out and WebFetch refused the domain. |

## Blocks and unreadable pages (recorded, not worked around)

- https://furahiafoundation.org/ - HTTP 403.
- https://www.liftedstrong.org/ - HTTP 403.
- https://www.wvi.org/tanzania - HTTP 403.
- https://www.lesolstice.org/about - HTTP 429 (homepage read earlier).
- https://www.osotuwa.org/sponsor-details and /contact - HTTP 429 (homepage read).
- https://www.samequalitiesfoundation.org/ - robots.txt disallows: left for a browser pass (tag risky).
- https://thv.or.tz/ - SSL hostname mismatch.
- https://seedsofkindness.or.tz/ - DNS failure.
- https://www.netzkraft.net/profil.php?teilnehmer=20174&lg=en - connection timeout; WebFetch: domain access denied.
- http://upendokwanza.org/ - domain expired (registrar page).
- Script-rendered, no readable text: dyslexiatanzania.org, gilyschildrenfoundation.org, nafgemtanzania.or.tz (title only), afotatz.org (partly).
- Missed guesses (404, harmless): bassari.de/english/contact-us, /english/about-us, /english/contact; afotatz.org/contacts; africanmoons.org/shalom-centre-orphanage.

## Strongest leads

- Hope and Soul Tanzania: family support for 100+ children, pays government/private school or daycare; also funds Women's Christian Orphanage.
- ProManity International (Pippi House): shelter for about 70 girls aged 7-20 in Arusha; all attend school.
- Bassari Community Empowerment and Development: children's home at Ngyani, Meru (Usa River PO Box).
- New Stars Foundation (Usa River, Leganga): free daycare/pre-school for 38 children; seeks sponsors for primary fees; founder's work email.
- From Hearts 2 Hands: sponsors children at private school near Usa River.
- Tupendane Foundation (TUFOI): pays school fees, audited 2025 accounts.
- Gem Legacy: Sanawari primary scholarships (2023) and orphan fees.
- African Moons and Kid Care International: US funders of Shalom Centre orphanage and the Safe Home for Children with Disabilities.
- Foundation Le Solstice Tanzania: quarterly school sponsorship programme 2025-2026.
- HalevAfrica (Moshi), Kipepeo Family Foundation (Moshi): school-fee sponsorship.

## Gaps

- 88 records are `unverified`: most have only a register entry (no site found, no search spent), so their class rests on the mission statement; a few have a blocked or unreachable site.
- Daily News story on 20 vulnerable Usa River children seeking sponsorship (Q2) was not read.
- Named homes not yet identified as records: Shalom Centre Orphanage, Safe Home for Children with Disabilities, Women's Christian Orphanage, Canaan Children's Home (probably Canaan Children's Center), Grace orphanage children's center (THV), Sara Orphanage (Glory Reach), Msamaria Children's Home / Msamaria Center (Moshi).
- Work emails found: fthomas@asanteafrica.org (role not stated), jvann@africanmoons.org (role not stated), elizabeth@newstarsfoundation.org (founder). No other named work emails.

## Pages read per target (fetched sources in the records)

- ACHA WACHEZE: https://nis.jamii.go.tz/ngo_profile/14218
- ADVENTIST DEVELOPMENT AND RELIEF AGENCY: https://nis.jamii.go.tz/ngo_profile/504, https://adratanzania.org/, https://adratanzania.org/contact-us/, https://adratanzania.org/action-for-right-and-inclusion-of-children-with-albinism/
- AFRICA MASTERPIECE CHILDREN ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/11766
- AFRO RURAL DEVELOPMENT CONSORTIUM: https://nis.jamii.go.tz/ngo_profile/14103
- AHSANTE FOUNDATION TANZANIA (AFOTA): https://nis.jamii.go.tz/ngo_profile/16623, https://afotatz.org/contact.php, https://afotatz.org/leadership.php
- ARUSHA YOUNG  FEMALE RECOVERY COMMUNITY (AYOFERC): https://nis.jamii.go.tz/ngo_profile/9953
- ASANTE AFRICA TANZANIA: https://nis.jamii.go.tz/ngo_profile/4729, https://asanteafrica.org/, https://asanteafrica.org/contact-us/
- ASHE FOUNDATION: https://nis.jamii.go.tz/ngo_profile/17791
- African Moons Tanzania: https://nis.jamii.go.tz/ngo_profile/686, https://africanmoons.org/home/, https://africanmoons.org/special-needs/, https://africanmoons.org/contact-us/
- Alliance on Traditional Practices and Women Empowerment (ATPWE): https://nis.jamii.go.tz/ngo_profile/6941
- Bassari Community Empowerment and Development: https://nis.jamii.go.tz/ngo_profile/424, https://www.bassari.de/childrens-home-tanzania/, https://www.bassari.de/contact/
- Benjamin Runga Foundation: https://nis.jamii.go.tz/ngo_profile/13974, https://benjaminrungafoundation.org/
- Bridge foundation: https://nis.jamii.go.tz/ngo_profile/14823
- Butterfly Africa: https://nis.jamii.go.tz/ngo_profile/21549
- CENTRAL CHILDREN SUPPORT (CCS): https://nis.jamii.go.tz/ngo_profile/18151
- Change your life Foundation: https://nis.jamii.go.tz/ngo_profile/22582
- Child & Youth Development Center - DLBC: https://nis.jamii.go.tz/ngo_profile/13312
- Children Talents Identification and Development Organization: https://nis.jamii.go.tz/ngo_profile/4473
- Children, Youth education and Talent Empowerment Organisation (CHAYETEO): https://nis.jamii.go.tz/ngo_profile/10581, https://satinofootballacademy.com/
- DINKWA WOMEN DEVELOPMENT ORGANIZATION (DIWODEO): https://nis.jamii.go.tz/ngo_profile/4914
- DOVE FOUNDATION: https://nis.jamii.go.tz/ngo_profile/18056
- DYSLEXIA TANZANIA: https://nis.jamii.go.tz/ngo_profile/17121, https://www.dyslexiatanzania.org/
- EASTERN STAR CHILDREN ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/4968
- EDUCATION FOR CHILDREN IN NEED (ECN): https://nis.jamii.go.tz/ngo_profile/5031
- EJUNG'O CHILD AND YOUTH FOUNDATION: https://nis.jamii.go.tz/ngo_profile/12946
- ELECTIVE DEVELOPMENT VOLUNTEERS ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/7282
- ELLE PEUT NAIDIM (EPN): https://nis.jamii.go.tz/ngo_profile/11823, https://www.epn.or.tz/
- ELY EDUCATION VISION ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/20313, https://www.ely-school.org/, https://www.ely-school.org/contact
- EMBUAN CHILDREN AND YOUTH FOUNDATION (ECYF): https://nis.jamii.go.tz/ngo_profile/5009
- EMPATHY FOUNDATION  TANZANIA: https://nis.jamii.go.tz/ngo_profile/23366
- ESAM Foundation for Change: https://nis.jamii.go.tz/ngo_profile/21882
- Empact Foundation: https://nis.jamii.go.tz/ngo_profile/18013
- Every Child Count: https://nis.jamii.go.tz/ngo_profile/11096
- Exploration Kids Organization - EKO: https://nis.jamii.go.tz/ngo_profile/20034
- FINNISH SPECIAL EDUCATION IN AFRICA ry: https://nis.jamii.go.tz/ngo_profile/12687, https://www.fsea.fi/
- FOUNDATION LE SOLSTICE TANZANIA: https://nis.jamii.go.tz/ngo_profile/5185, https://www.lesolstice.org/
- Friends Support for Community Development (FRI-SUCODE) Organization: https://nis.jamii.go.tz/ngo_profile/10487, https://nambala-help.org/
- From Hearts 2 Hands: https://nis.jamii.go.tz/ngo_profile/19405, https://fromhearts2hands.com/, https://fromhearts2hands.com/about/
- Furahia Mtoto Foundation (FUMFO): https://nis.jamii.go.tz/ngo_profile/10377
- GEM LEGACY INC: https://nis.jamii.go.tz/ngo_profile/12715, https://gemlegacy.org/, https://gemlegacy.org/primary-schools/, https://gemlegacy.org/contact/
- GENTECH FOUNDATION: https://nis.jamii.go.tz/ngo_profile/13422, https://gentechfoundationtz.org/
- GLORY REACH AND HELP FOUNDATION: https://nis.jamii.go.tz/ngo_profile/5358
- GOOD HOPE KIWAWA FOUNDATION: https://nis.jamii.go.tz/ngo_profile/20503
- Gily's Children Foundation: https://nis.jamii.go.tz/ngo_profile/14796, https://www.gilyschildrenfoundation.org/
- Glory Vision Tanzania: https://nis.jamii.go.tz/ngo_profile/11639
- Green Future and Community Development Tanzania Organization.: https://nis.jamii.go.tz/ngo_profile/18505
- Green Path Foundation (Green PF): https://nis.jamii.go.tz/ngo_profile/25118
- HALEVAFRICA: https://nis.jamii.go.tz/ngo_profile/18516, https://halevafrica.com/, https://halevafrica.com/our-story/
- HANDS FOR CHILDREN AND WOMEN IN TANZANIA (HACHAWOTA): https://nis.jamii.go.tz/ngo_profile/4526
- HEALTH INITIATIVE FOR KIDS AND ELDERS (HIKE): https://nis.jamii.go.tz/ngo_profile/11832
- HELP FOR THE MAASAI ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/5500
- HOPE FOR CHILDREN ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/13098
- HOPE SEED INITIATIVES: https://nis.jamii.go.tz/ngo_profile/11385
- HUSNA FOUNDATION: https://nis.jamii.go.tz/ngo_profile/18410
- Happy Childhood Foundation: https://nis.jamii.go.tz/ngo_profile/381, https://www.canaanchildrenscenter.com/
- Hope Bearers: https://nis.jamii.go.tz/ngo_profile/15621
- Hope and Soul Tanzania: https://nis.jamii.go.tz/ngo_profile/12983, https://hopeandsoul.org.uk/about-us/, https://hopeandsoul.org.uk/contact-us/
- Huduma ya Kijamii Tanzania (HKT): https://nis.jamii.go.tz/ngo_profile/14402
- I Want to Be Foundation: https://nis.jamii.go.tz/ngo_profile/22294
- JAMII IMARIKA FOUNDATION: https://nis.jamii.go.tz/ngo_profile/17231
- JAMII INNOVATION: https://nis.jamii.go.tz/ngo_profile/16885
- KABILA MOJA IMPACT: https://nis.jamii.go.tz/ngo_profile/17582
- KALULU  CHARITABLE  FOUNDATION: https://nis.jamii.go.tz/ngo_profile/19117
- KILI-HOPE ORGANISATION: https://nis.jamii.go.tz/ngo_profile/12284
- KILIMANJARO SMILEY FOUNDATION: https://nis.jamii.go.tz/ngo_profile/16478
- KINGDOM CHILDCARE ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/18619
- KUJALI FOUNDATION TANZANIA (KFT): https://nis.jamii.go.tz/ngo_profile/18035
- KUZA KIPAJI ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/17981
- Kid Care International: https://nis.jamii.go.tz/ngo_profile/2550, https://kidcare.org/, https://kidcare.org/orphanage/, https://kidcare.org/contact/
- Kujengana Network: https://nis.jamii.go.tz/ngo_profile/18335
- LEAD  FOR HUMAN CARE AND SHARE ORGANIZATION (LEHCSO): https://nis.jamii.go.tz/ngo_profile/5377
- LEADING BY FEEDING AFRICA: https://nis.jamii.go.tz/ngo_profile/17176
- LEARNING MINDS AFRICA ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/4076
- LIFE BRIDGE FOUNDATION: https://nis.jamii.go.tz/ngo_profile/17059
- LIFTED STRONG COMMUNITY ORGANIZATION (LISCO): https://nis.jamii.go.tz/ngo_profile/7846
- LIGHT FOR MANY: https://nis.jamii.go.tz/ngo_profile/14608
- LIKALILO INITIATIVES FOUNDATION: https://nis.jamii.go.tz/ngo_profile/16712
- LIPO TUMAINI ORGANIZATION (LTO): https://nis.jamii.go.tz/ngo_profile/19551
- LITTLE PROSPECTS FOUNDATION (LPF): https://nis.jamii.go.tz/ngo_profile/18204
- LOVING BY ACTIONS ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/20087
- Lomayana-Saint: https://nis.jamii.go.tz/ngo_profile/18323
- MALEZI AIDS/CARE AWARENESS ORGANIZATION (MACAO): https://nis.jamii.go.tz/ngo_profile/22511
- MAMA ZETU FOUNDATION: https://nis.jamii.go.tz/ngo_profile/14539
- MESHACK ERETO FOUNDATION: https://nis.jamii.go.tz/ngo_profile/15920
- MORAVIAN NORTHERN SOCIAL DEVELOPMENT ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/19706
- MOTHER AND CHILD CARE: https://nis.jamii.go.tz/ngo_profile/4080
- Maasai Women and Children Initiative ( MWACI-Ogranization): https://nis.jamii.go.tz/ngo_profile/18160, https://mwaci.org/
- Marangu Anza Pamoja Organization: https://nis.jamii.go.tz/ngo_profile/13564, https://www.anza-pamoja.com/
- Masola Foundation: https://nis.jamii.go.tz/ngo_profile/10834
- Milelo Tanzania Organization: https://nis.jamii.go.tz/ngo_profile/22321, https://www.milelo.de/
- NAFGEM Tanzania: https://nis.jamii.go.tz/ngo_profile/6915, https://www.nafgemtanzania.or.tz/
- NDOTO ZETU: https://nis.jamii.go.tz/ngo_profile/11826, https://ndotozetu.or.tz/
- NEEMAH WINGS FOUNDATION: https://nis.jamii.go.tz/ngo_profile/21394
- NEW STARS FOUNDATION: https://nis.jamii.go.tz/ngo_profile/11923, https://newstarsfoundation.org/about-us/, https://newstarsfoundation.org/projects/education/
- NIKUMBUKE LEO ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/11514
- NURU YETU FOUNDATION: https://nis.jamii.go.tz/ngo_profile/14867, https://www.nuruyetufoundation.org/
- Ndoto in Action (NIA): https://nis.jamii.go.tz/ngo_profile/11707, https://ndotoinaction.or.tz/
- O'BRIEN SCHOOL FOR THE MAASAI: https://nis.jamii.go.tz/ngo_profile/7544, https://www.obrienschool.org
- OKIA TANZANIA: https://nis.jamii.go.tz/ngo_profile/17534
- OSOTUWA FOUNDATION: https://nis.jamii.go.tz/ngo_profile/16360, https://www.osotuwa.org/
- PASSIONATE KIDS CONNECT: https://nis.jamii.go.tz/ngo_profile/21046
- PROJECT ZAWADI INCORPORATED: https://nis.jamii.go.tz/ngo_profile/5274, https://projectzawadi.org/students/student-program-overview/, https://projectzawadi.org/
- ProManity International: https://nis.jamii.go.tz/ngo_profile/11362, https://promanity.de/ueber-uns-pippi-house-foundation/, https://promanity.de/kontakt/
- RELIGHT WINGS FOUNDATION: https://nis.jamii.go.tz/ngo_profile/22508
- RESTORE HOPE FOR YOUTH: https://nis.jamii.go.tz/ngo_profile/15689
- SAFARIS WITH A HEART: https://nis.jamii.go.tz/ngo_profile/15157, https://safariswithaheart.com/charity-projects/current-projects/
- SAIDIA WANAJAMII TANZANIA (SAWATA): https://nis.jamii.go.tz/ngo_profile/7641
- SEEDS OF KINDNESS ORGANIZATION (SOK): https://nis.jamii.go.tz/ngo_profile/15948
- ST. SIMON TOMORROW RETURN OF HOPE FOUNDATION: https://nis.jamii.go.tz/ngo_profile/17991
- STABLE LIFE FOR TANZANIA KIDS FOUNDATION: https://nis.jamii.go.tz/ngo_profile/5271
- STUDENTS SUPPORT FOUNDATION(SSF): https://nis.jamii.go.tz/ngo_profile/17248
- SUPPORT CHILDREN AND COMMUNITY ADVANCEMENT   (SUCARE): https://nis.jamii.go.tz/ngo_profile/8810
- Salama Foundation Tanzania: https://nis.jamii.go.tz/ngo_profile/19516
- Shujaa wa Upendo Initiative (SUI Tanzania): https://nis.jamii.go.tz/ngo_profile/22579
- Son and Oscar Foundation: https://nis.jamii.go.tz/ngo_profile/16173
- Starving children: https://nis.jamii.go.tz/ngo_profile/16291
- TABASAMU AFRICA ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/13710, https://tabasamuafrica.org/, https://tabasamuafrica.org/contacts/
- TANZANIA HOST VOLUNTEER (THV): https://nis.jamii.go.tz/ngo_profile/14662
- TARAMA WOMEN FOUNDATION: https://nis.jamii.go.tz/ngo_profile/18458
- THE BANDARI YA MAENDELEO ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/4976, https://thebandariproject.com/about/, https://thebandariproject.com/contact/
- THE LITTLE OASIS FOUNDATION (TLOF): https://nis.jamii.go.tz/ngo_profile/19216, https://thelittleoasisfoundation.org/our-programs/
- THE SAME QUALITIES FOUNDATION (SQF): https://nis.jamii.go.tz/ngo_profile/4833
- TODAY'S CHILDREN  AND YOUTH LIFE ORGANIZATION (TCYLO): https://nis.jamii.go.tz/ngo_profile/4677
- TRAINING, RESEARCH, MONITORING AND EVALUATION ON GENDER AND AIDS (TRMEGA): https://nis.jamii.go.tz/ngo_profile/4578
- TREE OF LOVE FOUNDATION: https://nis.jamii.go.tz/ngo_profile/275
- TUPENDANE FOUNDATION AND INITIATIVES (TUFOI): https://nis.jamii.go.tz/ngo_profile/13550, https://www.tupendanefoundation.or.tz/, https://www.tupendanefoundation.or.tz/contact-us
- The Foundation for African Empowerment (FAE): https://nis.jamii.go.tz/ngo_profile/5186, https://www.thefaeafrica.org/provide-assistive-learning-devices-and-sponsorship/, https://www.thefaeafrica.org/contact-us/
- The Hearts of Hope Foundation Tanzania: https://nis.jamii.go.tz/ngo_profile/23827
- The Kutamani Foundation: https://nis.jamii.go.tz/ngo_profile/11875
- UGUTU COMMUNITY FOUNDATION: https://nis.jamii.go.tz/ngo_profile/21208
- UNITED WE CHANGE LIVES: https://nis.jamii.go.tz/ngo_profile/16346
- USA-RIVER CHILDREN CENTRE: https://nis.jamii.go.tz/ngo_profile/4508
- Upendo Kwanza: https://nis.jamii.go.tz/ngo_profile/16812, http://upendokwanza.org/
- Uplifting  and Nurturing Them: https://nis.jamii.go.tz/ngo_profile/19013
- VICTORY OF WOMEN AND CHILDREN FOUNDATION: https://nis.jamii.go.tz/ngo_profile/18246
- VOLANTE'S EAGLES ORGANIZATION (VEO): https://nis.jamii.go.tz/ngo_profile/24879
- VUKA INITIATIVE: https://nis.jamii.go.tz/ngo_profile/10647
- Vision of East African Child: https://nis.jamii.go.tz/ngo_profile/5245
- Volcano Development of Children's (VODEC): https://nis.jamii.go.tz/ngo_profile/5772
- WAMOJA FOUNDATION: https://nis.jamii.go.tz/ngo_profile/24398
- WARIOBA CHILD COMPASSION: https://nis.jamii.go.tz/ngo_profile/237
- WATOTO FUTURE INITIATIVES: https://nis.jamii.go.tz/ngo_profile/12129
- WE CARE AID (WCAid) Organization: https://nis.jamii.go.tz/ngo_profile/13618
- WILLOWS INTERNATIONAL TANZANIA: https://nis.jamii.go.tz/ngo_profile/593
- WINGS OF CHANGE (WOC): https://nis.jamii.go.tz/ngo_profile/18629
- WOMEN AND CHILD VISION (WOCHIVI): https://nis.jamii.go.tz/ngo_profile/10398
- WOMEN INITIATIVES FOR THE STREET AND WORKING CHILDREN' WELFARE (WIWOCHI): https://nis.jamii.go.tz/ngo_profile/4410, https://wiwochi.org/, https://wiwochi.org/contact-us/
- WORLD VISION TANZANIA: https://nis.jamii.go.tz/ngo_profile/4372
- Wings Children Foundation (WCF): https://nis.jamii.go.tz/ngo_profile/18623
- YOUNG MINDS EDUCATION ORGANIZATION: https://nis.jamii.go.tz/ngo_profile/13599, https://ymearusha.org/
- YOUTH POWER IN SOCIAL ACTION: https://nis.jamii.go.tz/ngo_profile/5229
- ZION GATES FOUNDATION: https://nis.jamii.go.tz/ngo_profile/13174, https://ziongates.org/
- kipepeo family foudation: https://nis.jamii.go.tz/ngo_profile/1214, https://www.kipepeo-kiwavi.com/english/go-2-school/, https://www.kipepeo-kiwavi.com/english/contact/
