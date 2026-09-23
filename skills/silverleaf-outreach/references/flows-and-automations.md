# New-contact intake and track selection

Newly acquired organisation and business-contact leads use F12 for intake and AQ00/AQ01/AQ02 for cadence. Marketing calendar and event timing do not control this acquisition path. AQ01 uses F13: one routing request and one check-in after five working days. AQ02 retains the Day 0, +4 working days and +4 working days test. All are design-only and stop on any response or suppression event.

See `new-lead-acquisition-framework.md` for the full record, message-module and expansion rules.

# Silverleaf outreach flows

Version 2026-09-09 marketing v3, with the send steps of F01 and F03 updated on 2026-09-23 (configuration `automation-2026-09-23-offer-v4`) to use the offer-aligned drafts. These are implementation recipes. External sending and recurring jobs remain disabled.

Read [campaign-positioning-and-cadence.md](campaign-positioning-and-cadence.md) before using a Silverleaf claim, parent-language draft, broadcast date or event sequence. Recipient hooks remain verified-only.

## Operating decisions

- Personalised partnership outreach uses Day 0, +4 working days and +4 working days as a measured test. Stop after three delivered messages.
- A fresh parent enquiry receives an acknowledgement, one helpful reminder after two working days and a close-the-loop message five working days later.
- A historical public enquiry receives at most one reviewed requalification reply.
- Event production begins at T-21. A non-responder receives one direct invitation; only an RSVP or explicit opt-in unlocks T-2 and T-1 reminders.
- Public social channels may use the fuller event SOP cadence. Direct lead messages use the lower cadence above.
- Every planned date, fee, discount, event, capacity claim and visit slot must pass its stated approval gate.

## F01

| Step | Trigger | Condition | Action | Delay | Database update | Example | Principle |
|---:|---|---|---|---|---|---|---|
| 1 | One account and recipient selected | Identity, route, role, sender, offer and dynamic facts verified; alternatives inactive | Send the row's request-first message (subject and body) | Day 0 after checks | awaiting_reply; provider ID; delivered_at; campaign_id=C01 | Use the personalised row; include a recipient hook only when hook_status is Verified | Request-first, recipient-centred, one CTA; the offer follows in follow_up_1; PE023 and PE024 |
| 2 | Initial delivered; no reply | No reply, referral, refusal, opt-out, bounce, OOO or active duplicate | Send follow_up_1 (the documented offer) in the same thread | 4 working days after actual delivery | last_step=2; delivered_at | State the documented offer from the offer register, with the campus fit; offer the one-page outline | Add useful context; do not repeat the opening |
| 3 | First follow-up delivered; no reply | All stop checks still pass | Send follow_up_2 (the close) and end the sequence | 4 working days after step 2 delivery | sequence_complete | Ask whether to send the outline or close the conversation | Lower-effort final ask; stop after three delivered messages |

## F02

| Step | Trigger | Condition | Action | Delay | Database update | Example | Principle |
|---:|---|---|---|---|---|---|---|
| 1 | Any reply | Match provider event to account and message; deduplicate | Cancel all pending cold follow-ups for the account and classify the reply | Immediately | conversation or owner_review | No generic automatic pitch | Response handling overrides the cold sequence |
| 2 | Interested | A current owner can confirm audience and format | Draft a short planning response and offer real availability | Same working period or next working day | conversation; owner assigned | Thank you. Could we confirm the audience and the easiest format for one optional session? | Make the next step concrete |
| 3 | Requests details | Approved information is available | Send the concise outline or approved fact sheet | Next working day | details_requested; fact_version recorded | The outline covers the English-medium programme, digital learning, available levels and how families arrange a visit. | Answer the request with approved facts only |
| 4 | Named referral | Referral and contact route verified | Transfer the same account to the referred colleague; keep prior sequence cancelled | After verification | referred; referral_source; new owner | Thank you for pointing me to [colleague]. I will address the outline to them. | One active sequence per organisation |
| 5 | Not now | Recipient gives a future date or period | Record the requested timing and draft one contextual follow-up for that date | Requested date only | deferred; next_action_date | Thank you. I will follow up in [requested period]. | Respect stated timing |
| 6 | Refusal, opt-out, hard bounce or out of office | Event type verified | Suppress on refusal/opt-out/bounce; pause to stated return date for OOO | Immediately | suppressed, channel_invalid or paused; pending steps cancelled | No further sales message; a simple acknowledgement may be used for a human refusal | Stop before scheduling another touch |

## F03

| Step | Trigger | Condition | Action | Delay | Database update | Example | Principle |
|---:|---|---|---|---|---|---|---|
| 1 | SACCOS and committee route selected | Current operation, committee route and locality verified; 2027 facts approved | Send the row's SACCOS request-first message (subject and body) | Day 0 after checks | awaiting_reply; audience=members; campaign_id=C02 | Ask for a short meeting with the committee about members' children's education; no offer terms | Qualification before enrichment; PE015 and PE024 |
| 2 | Initial delivered; no reply | F01 stop checks pass | Send the SACCOS first follow-up in the same thread | 4 working days after actual delivery | last_step=2 | State the family offer and the member-association rate exactly as the offer register records them (Finance must extend the KINEFA rate first); no loan, subsidy or referral claim | Add practical value |
| 3 | First follow-up delivered; no reply | F01 stop checks pass | Send the final low-effort ask and stop | 4 working days after step 2 delivery | sequence_complete | Should I send the member-information outline for a quick review, or close this for now? | Limited pursuit |

## F04

| Step | Trigger | Condition | Action | Delay | Database update | Example | Principle |
|---:|---|---|---|---|---|---|---|
| 1 | Partner session agreed | Audience, owner, date, time, venue, capacity, content and RSVP route confirmed | Open the event brief and asset workflow | At least 21 calendar days before the session | session_scheduled; partner_code; campaign brief | No audience message yet | SOP preparation gate; PE012 |
| 2 | Invitation assets approved | Written approval exists at least 48 hours before scheduled delivery | Give the approved invitation to the partner for circulation | Default 14 calendar days before the session, or approved date | invitation_shared; fact_version; asset_version | Silverleaf Academy will hold an optional admissions Q&A for [Partner] staff on [confirmed date/time]. | Concrete opt-in route; PE013 and PE017 |
| 3 | Parent opts in | Parent supplies their own contact and preference | Assign admissions owner and acknowledge | Same working period where possible; no later than next working day | parent_opt_in; consent_time; partner_code; owner | Which age or grade are you enquiring about, and which area would you travel from? | Qualify before recommending |
| 4 | Age or grade and area received | Admissions confirms campus fit, availability and current information | Offer real visit slots or the correct application step | After fit check | qualified; visit_offered or application_started | Based on what you shared, we can discuss [confirmed campus]. Would you like to arrange a visit? | Specific relevant next step |
| 5 | Tour, application or enrolment occurs | Actual event recorded by admissions | Update the funnel and report aggregate partner results | On actual event | tour_booked, tour_attended, application or enrollment | No automatic sales message required | Track Inquiry -> Tour -> Application -> Enrollment; PE021 |

## F05

| Step | Trigger | Condition | Action | Delay | Database update | Example | Principle |
|---:|---|---|---|---|---|---|---|
| 1 | Historical enquiry selected | Original author, date, request, source language, current relevance and allowed reply route verified | Prepare one contextual requalification reply | After human review | historical_review; campaign_id=C04 | I saw your [date] enquiry about [specific need] in [area]. Are you still looking? | Use the actual need; no inferred parenthood |
| 2 | One reply approved | Original public route still permits a relevant response | Post or send the one reviewed reply | Once only | requalification_sent; delivered_at | If it would help, reply with the student's age or grade and the area you would travel from. | One answerable question |
| 3 | No reply or enquiry is unrelated | No current interest or outside school scope | Close or hold with the precise reason | No automatic follow-up | closed, stale or outside_scope | No further outreach | Historical interest is not current intent |

## F06

| Step | Trigger | Condition | Action | Delay | Database update | Example | Principle |
|---:|---|---|---|---|---|---|---|
| 1 | Fresh inbound enquiry or explicit opt-in | Valid channel, consent or inbound context, source and owner recorded | Acknowledge and ask for age or grade plus travel area | Same working period where possible; no later than next working day | inquiry; first_response_at; owner; campaign_id=C03 | Tafadhali jibu kwa umri au darasa la mwanafunzi na eneo unalosafiri kutoka. | Low-friction qualification; PE003, PE004 and PE011 |
| 2 | Acknowledgement delivered; no reply | No reply, application, visit, refusal or opt-out | Send one helpful reminder explaining why the two details matter | 2 working days after actual delivery | last_step=2 | Age or grade and travel area help us check the right campus and current information. | Add context, not pressure |
| 3 | Reminder delivered; no reply | All stop checks pass | Send a close-the-loop message and stop | 5 working days after step 2 delivery | sequence_complete | If you would still like information, reply with the student's age or grade and travel area. Otherwise, we will close this enquiry for now. | Clear ending; proposed service-level test |
| 4 | Parent replies | Reply matched to enquiry | Cancel pending reminders and enter F04 fit check | Immediately | current_enquiry; pending steps cancelled | No generic response; answer the stated question | Response overrides nurture |

## F07

| Step | Trigger | Condition | Action | Delay | Database update | Example | Principle |
|---:|---|---|---|---|---|---|---|
| 1 | Open day approved | Campus, date, time, venue, capacity, registration route, owners and content confirmed | Create event brief and assets | 21 calendar days before event | event_confirmed; campaign_id=C05 | No direct message yet | Internal preparation precedes external invitation; PE012 |
| 2 | Direct invitation approved | Recipient is opted in or otherwise appropriate and campus fit is plausible | Send one invitation with one RSVP action | Default 14 calendar days before event | invited; rsvp_pending | Silverleaf Academy will hold an open day at [confirmed campus] on [date/time]. Reply [RSVP] if you would like to join. | One invitation for non-responders; PE017 |
| 3 | RSVP confirmed | Registration exists and event remains confirmed | Send logistics, location and what to bring | 2 calendar days before event | reminder_1_sent | Here are the confirmed time, location pin and joining instructions for your visit. | Reminder only after RSVP |
| 4 | RSVP confirmed; event remains active | No cancellation and no opt-out | Send final concise reminder | 1 calendar day before event | reminder_2_sent | We look forward to welcoming you tomorrow at [confirmed time and campus]. | Practical reminder, no repeated pitch |
| 5 | Attendance recorded | Attendance and parent identity matched | Thank the attendee and offer the next admissions step | Within 1 working day after event | attended; next_step_offered | Thank you for visiting. Would you like us to check the next admissions step for [age/grade]? | Move an actual attendee to the funnel |

## F08

| Step | Trigger | Condition | Action | Delay | Database update | Example | Principle |
|---:|---|---|---|---|---|---|---|
| 1 | Event brief approved | Event details, audience and goal confirmed | Publish the platform-appropriate announcement and begin production | 21 calendar days before event | public_announcement; campaign_id=C06 | Approved event announcement with date, time, venue and one CTA | SOP public cadence; PE012 and PE013 |
| 2 | Announcement live | Approved teaser asset available | Publish teaser or behind-the-scenes content | 14 calendar days before event | teaser_live | 15-30 second Reel or event preparation post | Build interest with new information |
| 3 | Event remains confirmed | Approved countdown and logistics are current | Publish seven-day countdown and community logistics | 7 calendar days before event | countdown_7_live | What to expect, when and where | Useful event detail |
| 4 | Event remains confirmed | Approved story or feature asset available | Publish preview, speaker or student story; public social only | 3 calendar days before event | countdown_3_live | One specific event highlight | Reserve distinct material for follow-up |
| 5 | Event remains confirmed | All platforms and live coverage logistics ready | Publish final public reminder | 1 calendar day before event | final_reminder_live | See you tomorrow at [confirmed details] | Last factual reminder |
| 6 | Event in progress | Approved shot list, media permissions and platform owner active | Publish only the platform-specific live coverage allowed by the SOP | During event | live_coverage_log | WhatsApp maximum two event updates; social cadence follows the SOP | Safeguarding and over-notification controls; PE018 and PE019 |
| 7 | Event ends | Approved photos and copy available | Publish thank-you Stories, photo carousel/album and WhatsApp thank-you | Within 2 hours for Stories; within 24 hours for photos and WhatsApp | post_event_day_1 | Thank the community and show approved highlights | SOP post-event clock; PE014 |
| 8 | Edited video approved | Brand end screen, subtitles, permissions and copy approved | Publish Reel and full highlight video | Within 48 hours for Reel; within 72 hours for YouTube video | post_event_video | One approved highlight story and next action | Accessible, on-brand video; PE014 |
| 9 | Event data reconciled | Platform, registration, attendance and admissions events available | Complete report and debrief | Within 7 calendar days after event | event_reported; learning_logged | No audience send required | Campaign N+1 should reuse the learning |

## F09

| Step | Trigger | Condition | Action | Delay | Database update | Example | Principle |
|---:|---|---|---|---|---|---|---|
| 1 | September admissions broadcast approved | 2027 facts, route, owner and collateral confirmed | Send one admissions announcement to the eligible opt-in audience | Candidate date 2026-09-25; confirm before scheduling | broadcast_1; campaign_id=C07 | Applications for 2027 are open. Reply with student age or grade and travel area. | Planned internal schedule; no fee figures; PE001, PE015 and PE016 |
| 2 | October broadcast approved | No response, application, enrolment, refusal or opt-out; campaign remains current | Send a campus-fit and visit-oriented broadcast | Candidate date 2026-10-31; confirm before scheduling | broadcast_2 | Tell us the student's age or grade and travel area so we can check the right campus and current information. | Primary intake season; PE003 and PE004 |
| 3 | November broadcast approved | Suppression checks pass and a real admissions next step is available | Offer practical application help or a confirmed visit | Candidate date 2026-11-30; confirm before scheduling | broadcast_3 | Would you like current admissions steps or help arranging a campus visit? | Remove false urgency; one useful next step |
| 4 | December broadcast approved | Office coverage and response owner confirmed; suppression checks pass | Send a final new-year check-in and end the planned series | Candidate date 2026-12-31; confirm before scheduling | broadcast_4; sequence_complete | If 2027 is still under consideration, reply with student age or grade and travel area. | Close the loop without a fabricated deadline |

## F10

| Step | Trigger | Condition | Action | Delay | Database update | Example | Principle |
|---:|---|---|---|---|---|---|---|
| 1 | Student enters approved transition cohort | Current family roster, consent basis, grade, campus and transition date verified | Explain the upcoming transition and available confirmed pathways | Proposed 12 weeks before the relevant primary intake window | progression_opened; campaign_id=C08 | We would like to help you plan the next school stage. May we share the confirmed primary options? | Warm lifecycle journey; PE022 |
| 2 | No decision recorded | Family remains eligible and no opt-out | Share a confirmed primary-campus guide | Proposed 8 weeks before intake window | guide_shared | Here are the confirmed campus options and admissions steps for the next stage. | Answer likely questions before asking for a visit |
| 3 | No decision recorded | Real visit slots available | Offer a campus visit | Proposed 4 weeks before intake window | visit_offered | Would you like to visit [confirmed campus] on one of these available dates? | Concrete decision support |
| 4 | No decision recorded | Human owner has reviewed the record | Make one final planning check-in and stop automation | Proposed 1 week before intake window | owner_review; sequence_complete | Would a short planning call help, or should we close this transition conversation for now? | Human review for a high-value warm family |

## F11

| Step | Trigger | Condition | Action | Delay | Database update | Example | Principle |
|---:|---|---|---|---|---|---|---|
| 1 | Referral campaign considered | Referral scheme approval, terms, eligibility, consent and tracking are absent | Do not send or schedule referral copy | Blocked until approval is recorded | blocked; campaign_id=C09 | No reward or referral promise may be drafted as active | The Gantt chart schedules referral-scheme approval through 2026-10-30; PE015 |

## Automation operation

The companion `automation-recipes.json` is design-only. A sending implementation still needs authenticated channels, an agreed sender, selected records, approval state and a reliable event feed for replies, bounces, opt-outs, registrations and admissions outcomes.

Use an idempotency key made from campaign ID, resolved account or enquiry ID and step number. Recheck all stop events immediately before delivery. Calculate working-day delays from actual delivery time in Africa/Nairobi. A scheduler recovery must not produce catch-up bursts.
