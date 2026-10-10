# Government segments, 2026-10-11

Every office in the government run, in one confidence segment, whatever the channel: the letters go by hand or post, and email (where an office publishes an official inbox) is an advance copy at most. Nothing is sent from this repository; a person delivers. Files in runtime/resend/2026-10-11/ (not committed): `government-<confidence>.csv` (Resend import, email rows only) and `government-delivery-<confidence>.csv` (every office: who decides, who can decide quickly, how to deliver).

## Rules

- **High**: the letter is ready (a pilot council's GA01 introduction), it goes to a post whose current holder an official source named within 180 days (leadership profile, or the office's own news), and the postal address comes from an official source.
- **Medium**: the letter is ready, but the addressee's holder is not named or not current in an official source, or the postal address needs confirming. The reason says what to confirm.
- **Low**: the letter is held. Non-pilot councils (promote: add the council to the pilot), district and regional courtesy notices (promote: the B2G owner's approval after the pilot introductions), and every ward and village letter, held until its council introduces us (GA01) and the executive officer is verified within 90 days. Wards carry a wave: first (up to 10 km from a campus), second (10 to 20 km) and later (over 20 km).
- Letters are addressed by title, as Tanzanian protocol expects. The holder's name is for the cover note, the follow-up call and the visit, never a reason to write to a person privately. Named councillors are engaged only through the forum they chair.

## Counts

| Segment | Offices | Of which with an official email (Resend file) |
|---|---:|---:|
| government-high | 4 | 4 |
| government-medium | 0 | 0 |
| government-low | 145 | 7 |

| Segment | Council | District | Region | Ward | Village |
|---|---:|---:|---:|---:|---:|
| high | 4 | 0 | 0 | 0 | 0 |
| medium | 0 | 0 | 0 | 0 | 0 |
| low | 5 | 7 | 3 | 128 | 2 |

Within the segments, `release_order` gives the order of delivery once each gate opens:

| Release order | Offices | Segment |
|---|---:|---|
| 1 now: pilot council introduction | 4 | high |
| 2 after the introduction: pilot ward, first wave | 51 | low |
| 3 after the introduction: pilot ward, second wave | 25 | low |
| 4 courtesy notice after the pilot introductions | 10 | low |
| 5 if the pilot widens: non-pilot council | 5 | low |
| 6 later: non-pilot ward | 11 | low |
| 7 later wave or locate first | 43 | low |

## High and medium: deliver first

| Segment | Office | Letter to | Decides | Quick decision | Postal address | Office phone | Reason |
|---|---|---|---|---|---|---|---|
| high | Halmashauri ya Jiji la Arusha (Arusha City Council) | Mkurugenzi wa Halmashauri (Council Director): Ndg.John L Kayombo | Mkurugenzi wa Halmashauri (Council Director): Ndg.John L Kayombo (current) | - | P.O. Box 3013, Arusha (S.L.P 3013) | +255272548072 | ready; addressed to the Council Director by title, held by Ndg.John L Kayombo (official leadership profile, source dated 2026-09-11); official postal address P.O. Box 3013, Arusha (S.L.P 3013) |
| high | Halmashauri ya Wilaya ya Arusha (Arusha District Council) | Mkurugenzi wa Halmashauri (Council Director): Ndg. Seleman Msumi | Mkurugenzi wa Halmashauri (Council Director): Ndg. Seleman Msumi (current) | Head of Pre-Primary and Primary Education Division: Judith Mrimi (B2G check first) (to confirm); Head of Community Development Division: Stedvant Kileo (to confirm); Council Social Welfare Officer: Beatrice Tengi (to confirm) | P.O. Box 2330, Arusha (S.L.P. 2330) | +255736500476 | ready; addressed to the Council Director by title, held by Ndg. Seleman Msumi (official leadership profile, source dated 2026-10-03); official postal address P.O. Box 2330, Arusha (S.L.P. 2330) |
| high | Halmashauri ya Wilaya ya Hai (Hai District Council) | Mkurugenzi wa Halmashauri (Council Director): Dionis Myinga | Mkurugenzi wa Halmashauri (Council Director): Dionis Myinga (current) | Head of Pre-Primary and Primary Education Division: Musa Kalanje (B2G check first) (to confirm) | P.O. Box 27, Hai, Kilimanjaro (S.L.P. 27) | +255272974369 | ready; addressed to the Council Director by title, held by Dionis Myinga (official leadership profile, source dated 2026-09-08); official postal address P.O. Box 27, Hai, Kilimanjaro (S.L.P. 27) |
| high | Halmashauri ya Wilaya ya Meru (Meru District Council) | Mkurugenzi wa Halmashauri (Council Director): Mwl. Zainabu Juma Makwinya | Mkurugenzi wa Halmashauri (Council Director): Mwl. Zainabu Juma Makwinya (current) | - | P.O. Box 462, Usa River, Arusha (S.L.P 462) | +255272970482 | ready; addressed to the Council Director by title, held by Mwl. Zainabu Juma Makwinya (official leadership profile, source dated 2026-10-08); official postal address P.O. Box 462, Usa River, Arusha (S.L.P 462) |

## Low: held offices

| Office | Letter to | Decides | Postal address | Promote by |
|---|---|---|---|---|
| Halmashauri ya Manispaa ya Moshi (Moshi Municipal Council) | Mkurugenzi wa Halmashauri (Council Director): Bi.Upendo Eric Mangali | Mkurugenzi wa Halmashauri (Council Director): Bi.Upendo Eric Mangali (current) | P.O BOX 318 MOSHI | held: outside the v1 pilot councils; promote: the user adds Moshi Municipal Council to the pilot |
| Halmashauri ya Wilaya ya Monduli (Monduli District Council) | Mkurugenzi wa Halmashauri (Council Director): Bi. happiness R Laizer | Mkurugenzi wa Halmashauri (Council Director): Bi. happiness R Laizer (current) | P.O. Box 1, Monduli (S.L.P 1) | held: outside the v1 pilot councils; promote: the user adds Monduli District Council to the pilot |
| Halmashauri ya Wilaya ya Moshi (Moshi District Council) | Mkurugenzi wa Halmashauri (Council Director): Ndg. Shadrack Mohamed Mhagama | Mkurugenzi wa Halmashauri (Council Director): Ndg. Shadrack Mohamed Mhagama (current) | PO.BOX 3003 MOSHI | held: outside the v1 pilot councils; promote: the user adds Moshi District Council to the pilot |
| Halmashauri ya Wilaya ya Siha (Siha District Council) | Mkurugenzi wa Halmashauri (Council Director): Binuru Mussa | Mkurugenzi wa Halmashauri (Council Director): Binuru Mussa (current) | P.O. Box 129, Siha, Kilimanjaro (S.L.P. 129) | held: outside the v1 pilot councils; promote: the user adds Siha District Council to the pilot |
| Halmashauri ya Wilaya ya Simanjiro (Simanjiro District Council) | Mkurugenzi wa Halmashauri (Council Director): Bw.Gracian Makota | Mkurugenzi wa Halmashauri (Council Director): Bw.Gracian Makota | P.O. Box 9596, Orkesumet, Simanjiro, Manyara | held: outside the v1 pilot councils; promote: the user adds Simanjiro District Council to the pilot; then confirm the director's name from an official source |
| Ofisi ya Mkuu wa Wilaya ya Arumeru (Arumeru District Commissioner's Office) | Katibu Tawala wa Wilaya (District Administrative Secretary): Joseph Mabiti | Mkuu wa Wilaya (District Commissioner): Neema Kichiki Lugangira (current) | - | held: courtesy notice, not a v1 target; promote: the B2G owner approves the notice once the pilot councils have introduced us; find the office's postal address |
| Ofisi ya Mkuu wa Wilaya ya Arusha (Arusha District Commissioner's Office) | Katibu Tawala wa Wilaya (District Administrative Secretary): Jacob Julius Rombo | Mkuu wa Wilaya (District Commissioner): Nicodemus Tambo Mwikozi (current) | - | held: courtesy notice, not a v1 target; promote: the B2G owner approves the notice once the pilot councils have introduced us; find the office's postal address |
| Ofisi ya Mkuu wa Wilaya ya Hai (Hai District Commissioner's Office) | Katibu Tawala wa Wilaya (District Administrative Secretary): Sospeter Magonera | Mkuu wa Wilaya (District Commissioner): Rukia Zuber (current) | - | held: courtesy notice, not a v1 target; promote: the B2G owner approves the notice once the pilot councils have introduced us; find the office's postal address |
| Ofisi ya Mkuu wa Wilaya ya Monduli (Monduli District Commissioner's Office) | Katibu Tawala wa Wilaya (District Administrative Secretary): not named in any official source | Mkuu wa Wilaya (District Commissioner): Gloriana Kimath | - | held: courtesy notice, not a v1 target; promote: the B2G owner approves the notice once the pilot councils have introduced us; find the office's postal address |
| Ofisi ya Mkuu wa Wilaya ya Moshi (Moshi District Commissioner's Office) | Katibu Tawala wa Wilaya (District Administrative Secretary): not named in any official source | Mkuu wa Wilaya (District Commissioner): Godfrey Mnzava | - | held: courtesy notice, not a v1 target; promote: the B2G owner approves the notice once the pilot councils have introduced us; find the office's postal address |
| Ofisi ya Mkuu wa Wilaya ya Siha (Siha District Commissioner's Office) | Katibu Tawala wa Wilaya (District Administrative Secretary): Jane Chalamila | Mkuu wa Wilaya (District Commissioner): Christopher Timbuka (current) | - | held: courtesy notice, not a v1 target; promote: the B2G owner approves the notice once the pilot councils have introduced us; find the office's postal address |
| Ofisi ya Mkuu wa Wilaya ya Simanjiro (Simanjiro District Commissioner's Office) | Katibu Tawala wa Wilaya (District Administrative Secretary): Warda A. Maulid | Mkuu wa Wilaya (District Commissioner): Fakii Lulandala | - | held: courtesy notice, not a v1 target; promote: the B2G owner approves the notice once the pilot councils have introduced us; find the office's postal address |
| Sekretarieti ya Mkoa wa Arusha (Arusha Regional Secretariat) | Katibu Tawala wa Mkoa (Regional Administrative Secretary): Dkt Toba Alnason Nguvila | Mkuu wa Mkoa (Regional Commissioner): Mhe. CPA AMOS GABRIEL MAKALLA (current) | P.O. Box 3050, Arusha | held: courtesy notice, not a v1 target; promote: the B2G owner approves the notice once the pilot councils have introduced us |
| Sekretarieti ya Mkoa wa Kilimanjaro (Kilimanjaro Regional Secretariat) | Katibu Tawala wa Mkoa (Regional Administrative Secretary): Ndg. Kiseo Yusuf Nzowa | Mkuu wa Mkoa (Regional Commissioner): Mhe. Nurdin Hassan Babu (current) | Katibu Tawala, Ofisi ya Mkoa wa Kilimanjaro, P.O. Box 3070, Moshi (S.L.P 3070) | held: courtesy notice, not a v1 target; promote: the B2G owner approves the notice once the pilot councils have introduced us |
| Sekretarieti ya Mkoa wa Manyara (Manyara Regional Secretariat) | Katibu Tawala wa Mkoa (Regional Administrative Secretary): Bi. Maryam Ahmed Muhaji | Mkuu wa Mkoa (Regional Commissioner): Mhe. Queen Cuthbert Sendiga | P.O. Box 310, Babati | held: courtesy notice, not a v1 target; promote: the B2G owner approves the notice once the pilot councils have introduced us |

Wards and villages (all low until their council introduces us), by council and wave:

| Council | First wave (up to 10 km) | Second wave (10 to 20 km) | Later wave (over 20 km) | Locate first |
|---|---:|---:|---:|---:|
| Arusha City Council | 23 | 1 | 0 | 2 |
| Arusha District Council | 12 | 8 | 3 | 3 |
| Hai District Council | 2 | 9 | 1 | 4 |
| Meru District Council | 14 | 7 | 2 | 3 |
| Monduli District Council | 0 | 1 | 4 | 0 |
| Moshi District Council | 0 | 1 | 3 | 0 |
| Moshi Municipal Council | 0 | 2 | 15 | 0 |
| Siha District Council | 2 | 5 | 2 | 0 |
| Simanjiro District Council | 0 | 0 | 1 | 0 |

Ward and village executive officers named by an official source: 3 of 130. Ask each pilot council for the WEO list at the GA01 meeting.

Rules in full: the docstring of scripts/messaging/export_resend_contacts.py. Each row's confidence_reason says what would promote it.
