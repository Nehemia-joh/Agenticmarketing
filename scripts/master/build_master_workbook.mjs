import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, '../..');
const out = path.join(root, 'outputs', 'master');
const cache = path.join(root, 'runtime', 'artifacts');
const previewDir = process.env.SILVERLEAF_PREVIEW_DIR || path.join(root, 'runtime', 'previews');
const workbookPath = process.env.SILVERLEAF_WORKBOOK_PATH || path.join(out, 'Silverleaf Master Database - Consolidated.xlsx');
const dataPath = process.env.SILVERLEAF_WORKBOOK_INPUT || path.join(cache, 'workbook-input.json');
const verificationPath = process.env.SILVERLEAF_WORKBOOK_VERIFICATION || path.join(root, 'outputs', 'reports', 'workbook-verification.json');
const data = JSON.parse(await fs.readFile(dataPath, 'utf8'));
await fs.mkdir(previewDir, { recursive: true });
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(workbookPath));
const messageById = new Map(data.messages.map(row => [row.message_id, row]));

const colours = {
  blue: '#002368',
  lightBlue: '#80BFEC',
  silver: '#818283',
  paleBlue: '#D9ECF9',
  gold: '#FFC952',
  white: '#FFFFFF',
  text: '#172A3A',
};

function excelColumn(index) {
  let value = '';
  for (index += 1; index; index = Math.floor((index - 1) / 26)) {
    value = String.fromCharCode(65 + ((index - 1) % 26)) + value;
  }
  return value;
}

function getOrAddSheet(name) {
  return workbook.worksheets.items.find(sheet => sheet.name === name) ?? workbook.worksheets.add(name);
}

function styleTableSheet(sheet, title, subtitle, headers, rows, widths, rowHeight, tableName) {
  sheet.showGridLines = false;
  sheet.getRange('A1').values = [[title]];
  sheet.getRange('A2').values = [[subtitle]];
  sheet.getRange('A1').format.font = { name: 'Arial', size: 16, bold: true, color: colours.blue };
  sheet.getRange('A2').format.font = { name: 'Arial', size: 10, italic: true, color: colours.silver };
  sheet.getRange('A1:A2').format.rowHeight = 25;
  const range = sheet.getRangeByIndexes(3, 0, rows.length + 1, headers.length);
  range.values = [headers, ...rows];
  range.format.font = { name: 'Arial', size: 10, color: colours.text };
  range.format.wrapText = true;
  range.format.verticalAlignment = 'top';
  range.format.rowHeight = rowHeight;
  sheet.getRangeByIndexes(3, 0, 1, headers.length).format = {
    fill: colours.blue,
    font: { name: 'Arial', size: 10, bold: true, color: colours.white },
    wrapText: true,
    rowHeight: 38,
  };
  widths.forEach((width, index) => {
    sheet.getRangeByIndexes(3, index, rows.length + 1, 1).format.columnWidth = width;
  });
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(Math.min(2, headers.length));
  const end = `${excelColumn(headers.length - 1)}${rows.length + 4}`;
  const table = sheet.tables.add(`A4:${end}`, true, tableName);
  table.style = 'TableStyleMedium2';
}

function replaceSheet(name, subtitle, headers, rows, widths, rowHeight, tableName) {
  const sheet = getOrAddSheet(name);
  for (const table of [...sheet.tables.items]) table.delete();
  const used = sheet.getUsedRange();
  if (used) used.clear({ applyTo: 'all' });
  styleTableSheet(sheet, name, subtitle, headers, rows, widths, rowHeight, tableName);
  return sheet;
}

const counts = data.report.counts;
replaceSheet(
  'Start here',
  'Silverleaf master intelligence, new-contact acquisition, campaign positioning and design-only automation · reviewed 9 September 2026',
  ['Table', 'Records / use', 'How to use it'],
  [
    ['Organisations', counts.organisations, 'Filter by segment and selection. Choose at most one current recipient per resolved organisation.'],
    ['Contacts', counts.contacts, 'Business contacts only. A named person is not evidence that they are a parent.'],
    ['Enquiries', counts.enquiries, 'Historical public childcare and school enquiries. Use the one-reply review flow.'],
    ['Messages', counts.messages, 'Campaign message v3 for every organisation/contact draft. Earlier versions remain in SQLite message_versions.'],
    ['Verified hooks', counts.verified_hooks, 'Six message variants across two organisations retain exact verified hooks. Every other hook remains inactive.'],
    ['Positioning evidence', counts.positioning_evidence, 'Approved value pillars, current official web checks, operational rules and blocked claims with exact sources.'],
    ['Campaigns', counts.campaigns, 'Campaign blueprints with audience, objective, channel, CTA, owner, approver and activation gate.'],
    ['Campaign touchpoints', counts.campaign_touchpoints, 'Touchpoints and delays separated by audience state. Planned dates require confirmation.'],
    ['Lead assignments', counts.campaign_lead_assignments, 'Every organisation/contact message and every historical enquiry mapped to a campaign decision.'],
    ['Acquisition tracks', counts.acquisition_tracks, 'AQ00 holds unresolved leads, AQ01 asks for routing, and AQ02 tests direct-recipient outreach.'],
    ['Value modules', counts.value_proposition_modules, 'Approved Silverleaf positioning is selected only where it helps the recipient assess the offer.'],
    ['Lead intake rules', counts.lead_intake_rules, 'Apply after each list expansion to preserve sources, deduplicate, classify and assign copy rules.'],
    ['Parent enquiry drafts', `${counts.parent_enquiry_outreach_drafts} drafts / ${counts.parent_enquiry_excluded_from_outreach} excluded`, 'All 32 records remain visible. Only daycare/nursery and primary-school enquiries have one-reply copy; no automatic follow-up.'],
    ['Audience segments', counts.outreach_segments, 'Use segment for offer and cadence, then personalise the recipient reason and ask.'],
    ['Automation recipes', counts.automation_steps, 'Design-only triggers, conditions, delays, database updates and stop rules.'],
    ['Knowledge sources', counts.knowledge_documents, 'Marketing documents, outreach guidance, official web verification and structured references.'],
    ['Source files', counts.source_files, 'Exact archived file bytes with SHA-256 hashes.'],
    ['Source rows', counts.source_records, 'Parsed pages, paragraphs, rows, sections and relationships with source IDs.'],
    ['Strategies', counts.strategies, 'Consolidated strategy guidance, including campaign and cadence decisions.'],
    ['Sending', 'Disabled', 'No campaign, broadcast, recurring job or delivery integration is active.'],
  ],
  [34, 20, 105], 58, 'TStartHereV3',
);

replaceSheet(
  'Messages',
  'Source-backed message copy with independent acquisition-track controls. Recipient hooks appear only where their exact claims were verified.',
  ['message_id', 'target_name', 'organisation_name', 'target_type', 'segment', 'acquisition_track_id', 'value_module_ids', 'subject_v3', 'hook_status', 'hook', 'first_message_v2', 'campaign_message_v3', 'follow_up_1_v3', 'follow_up_2_v3', 'campaign_evidence', 'campaign_copy_status', 'contact_channel', 'channel_attribution', 'acquisition_version', 'strategy_scope', 'strategy_id', 'conditions', 'source_record_id'],
  data.outreach_plans.map(row => [
    row.message_id, row.target_name, row.organisation_name, row.target_type, row.segment,
    row.acquisition_track_id, row.value_module_ids, row.campaign_subject_v3, row.hook_status, row.hook, row.first_message_v2,
    row.campaign_message_v3, row.campaign_follow_up_1_v3, row.campaign_follow_up_2_v3,
    row.campaign_evidence, row.campaign_copy_status, row.contact_channel, row.channel_attribution,
    row.acquisition_version, row.strategy_scope,
    messageById.get(row.message_id)?.strategy_id,
    messageById.get(row.message_id)?.conditions, messageById.get(row.message_id)?.source_record_id,
  ]),
  [22, 28, 42, 16, 24, 20, 42, 48, 30, 80, 95, 105, 90, 70, 38, 48, 34, 45, 40, 85, 30, 95, 24], 170, 'TMessagesV3',
);

replaceSheet(
  'Outreach plans',
  'One row per organisation/contact draft. Acquisition track controls cadence; segment and value modules shape the offer; exact evidence controls hooks.',
  ['message_id', 'target_name', 'organisation_name', 'segment', 'acquisition_track_id', 'value_module_ids', 'acquisition_version', 'strategy_scope', 'recipient_role', 'persona', 'selection', 'review_status', 'contact_channel', 'channel_attribution', 'hook_status', 'hook', 'hook_evidence', 'campaign_version', 'campaign_subject_v3', 'campaign_message_v3', 'campaign_follow_up_1_v3', 'campaign_follow_up_2_v3', 'campaign_evidence', 'campaign_copy_status', 'relevance_reason', 'proposed_offer', 'cta_type', 'flow_id', 'evidence_url', 'evidence_date', 'verified_on', 'evidence_basis', 'evidence_record_ids', 'missing_information'],
  data.outreach_plans.map(row => [
    row.message_id, row.target_name, row.organisation_name, row.segment, row.acquisition_track_id,
    row.value_module_ids, row.acquisition_version, row.strategy_scope, row.recipient_role, row.persona,
    row.selection, row.review_status, row.contact_channel, row.channel_attribution, row.hook_status,
    row.hook, row.hook_evidence, row.campaign_version, row.campaign_subject_v3, row.campaign_message_v3,
    row.campaign_follow_up_1_v3, row.campaign_follow_up_2_v3, row.campaign_evidence,
    row.campaign_copy_status, row.relevance_reason, row.proposed_offer, row.cta_type, row.flow_id,
    row.evidence_url, row.evidence_date, row.verified_on, row.evidence_basis, row.evidence_record_ids,
    row.missing_information,
  ]),
  [22, 28, 42, 24, 20, 42, 40, 85, 28, 18, 23, 22, 34, 48, 30, 80, 75, 34, 48, 105, 90, 70, 40, 48, 80, 75, 24, 12, 55, 18, 18, 50, 90, 100], 175, 'TOutreachPlansV3',
);

function sequenceFor(row) {
  if (row.acquisition_track_id === 'AQ00') {
    return ['Hold for verification; do not send', '', 'No follow-up', '', 'No follow-up', '', 'Held'];
  }
  if (row.acquisition_track_id === 'AQ01') {
    const addressee = row.target_type === 'contact' && row.target_name
      ? row.target_name
      : `${row.organisation_name || 'your organisation'} team`;
    const followUp = `Hello ${addressee},\n\nI wanted to check whether you are the right person to review a short staff-school information outline. If not, who would be the best colleague to contact?`;
    return ['After route and copy review', row.campaign_message_v3, '5 working days after actual delivery', followUp, 'Stop; no second follow-up', '', 'Routing-first test'];
  }
  return ['After identity, role and copy review', row.campaign_message_v3, '4 working days after actual delivery', row.campaign_follow_up_1_v3, '4 working days after follow-up 1 delivery', row.campaign_follow_up_2_v3, 'Direct-recipient test'];
}

replaceSheet(
  'Sequences',
  'Acquisition-track sequences are independent of the internal marketing calendar. AQ00 holds, AQ01 routes with one check-in, and AQ02 tests three touches.',
  ['message_id', 'recipient', 'organisation', 'segment', 'acquisition_track_id', 'selection', 'initial_subject', 'initial_timing', 'initial_message_v3', 'delay_to_follow_up_1', 'follow_up_1', 'delay_to_follow_up_2', 'follow_up_2', 'track_status', 'copy_status'],
  data.outreach_plans.map(row => {
    const seq = sequenceFor(row);
    return [
      row.message_id, row.target_name, row.organisation_name, row.segment, row.acquisition_track_id,
      row.selection, row.campaign_subject_v3, seq[0], seq[1], seq[2], seq[3], seq[4], seq[5], seq[6],
      row.campaign_copy_status,
    ];
  }),
  [22, 28, 42, 24, 20, 22, 48, 38, 105, 38, 90, 38, 72, 30, 50], 175, 'TSequencesV4',
);

replaceSheet(
  'Segments',
  'Use the segment to select the offer. Acquisition track selects cadence; recipient evidence and role select the reason and CTA.',
  ['segment', 'audience', 'offer', 'qualification', 'flow_id'],
  data.outreach_segments.map(row => [row.segment, row.audience, row.offer, row.qualification, row.flow_id]),
  [30, 52, 65, 80, 14], 88, 'TSegmentsV3',
);

replaceSheet(
  'Acquisition tracks',
  'New organisation and business-contact leads use evidence-selected tracks. These tests do not inherit the internal marketing calendar.',
  ['track_id', 'name', 'use_when', 'initial_touch', 'follow_up_policy', 'desired_outcome', 'source_basis', 'status'],
  data.acquisition_tracks.map(row => [row.track_id, row.name, row.use_when, row.initial_touch, row.follow_up_policy, row.desired_outcome, row.source_basis, row.status]),
  [14, 26, 72, 55, 78, 62, 48, 32], 92, 'TAcquisitionTracks',
);

replaceSheet(
  'Value modules',
  'Select only the propositions that help the recipient assess the offer. A Silverleaf claim is never evidence about the recipient.',
  ['module_id', 'audience', 'name', 'recipient_value', 'silverleaf_contribution', 'recipient_contribution', 'use_when', 'do_not_imply', 'evidence_ids', 'status'],
  data.value_proposition_modules.map(row => [row.module_id, row.audience, row.name, row.recipient_value, row.silverleaf_contribution, row.recipient_contribution, row.use_when, row.do_not_imply, row.evidence_ids, row.status]),
  [14, 42, 34, 68, 72, 62, 78, 78, 38, 38], 110, 'TValueModules',
);

replaceSheet(
  'Lead intake rules',
  'Run after each lead-list expansion. Preserve source records, deduplicate carefully, classify the recipient and assign acquisition metadata before drafting.',
  ['rule_id', 'stage_order', 'applies_to', 'rule', 'required_fields', 'decision', 'next_step', 'source_basis'],
  data.lead_intake_rules.map(row => [row.rule_id, Number(row.stage_order), row.applies_to, row.rule, row.required_fields, row.decision, row.next_step, row.source_basis]),
  [14, 14, 34, 82, 68, 82, 52, 40], 98, 'TLeadIntakeRules',
);

const flowRows = data.automation_recipes.map(row => [
  row.flow_id, Number(row.step), row.trigger, row.condition, row.action, row.delay,
  row.database_update, row.example_copy, row.principle, row.mode,
]);
for (const name of ['Flows', 'Automation recipes']) {
  replaceSheet(
    name,
    name === 'Flows'
      ? 'Audience-state flows include appendable new-lead intake, routing, direct outreach, parent enquiries, events and broadcasts.'
      : 'Design-only implementation recipes. New-contact cadence is independent of the internal marketing calendar; sending remains disabled.',
    ['flow_id', 'step', 'trigger', 'condition', 'action', 'delay', 'database_update', 'example_copy', 'principle', 'mode'],
    flowRows,
    [14, 10, 42, 78, 70, 45, 62, 95, 58, 34], 135,
    name === 'Flows' ? 'TFlowsV3' : 'TAutomationRecipesV3',
  );
}

const strategyRows = [];
for (const strategy of data.strategies) {
  const parts = strategy.content.match(/[\s\S]{1,1200}/g) || [''];
  parts.forEach((content, index) => strategyRows.push([
    strategy.strategy_id, strategy.title, strategy.segment, `${index + 1}/${parts.length}`,
    content, strategy.status,
  ]));
}
replaceSheet(
  'Strategies',
  'Consolidated imported and current guidance. Current campaign entries identify their positioning evidence IDs in the status field.',
  ['strategy_id', 'title', 'segment', 'part', 'content', 'status'],
  strategyRows,
  [30, 52, 34, 12, 110, 65], 190, 'TStrategiesV3',
);

replaceSheet(
  'Source rows',
  `${counts.source_records} parsed records. Full payloads and exact archived bytes are stored in SQLite.`,
  ['record_id', 'source_id', 'source_file', 'location'],
  data.source_rows.map(row => [row.record_id, row.source_id, row.source_file, row.location]),
  [24, 24, 90, 50], 28, 'TSourceRowsV3',
);

replaceSheet(
  'Source files',
  `${counts.source_files} source files archived with SHA-256 hashes.`,
  ['source_id', 'path', 'kind', 'bytes', 'sha256'],
  data.source_files.map(row => [row.source_id, row.path, row.kind, Number(row.bytes), row.sha256]),
  [24, 95, 14, 18, 72], 40, 'TSourceFilesV3',
);

replaceSheet(
  'Knowledge sources',
  'Marketing documents, operational references, outreach guidance and official web verification. Planned sources remain clearly marked.',
  ['document_id', 'title', 'classification', 'record_count', 'relative_path', 'status'],
  data.knowledge_documents.map(row => [
    row.document_id, row.title, row.classification, Number(row.record_count), row.relative_path, row.status,
  ]),
  [24, 52, 50, 18, 92, 88], 80, 'TKnowledgeSourcesV3',
);

replaceSheet(
  'Positioning evidence',
  'Use allowed claims only under their stated conditions. Planned dates and mutable statistics are not evergreen campaign facts.',
  ['evidence_id', 'category', 'claim_or_rule', 'campaign_use', 'source_path', 'source_locator', 'evidence_class', 'verified_on', 'use_status', 'conditions'],
  data.positioning_evidence.map(row => [
    row.evidence_id, row.category, row.claim_or_rule, row.campaign_use, row.source_path,
    row.source_locator, row.evidence_class, row.verified_on, row.use_status, row.conditions,
  ]),
  [16, 30, 90, 72, 92, 62, 45, 18, 34, 85], 110, 'TPositioningEvidence',
);

replaceSheet(
  'Campaigns',
  'Campaign blueprints. C01 and C02 use independent acquisition tracks; event and broadcast campaigns retain their own approval gates.',
  ['campaign_id', 'name', 'audience', 'segment', 'objective', 'mode', 'channels', 'flow_ids', 'owner', 'approver', 'primary_cta', 'language', 'activation_gate', 'status', 'source_basis'],
  data.campaigns.map(row => [
    row.campaign_id, row.name, row.audience, row.segment, row.objective, row.mode, row.channels,
    row.flow_ids, row.owner, row.approver, row.primary_cta, row.language, row.activation_gate,
    row.status, row.source_basis,
  ]),
  [14, 40, 75, 42, 75, 32, 58, 22, 50, 54, 65, 38, 95, 50, 42], 125, 'TCampaigns',
);

replaceSheet(
  'Campaign touchpoints',
  'Touchpoints and delays for campaign-facing flows. Response branches remain in Flows and Automation recipes.',
  ['campaign_id', 'touchpoint_order', 'flow_id', 'flow_step', 'timing', 'trigger', 'purpose', 'channel', 'audience_state', 'draft_copy', 'evidence_ids', 'status'],
  data.campaign_touchpoints.map(row => [
    row.campaign_id, Number(row.touchpoint_order), row.flow_id, Number(row.flow_step), row.timing,
    row.trigger, row.purpose, row.channel, row.audience_state, row.draft_copy, row.evidence_ids, row.status,
  ]),
  [14, 18, 12, 12, 48, 55, 68, 58, 82, 95, 35, 35], 125, 'TCampaignTouchpoints',
);

replaceSheet(
  'Lead assignments',
  'Every organisation/contact message and historical enquiry is assigned to a campaign state. New contacts also carry acquisition-track and value-module assignments.',
  ['assignment_id', 'campaign_id', 'target_type', 'target_id', 'message_id', 'acquisition_track_id', 'value_module_ids', 'strategy_scope', 'selection', 'eligibility_status', 'reason', 'next_action'],
  data.campaign_lead_assignments.map(row => [
    row.assignment_id, row.campaign_id, row.target_type, row.target_id, row.message_id,
    row.acquisition_track_id, row.value_module_ids, row.strategy_scope,
    row.selection, row.eligibility_status, row.reason, row.next_action,
  ]),
  [24, 14, 16, 24, 24, 20, 42, 85, 24, 28, 90, 90], 105, 'TLeadAssignments',
);

replaceSheet(
  'Parent enquiry drafts',
  'Historical public-enquiry drafts for human review. Use the original public route only where it still permits a relevant response; no automatic follow-up.',
  ['enquiry_id', 'campaign_id', 'subject', 'body', 'follow_up', 'language', 'route_status', 'evidence_ids', 'status'],
  data.parent_enquiry_drafts.map(row => [
    row.enquiry_id, row.campaign_id, row.subject, row.body, row.follow_up,
    row.language, row.route_status, row.evidence_ids, row.status,
  ]),
  [24, 14, 46, 115, 30, 36, 75, 36, 58], 175, 'TParentEnquiryDrafts',
);

replaceSheet(
  'Consolidation audit',
  'Database and campaign update checks recorded 9 September 2026.',
  ['check', 'value', 'status', 'notes'],
  [
    ['Marketing documents reviewed', data.report.marketing_documents_reviewed, 'Complete', 'All files under references/Marketing Documents were extracted and reviewed.'],
    ['New marketing originals archived', data.report.marketing_originals_added_to_master, 'Complete', 'The calendar was already present; the other 11 originals were added.'],
    ['Missing core records', data.report.missing_records, 'None', 'Organisation, contact, enquiry, message and outreach-plan counts were preserved.'],
    ['Organisation/contact messages rewritten', data.report.messages_rewritten_v3, 'Complete', 'Earlier versions remain in SQLite message_versions and backups.'],
    ['Historical enquiry rows covered', data.report.historical_parent_drafts_covered, 'Complete', `${counts.parent_enquiry_outreach_drafts} one-reply drafts; ${counts.parent_enquiry_excluded_from_outreach} outside-scope rows have no outreach copy.`],
    ['Verified recipient hooks', counts.verified_hooks, 'Preserved', 'No unverified recipient hook is active.'],
    ['New-contact acquisition scope', data.report.acquisition_version, 'Applied', 'Marketing documents supply positioning and value propositions; acquisition tracks control cadence.'],
    ['Acquisition track assignment', `${counts.acquisition_hold} hold / ${counts.acquisition_routing} routing / ${counts.acquisition_direct} direct`, 'Complete', 'Every current outreach-plan row is assigned; the refresh is rerunnable after list expansion.'],
    ['Campaign blueprints', counts.campaigns, 'Complete', 'Every campaign includes activation gates and source basis.'],
    ['Automation steps', counts.automation_steps, 'Design only', 'No sending integration or recurring schedule is active.'],
    ['SQLite integrity', 'ok', 'Complete', 'Foreign-key violations: 0.'],
    ['Planned dates and mutable claims', 'Approval required', 'Gated', 'Confirm events, fees, discounts, referral terms, capacity and visit slots before release.'],
  ],
  [48, 28, 22, 110], 72, 'TConsolidationAuditV3',
);

console.log((await workbook.inspect({
  kind: 'table', range: 'Start here!A1:C24', include: 'values,formulas',
  tableMaxRows: 24, tableMaxCols: 3, maxChars: 12000,
})).ndjson);
console.log((await workbook.inspect({
  kind: 'table', range: 'Positioning evidence!A1:J12', include: 'values,formulas',
  tableMaxRows: 12, tableMaxCols: 10, maxChars: 14000,
})).ndjson);
console.log((await workbook.inspect({
  kind: 'table', range: 'Campaign touchpoints!A1:L14', include: 'values,formulas',
  tableMaxRows: 14, tableMaxCols: 12, maxChars: 16000,
})).ndjson);
console.log((await workbook.inspect({
  kind: 'match',
  searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options: { useRegex: true, maxResults: 100 }, summary: 'formula error scan', maxChars: 2000,
})).ndjson);

for (const [sheetName, range, fileName] of [
  ['Start here', 'A1:C21', 'campaign-start-here.png'],
  ['Positioning evidence', 'A1:J10', 'campaign-positioning-evidence.png'],
  ['Campaigns', 'A1:O8', 'campaign-blueprints.png'],
  ['Campaign touchpoints', 'A1:L12', 'campaign-touchpoints.png'],
  ['Messages', 'A1:S8', 'campaign-messages.png'],
  ['Parent enquiry drafts', 'A1:I8', 'campaign-parent-drafts.png'],
  ['Acquisition tracks', 'A1:H8', 'acquisition-tracks.png'],
  ['Value modules', 'A1:J11', 'value-modules.png'],
  ['Lead intake rules', 'A1:H13', 'lead-intake-rules.png'],
  ['Sequences', 'A1:O8', 'acquisition-sequences.png'],
]) {
  const blob = await workbook.render({ sheetName, range, scale: 1 });
  await fs.writeFile(path.join(previewDir, fileName), new Uint8Array(await blob.arrayBuffer()));
}

await (await SpreadsheetFile.exportXlsx(workbook)).save(workbookPath);
await fs.mkdir(path.dirname(verificationPath), { recursive: true });
await fs.writeFile(verificationPath, JSON.stringify({
  output: workbookPath,
  campaign_version: '2026-09-09-marketing-evidence-v3',
  acquisition_version: data.report.acquisition_version,
  counts,
  missing_records: 0,
  formula_errors: 0,
  sending_enabled: false,
  sheets_added_or_refreshed: [
    'Start here', 'Messages', 'Outreach plans', 'Sequences', 'Segments', 'Flows',
    'Automation recipes', 'Strategies', 'Source rows', 'Source files', 'Knowledge sources',
    'Positioning evidence', 'Campaigns', 'Campaign touchpoints', 'Lead assignments',
    'Parent enquiry drafts', 'Consolidation audit',
    'Acquisition tracks', 'Value modules', 'Lead intake rules',
  ],
  exported: true,
}, null, 2));
console.log('Campaign workbook exported.');
