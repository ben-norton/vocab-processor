"""Build a comprehensive, well-documented AgentsTemplate.xlsx.

Patterns and serialisation rules are derived from:
  'Agents in RDF Serializations.md' (internal project reference)
  VocPub 4.x specification
  ISO 19115-3 CIT 1.0 / 2.0 CI_RoleCode codelist

Column design follows the VocPub / schema.org patterns for agents in
SKOS ConceptScheme TTL files:
  - Persons: subject IRI = vocab.geospecimens.org/org/; ORCID → schema:identifier
  - Orgs:    subject IRI = vocab.geospecimens.org/org/; schema:url + schema:homepage
  - Roles:   prov:qualifiedAssociation on the ConceptScheme
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment

# ── colour palette ──────────────────────────────────────────────────────────
C_HEADER_BG  = '1F4E79'   # dark navy   – column header / sheet title rows
C_HEADER_FG  = 'FFFFFF'   # white text
C_SECTION_BG = '2E75B6'   # mid-blue    – section dividers
C_SECTION2   = '4472C4'   # lighter blue – sub-section dividers (2nd namespace)
C_LABEL_BG   = 'D6E4F0'   # pale blue   – key-label cells
C_NOTE_BG    = 'E2EFDA'   # pale green  – instructional body text
C_CODE_BG    = 'F4F4F4'   # near-white  – code / TTL example cells
C_ALT_ROW    = 'EBF3FB'   # very light blue – alternating data rows
C_BORDER     = 'BFBFBF'   # grey border


def thin_border():
    s = Side(style='thin', color=C_BORDER)
    return Border(left=s, right=s, top=s, bottom=s)


def fill(hex_color):
    return PatternFill('solid', fgColor=hex_color)


def body_font(bold=False, size=10, color='000000', italic=False):
    return Font(name='Calibri', bold=bold, size=size, color=color,
                italic=italic)


def code_font(size=9):
    return Font(name='Consolas', size=size, color='1F4E79')


def wrap(h='left', v='top'):
    return Alignment(horizontal=h, vertical=v, wrap_text=True)


def set_col(ws, letter, width):
    ws.column_dimensions[letter].width = width


# ════════════════════════════════════════════════════════════════════════════
wb = openpyxl.Workbook()

# ════════════════════════════════════════════════════════════════════════════
# SHEET 1 — README
# ════════════════════════════════════════════════════════════════════════════
ws_rm = wb.active
ws_rm.title = 'README'
ws_rm.sheet_view.showGridLines = False
ws_rm.column_dimensions['A'].width = 26
ws_rm.column_dimensions['B'].width = 96


def rm_row(ws, r, row_type, col_a, col_b=None):
    """Write one README row and apply formatting."""
    ca = ws.cell(row=r, column=1, value=col_a)
    cb = ws.cell(row=r, column=2, value=col_b)

    if row_type == 'title':
        ca.font = Font(name='Calibri', bold=True, size=16, color=C_SECTION_BG)
        ca.alignment = Alignment(horizontal='left', vertical='center')
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ws.row_dimensions[r].height = 32

    elif row_type == 'section':
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ca.value = col_a
        ca.fill = fill(C_SECTION_BG)
        ca.font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
        ca.alignment = wrap('left', 'center')
        ws.row_dimensions[r].height = 18

    elif row_type == 'kv':
        ca.font = body_font(bold=True)
        ca.fill = fill(C_LABEL_BG)
        ca.alignment = wrap('left', 'top')
        ca.border = thin_border()
        cb.font = body_font()
        cb.alignment = wrap('left', 'top')
        cb.border = thin_border()

    elif row_type == 'body':
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ca.value = col_a
        ca.font = body_font()
        ca.alignment = wrap('left', 'top')
        ca.fill = fill(C_NOTE_BG)

    elif row_type == 'blank':
        ws.row_dimensions[r].height = 6


README_ROWS = [
    ('title',   'Agents Template — SKOS ConceptScheme Turtle Files'),
    ('blank',),
    ('section', 'PURPOSE'),
    ('body',
     'This workbook defines all agents (persons and organisations) associated '
     'with SKOS ConceptScheme vocabulary TTL files. It drives the Agents '
     'section of each .ttl file — schema:Person / schema:Organization '
     'descriptions plus the prov:qualifiedAssociation blocks that link agents '
     'and roles to each ConceptScheme.'),
    ('blank',),
    ('section', 'SERIALISATION PATTERN (VocPub)'),
    ('body',
     'The Turtle patterns below are the normative serialisation targets for '
     'this workbook. All columns in the Agents sheet map to predicates shown '
     'here. See the Mapping sheet for the full predicate-by-predicate breakdown '
     'and the TTL Patterns sheet for copy-ready block templates.'),
    ('kv', 'Person subject IRI',
     'Use a stable vocab.geospecimens.org/org/ IRI as the subject (e.g. '
     'https://vocab.geospecimens.org/org/ben-norton). Store the ORCID in '
     'orcidURI — it becomes schema:identifier, not the subject IRI.'),
    ('kv', 'Person predicates',
     'schema:name  |  schema:identifier (ORCID)  |  schema:email  |  '
     'schema:memberOf (affiliation URI)'),
    ('kv', 'Organization predicates',
     'schema:name  |  schema:url  |  schema:homepage  |  '
     'schema:parentOrganization  |  cmns-av:acronym'),
    ('kv', 'Role attachment on ConceptScheme',
     'prov:qualifiedAssociation [\n'
     '  a prov:Association ;\n'
     '  prov:agent <agentURI> ;\n'
     '  prov:hadRole isoroles:editor ;\n'
     '] ;'),
    ('kv', 'Direct attribution on ConceptScheme',
     'schema:creator <agentURI> ;\n'
     'schema:publisher <agentURI> ;'),
    ('blank',),
    ('section', 'SHEETS IN THIS WORKBOOK'),
    ('kv', 'README',       'Instructions and documentation (this sheet).'),
    ('kv', 'Agents',       'Main data table — one row per agent-affiliation combination.'),
    ('kv', 'Roles',        'CI_RoleCode values from both ISO 19115 namespaces.'),
    ('kv', 'Mapping',      'Column → RDF predicate → TTL pattern mapping table.'),
    ('kv', 'TTL Patterns', 'Copy-ready Turtle block templates for persons, orgs, and ConceptScheme attribution.'),
    ('blank',),
    ('section', 'COLUMN DESCRIPTIONS — Agents sheet'),
    ('kv', 'agentURI',
     'Persistent vocab.geospecimens.org/org/ IRI for this agent '
     '(e.g. https://vocab.geospecimens.org/org/ben-norton). '
     'This is the Turtle subject IRI. Leave blank to use a blank node '
     '(supply blankNodeLabel). '
     'For persons, do NOT use the ORCID here — put it in orcidURI instead.'),
    ('kv', 'blankNodeLabel',
     'Blank-node identifier used when agentURI is empty. The _: prefix is '
     'added automatically (e.g. agent_mineralogy_task_group → '
     '_:agent_mineralogy_task_group). Must be unique across the workbook.'),
    ('kv', 'agentName',
     'Full display name. Maps to schema:name. REQUIRED.'),
    ('kv', 'agentType',
     'RDF type — exactly schema:Person or schema:Organization. REQUIRED. '
     'Use the dropdown in the Agents sheet.'),
    ('kv', 'orcidURI',
     'ORCID IRI for persons (e.g. https://orcid.org/0000-0002-5819-9134). '
     'Maps to schema:identifier. Persons only. Leave blank for organisations.'),
    ('kv', 'hadRole',
     'ISO 19115 CI_RoleCode role(s) this agent plays in the vocabulary. '
     'Use the isoroles: prefix (e.g. isoroles:editor). Comma-separate '
     'multiple values. These become prov:qualifiedAssociation blocks on the '
     'ConceptScheme. See the Roles sheet for valid values and both namespace '
     'options.'),
    ('kv', 'agentEmail',
     'Contact email address. Maps to schema:email. Persons only.'),
    ('kv', 'agentURL',
     'URL of the agent or organisation profile page. Maps to schema:url.'),
    ('kv', 'agentHomepage',
     'Homepage of the organisation. Maps to schema:homepage. '
     'Organisations only. Often the same value as agentURL.'),
    ('kv', 'acronym',
     'Abbreviated name (e.g. TDWG, MinExt). Maps to cmns-av:acronym. '
     'Organisations only.'),
    ('kv', 'memberOfURI',
     'URI of the organisation this agent is a member of. '
     'Maps to schema:memberOf. Use one row per membership — repeat agent '
     'rows for multiple memberships.'),
    ('kv', 'memberOfName',
     'Human-readable name of the memberOf organisation. Used for '
     'documentation and when memberOfURI is blank.'),
    ('kv', 'memberOfRole',
     'The role or title of the person within the memberOf organisation '
     '(e.g. employee, co-convener). Maps to schema:roleName. Optional.'),
    ('kv', 'parentOrgURI',
     'URI of the parent organisation. schema:parentOrganization. '
     'Organisations only.'),
    ('kv', 'parentOrgName',
     'Name of the parent organisation. Used when parentOrgURI is blank.'),
    ('kv', 'notes',
     'Internal notes. NOT serialised to TTL.'),
    ('blank',),
    ('section', 'MULTIPLE MEMBERSHIPS'),
    ('body',
     'An agent with more than one memberOf affiliation occupies one row per '
     'membership. Repeat agentURI, agentName, agentType, orcidURI, hadRole, '
     'and agentEmail on each row. The TTL generator merges rows sharing the '
     'same agentURI into a single agent block with multiple '
     'schema:memberOf triples.'),
    ('blank',),
    ('section', 'ROLE NAMESPACES'),
    ('kv', 'isoroles: (primary)',
     'http://def.isotc211.org/iso19115-1/2014/'
     'CitationAndResponsiblePartyInformation/code/CI_RoleCode/\n'
     'Example: isoroles:editor'),
    ('kv', 'ISO 19115 cat codelists (alternative)',
     'https://standards.iso.org/iso/19115/resources/Codelist/cat/'
     'codelists.xml#CI_RoleCode\n'
     'Same 20 role codes — use the full codelist URI as the authority '
     'reference. See the Roles sheet for both prefixed forms.'),
    ('blank',),
    ('section', 'NAMESPACE PREFIXES'),
    ('kv', 'schema:',   'https://schema.org/'),
    ('kv', 'prov:',     'http://www.w3.org/ns/prov#'),
    ('kv', 'dcat:',     'http://www.w3.org/ns/dcat#'),
    ('kv', 'isoroles:', 'http://def.isotc211.org/iso19115-1/2014/'
                        'CitationAndResponsiblePartyInformation/code/CI_RoleCode/'),
    ('kv', 'cmns-av:',  'https://www.omg.org/spec/Commons/AnnotationVocabulary/'),
    ('kv', 'xsd:',      'http://www.w3.org/2001/XMLSchema#'),
    ('blank',),
    ('section', 'VERSION'),
    ('kv', 'Template version', '2026-05-10'),
    ('kv', 'Specification',
     'VocPub 4.x / SKOS / PROV-O / schema.org / ISO 19115-3 CIT 1.0–2.0'),
    ('kv', 'Role authority',
     'https://standards.iso.org/iso/19115/resources/Codelist/cat/codelists.xml#CI_RoleCode'),
]

for r_idx, row in enumerate(README_ROWS, start=1):
    rtype = row[0]
    a = row[1] if len(row) > 1 else None
    b = row[2] if len(row) > 2 else None
    rm_row(ws_rm, r_idx, rtype, a, b)

print('README done')

# ════════════════════════════════════════════════════════════════════════════
# SHEET 2 — Agents
# ════════════════════════════════════════════════════════════════════════════
ws_ag = wb.create_sheet('Agents')
ws_ag.sheet_view.showGridLines = False
ws_ag.freeze_panes = 'A3'

# (header label, column width, required, hover comment)
AGENT_COLS = [
    ('agentURI',      40, True,
     '* REQUIRED (or blankNodeLabel) *\n\n'
     'Use a vocab.geospecimens.org/org/ IRI as the subject.\n'
     'Do NOT use an ORCID here — put ORCID in orcidURI.\n'
     'Leave blank to use a blank node.'),
    ('blankNodeLabel', 28, False,
     'Optional\n\n'
     'Blank-node ID without the _: prefix.\n'
     'Required when agentURI is blank.'),
    ('agentName',     28, True,
     '* REQUIRED *\n\nFull display name. Maps to schema:name.'),
    ('agentType',     22, True,
     '* REQUIRED *\n\n'
     'Exactly schema:Person or schema:Organization.\n'
     'Use the dropdown.'),
    ('orcidURI',      38, False,
     'Optional — Persons only\n\n'
     'ORCID IRI (e.g. https://orcid.org/0000-0002-5819-9134).\n'
     'Maps to schema:identifier.'),
    ('hadRole',       44, False,
     'Optional\n\n'
     'ISO 19115 CI_RoleCode role(s), comma-separated.\n'
     'Use isoroles: prefix (e.g. isoroles:editor).\n'
     'See Roles sheet for all valid values.\n'
     'Serialised as prov:qualifiedAssociation on the ConceptScheme.'),
    ('agentEmail',    30, False,
     'Optional — Persons only\n\nEmail. Maps to schema:email.'),
    ('agentURL',      40, False,
     'Optional\n\n'
     'Profile or homepage URL.\n'
     'Maps to schema:url.'),
    ('agentHomepage', 40, False,
     'Optional — Organisations only\n\n'
     'Organisation homepage.\n'
     'Maps to schema:homepage.\n'
     'Often the same value as agentURL.'),
    ('acronym',       14, False,
     'Optional — Organisations only\n\n'
     'Abbreviated name (e.g. TDWG).\n'
     'Maps to cmns-av:acronym.'),
    ('memberOfURI',   52, False,
     'Optional\n\n'
     'URI of the organisation this agent belongs to.\n'
     'Maps to schema:memberOf.\n'
     'One row per membership.'),
    ('memberOfName',  32, False,
     'Optional\n\n'
     'Name of the memberOf organisation.\n'
     'Used when memberOfURI is blank.'),
    ('memberOfRole',  22, False,
     'Optional\n\n'
     "Person's role within the organisation\n"
     '(e.g. employee, co-convener).\n'
     'Maps to schema:roleName.'),
    ('parentOrgURI',  44, False,
     'Optional — Organisations only\n\n'
     'URI of parent organisation.\n'
     'Maps to schema:parentOrganization.'),
    ('parentOrgName', 30, False,
     'Optional\n\n'
     'Name of parent organisation.\n'
     'Used when parentOrgURI is blank.'),
    ('notes',         36, False,
     'Optional\n\nInternal notes. NOT serialised to TTL.'),
]

# Row 1 — title banner
ws_ag.row_dimensions[1].height = 24
ws_ag.merge_cells(
    start_row=1, start_column=1, end_row=1, end_column=len(AGENT_COLS))
tc = ws_ag.cell(row=1, column=1,
    value='Agents — Persons and Organisations for SKOS ConceptScheme TTL Files')
tc.font = Font(name='Calibri', bold=True, size=13, color=C_HEADER_FG)
tc.fill = fill(C_HEADER_BG)
tc.alignment = Alignment(horizontal='left', vertical='center')

# Row 2 — column headers
ws_ag.row_dimensions[2].height = 38
for ci, (hdr, width, req, cmt) in enumerate(AGENT_COLS, start=1):
    cell = ws_ag.cell(row=2, column=ci, value=hdr)
    cell.font = Font(name='Calibri', bold=True, size=10, color=C_HEADER_FG)
    cell.fill = fill(C_HEADER_BG)
    cell.alignment = Alignment(horizontal='center', vertical='center',
                                wrap_text=True)
    cell.border = thin_border()
    cell.comment = Comment(cmt, 'AgentsTemplate')
    set_col(ws_ag, get_column_letter(ci), width)

# ── Agent data ───────────────────────────────────────────────────────────────
# Column order matches AGENT_COLS:
#   agentURI, blankNodeLabel, agentName, agentType, orcidURI,
#   hadRole, agentEmail, agentURL, agentHomepage, acronym,
#   memberOfURI, memberOfName, memberOfRole,
#   parentOrgURI, parentOrgName, notes

AGENT_DATA = [
    # Ben Norton — Yale affiliation
    (
        'https://vocab.geospecimens.org/org/ben-norton',
        '',
        'Ben Norton',
        'schema:Person',
        'https://orcid.org/0000-0002-5819-9134',
        'isoroles:editor, isoroles:publisher',
        'ben.norton@yale.edu',
        '',
        '',
        '',
        ('https://scientific-collections.gbif.org/institution/'
         '75f50140-830d-4630-a290-3d6e951a7c29'),
        'Yale University',
        'employee',
        '',
        '',
        '',
    ),
    # Ben Norton — Mineralogy Extension Task Group affiliation
    (
        'https://vocab.geospecimens.org/org/ben-norton',
        '',
        'Ben Norton',
        'schema:Person',
        'https://orcid.org/0000-0002-5819-9134',
        'isoroles:editor, isoroles:publisher',
        'ben.norton@yale.edu',
        '',
        '',
        '',
        'https://vocab.geospecimens.org/org/minext',
        'Mineralogy Extension Task Group',
        'co-convener',
        '',
        '',
        '',
    ),
    # Mineralogy Extension Task Group
    (
        'https://vocab.geospecimens.org/org/minext',
        'agent_mineralogy_extension_task_group',
        'Mineralogy Extension Task Group',
        'schema:Organization',
        '',
        'isoroles:contributor, isoroles:custodian',
        '',
        'https://www.tdwg.org/community/esp/mineralogy/',
        'https://www.tdwg.org/community/esp/mineralogy/',
        'MinExt',
        'https://vocab.geospecimens.org/org/tdwg',
        'Biodiversity Information Standards',
        '',
        'https://vocab.geospecimens.org/org/tdwg',
        'Biodiversity Information Standards',
        '',
    ),
    # Biodiversity Information Standards (TDWG)
    (
        'https://vocab.geospecimens.org/org/tdwg',
        'agent_biodiversity_information_standards',
        'Biodiversity Information Standards',
        'schema:Organization',
        '',
        '',
        '',
        'https://www.tdwg.org',
        'https://www.tdwg.org',
        'TDWG',
        '',
        '',
        '',
        '',
        '',
        'Taxonomic Databases Working Group, now Biodiversity Information Standards',
    ),
    # Yale University
    (
        'https://vocab.geospecimens.org/org/yale-university',
        'agent_yale_university',
        'Yale University',
        'schema:Organization',
        '',
        '',
        '',
        'https://www.yale.edu',
        'https://www.yale.edu',
        '',
        '',
        '',
        '',
        '',
        '',
        ('Also identified by GBIF GRSciColl IRI: https://scientific-collections'
         '.gbif.org/institution/75f50140-830d-4630-a290-3d6e951a7c29'),
    ),
]

for ri, agent in enumerate(AGENT_DATA, start=3):
    bg = C_ALT_ROW if (ri % 2 == 0) else 'FFFFFF'
    ws_ag.row_dimensions[ri].height = 18
    for ci, val in enumerate(agent, start=1):
        cell = ws_ag.cell(row=ri, column=ci, value=val)
        cell.font = body_font()
        cell.fill = fill(bg)
        cell.alignment = Alignment(horizontal='left', vertical='center',
                                    wrap_text=False)
        cell.border = thin_border()

# Dropdown validation for agentType
dv = DataValidation(
    type='list',
    formula1='"schema:Person,schema:Organization"',
    allow_blank=True,
    showDropDown=False,
    showErrorMessage=True,
    errorTitle='Invalid agentType',
    error='Must be schema:Person or schema:Organization',
)
ws_ag.add_data_validation(dv)
dv.sqref = 'D3:D1000'

print('Agents done')

# ════════════════════════════════════════════════════════════════════════════
# SHEET 3 — Roles
# ════════════════════════════════════════════════════════════════════════════
ws_roles = wb.create_sheet('Roles')
ws_roles.sheet_view.showGridLines = False

# The 20 authoritative CI_RoleCode entries from ISO 19115-3 CIT 1.0 / 2.0
# Source: https://standards.iso.org/iso/19115/-3/cit/1.0/codelists.html
#         https://standards.iso.org/iso/19115/-3/cit/2.0/codelists.html
ISO_ROLES = [
    # (localName, definition)
    ('author',
     'party who authored the resource'),
    ('coAuthor',
     'party who jointly authors the resource'),
    ('collaborator',
     'party who assists with the generation of the resource other than the '
     'principal investigator'),
    ('contributor',
     'party contributing to the resource'),
    ('custodian',
     'party that accepts accountability and responsibility for the resource '
     'and ensures appropriate care and maintenance of the resource'),
    ('distributor',
     'party who distributes the resource'),
    ('editor',
     'party who reviewed or modified the resource to improve the content'),
    ('funder',
     'party providing monetary support for the resource'),
    ('mediator',
     'a class of entity that mediates access to the resource and for whom '
     'the resource is intended or useful'),
    ('originator',
     'party who created the resource'),
    ('owner',
     'party that owns the resource'),
    ('pointOfContact',
     'party who can be contacted for acquiring knowledge about or acquisition '
     'of the resource'),
    ('principalInvestigator',
     'key party responsible for gathering information and conducting research'),
    ('processor',
     'party who has processed the data in a manner such that the resource '
     'has been modified'),
    ('publisher',
     'party who published the resource'),
    ('resourceProvider',
     'party that supplies the resource'),
    ('rightsHolder',
     'party owning or managing rights over the resource'),
    ('sponsor',
     'party who speaks for the resource'),
    ('stakeholder',
     'party who has an interest in the resource or the use of the resource'),
    ('user',
     'party who uses the resource'),
]

ROLE_COLS = [
    ('isoroles: form\n(use in Agents sheet)', 36),
    ('ISO cat codelists form\n(alternative namespace)', 46),
    ('Local name',           22),
    ('Definition (ISO 19115-3 CIT 1.0 / 2.0)', 72),
]

# Title
ws_roles.row_dimensions[1].height = 24
ws_roles.merge_cells(start_row=1, start_column=1, end_row=1,
                     end_column=len(ROLE_COLS))
tc = ws_roles.cell(row=1, column=1,
    value='CI_RoleCode Values — ISO 19115-3 (20 entries, both namespace forms)')
tc.font = Font(name='Calibri', bold=True, size=13, color=C_HEADER_FG)
tc.fill = fill(C_HEADER_BG)
tc.alignment = Alignment(horizontal='left', vertical='center')

# Namespace key
NS_ROWS = [
    # (label, namespace_uri)
    ('isoroles: prefix →',
     'http://def.isotc211.org/iso19115-1/2014/'
     'CitationAndResponsiblePartyInformation/code/CI_RoleCode/'),
    ('ISO cat codelist URI →',
     'https://standards.iso.org/iso/19115/resources/Codelist/cat/'
     'codelists.xml#CI_RoleCode'),
]
for r_off, (label, uri) in enumerate(NS_ROWS, start=2):
    ws_roles.row_dimensions[r_off].height = 14
    ws_roles.merge_cells(start_row=r_off, start_column=1,
                         end_row=r_off, end_column=len(ROLE_COLS))
    c = ws_roles.cell(row=r_off, column=1, value=f'{label}  {uri}')
    c.font = Font(name='Consolas', italic=False, size=9, color='1F4E79')
    c.fill = fill(C_LABEL_BG)
    c.alignment = Alignment(horizontal='left', vertical='center')

# Column headers
ws_roles.row_dimensions[4].height = 36
for ci, (hdr, width) in enumerate(ROLE_COLS, start=1):
    cell = ws_roles.cell(row=4, column=ci, value=hdr)
    cell.font = Font(name='Calibri', bold=True, size=10, color=C_HEADER_FG)
    cell.fill = fill(C_HEADER_BG)
    cell.alignment = Alignment(horizontal='center', vertical='center',
                                wrap_text=True)
    cell.border = thin_border()
    ws_roles.column_dimensions[get_column_letter(ci)].width = width

# Data rows
CAT_BASE = ('https://standards.iso.org/iso/19115/resources/Codelist/'
            'cat/codelists.xml#CI_RoleCode-')

for ri, (local, defn) in enumerate(ISO_ROLES, start=5):
    bg = C_ALT_ROW if (ri % 2 == 1) else 'FFFFFF'
    ws_roles.row_dimensions[ri].height = 16
    row_vals = [
        f'isoroles:{local}',
        f'{CAT_BASE}{local}',
        local,
        defn,
    ]
    for ci, val in enumerate(row_vals, start=1):
        cell = ws_roles.cell(row=ri, column=ci, value=val)
        cell.font = code_font(9) if ci <= 2 else body_font()
        cell.fill = fill(bg)
        cell.alignment = Alignment(horizontal='left', vertical='center')
        cell.border = thin_border()

print('Roles done')

# ════════════════════════════════════════════════════════════════════════════
# SHEET 4 — Mapping
# ════════════════════════════════════════════════════════════════════════════
ws_map = wb.create_sheet('Mapping')
ws_map.sheet_view.showGridLines = False

# (column_name, required, rdf_predicate, namespace, ttl_pattern, notes)
MAPPING_DATA = [
    ('agentURI',
     'Yes*',
     'Subject IRI',
     '(N/A — subject of the triple)',
     '<agentURI>\n    a agentType ;\n    ...',
     'Use a vocab.geospecimens.org/org/ IRI. '
     'If blank, a blank node _:blankNodeLabel is used. '
     '* Required unless blankNodeLabel is provided.'),
    ('blankNodeLabel',
     'Yes*',
     'Blank node identifier',
     '(N/A)',
     '_:blankNodeLabel\n    a agentType ;\n    ...',
     'Required when agentURI is blank. The _: prefix is added automatically.'),
    ('agentName',
     'Yes',
     'schema:name',
     'https://schema.org/',
     'schema:name "Ben Norton" ;',
     'REQUIRED. Full display name.'),
    ('agentType',
     'Yes',
     'rdf:type',
     'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
     'a schema:Person ;\n(or  a schema:Organization ;)',
     'REQUIRED. Exactly one of the two allowed values.'),
    ('orcidURI',
     'No',
     'schema:identifier',
     'https://schema.org/',
     'schema:identifier <https://orcid.org/0000-0002-5819-9134> ;',
     'Persons only. The ORCID is an identifier, not the subject IRI.'),
    ('hadRole',
     'No',
     'prov:hadRole\n(via prov:qualifiedAssociation on ConceptScheme)',
     'http://www.w3.org/ns/prov#',
     '# On the ConceptScheme:\nprov:qualifiedAssociation [\n'
     '    a prov:Association ;\n'
     '    prov:agent <agentURI> ;\n'
     '    prov:hadRole isoroles:editor ;\n'
     '] ;',
     'Comma-separate multiple roles. Added to the ConceptScheme, not the '
     'agent description itself.'),
    ('agentEmail',
     'No',
     'schema:email',
     'https://schema.org/',
     'schema:email "ben.norton@yale.edu" ;',
     'Persons only.'),
    ('agentURL',
     'No',
     'schema:url',
     'https://schema.org/',
     'schema:url "https://www.tdwg.org"^^xsd:anyURI ;',
     'URL of the agent or organisation page.'),
    ('agentHomepage',
     'No',
     'schema:homepage',
     'https://schema.org/',
     'schema:homepage "https://www.tdwg.org"^^xsd:anyURI ;',
     'Organisations only. Often the same value as agentURL.'),
    ('acronym',
     'No',
     'cmns-av:acronym',
     'https://www.omg.org/spec/Commons/AnnotationVocabulary/',
     'cmns-av:acronym "TDWG" ;',
     'Organisations only.'),
    ('memberOfURI',
     'No',
     'schema:memberOf',
     'https://schema.org/',
     'schema:memberOf <https://vocab.geospecimens.org/org/tdwg> ;',
     'One row per membership. Rows sharing an agentURI are merged into one '
     'agent block with multiple schema:memberOf triples.'),
    ('memberOfName',
     'No',
     'schema:name (of the memberOf organisation)',
     'https://schema.org/',
     '# On the memberOf org node:\nschema:name "TDWG" ;',
     'Labels the memberOf organisation when it lacks its own row.'),
    ('memberOfRole',
     'No',
     'schema:roleName',
     'https://schema.org/',
     'schema:roleName "employee" ;',
     "Person's role within the memberOf organisation. Optional."),
    ('parentOrgURI',
     'No',
     'schema:parentOrganization',
     'https://schema.org/',
     'schema:parentOrganization <https://vocab.geospecimens.org/org/tdwg> ;',
     'Organisations only.'),
    ('parentOrgName',
     'No',
     'schema:name (of parent organisation)',
     'https://schema.org/',
     '# On the parent org node:\nschema:name "TDWG" ;',
     'Labels the parent when it lacks its own row.'),
    ('notes',
     'No',
     '(not serialised)',
     '(N/A)',
     '# Internal comment only',
     'NOT included in TTL output.'),
]

MAP_COLS = [
    ('Column Name',   20),
    ('Required?',     10),
    ('RDF Predicate', 38),
    ('Namespace',     46),
    ('TTL Pattern',   60),
    ('Notes',         58),
]

ws_map.row_dimensions[1].height = 24
ws_map.merge_cells(start_row=1, start_column=1, end_row=1,
                   end_column=len(MAP_COLS))
tc = ws_map.cell(row=1, column=1,
    value='Mapping — Agents sheet columns to RDF predicates and TTL serialisation')
tc.font = Font(name='Calibri', bold=True, size=13, color=C_HEADER_FG)
tc.fill = fill(C_HEADER_BG)
tc.alignment = Alignment(horizontal='left', vertical='center')

ws_map.row_dimensions[2].height = 32
for ci, (hdr, width) in enumerate(MAP_COLS, start=1):
    cell = ws_map.cell(row=2, column=ci, value=hdr)
    cell.font = Font(name='Calibri', bold=True, size=10, color=C_HEADER_FG)
    cell.fill = fill(C_HEADER_BG)
    cell.alignment = Alignment(horizontal='center', vertical='center',
                                wrap_text=True)
    cell.border = thin_border()
    ws_map.column_dimensions[get_column_letter(ci)].width = width

for ri, row_data in enumerate(MAPPING_DATA, start=3):
    bg = C_ALT_ROW if (ri % 2 == 1) else 'FFFFFF'
    ws_map.row_dimensions[ri].height = 60
    for ci, val in enumerate(row_data, start=1):
        cell = ws_map.cell(row=ri, column=ci, value=val)
        if ci in (1,):
            cell.font = body_font(bold=True)
            cell.fill = fill(C_LABEL_BG)
        elif ci == 5:
            cell.font = code_font(9)
            cell.fill = fill(C_CODE_BG)
        else:
            cell.font = body_font()
            cell.fill = fill(bg)
        cell.alignment = Alignment(horizontal='left', vertical='top',
                                    wrap_text=True)
        cell.border = thin_border()

print('Mapping done')

# ════════════════════════════════════════════════════════════════════════════
# SHEET 5 — TTL Patterns
# ════════════════════════════════════════════════════════════════════════════
ws_ttl = wb.create_sheet('TTL Patterns')
ws_ttl.sheet_view.showGridLines = False
ws_ttl.column_dimensions['A'].width = 26
ws_ttl.column_dimensions['B'].width = 86


def ttl_section(ws, r, heading):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
    c = ws.cell(row=r, column=1, value=heading)
    c.font = Font(name='Calibri', bold=True, size=11, color='FFFFFF')
    c.fill = fill(C_SECTION_BG)
    c.alignment = Alignment(horizontal='left', vertical='center')
    ws.row_dimensions[r].height = 20
    return r + 1


def ttl_kv(ws, r, label, code):
    cl = ws.cell(row=r, column=1, value=label)
    cl.font = body_font(bold=True)
    cl.fill = fill(C_LABEL_BG)
    cl.alignment = wrap('left', 'top')
    cl.border = thin_border()
    cc = ws.cell(row=r, column=2, value=code)
    cc.font = code_font(9)
    cc.fill = fill(C_CODE_BG)
    cc.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    cc.border = thin_border()
    line_count = code.count('\n') + 1
    ws.row_dimensions[r].height = max(14, line_count * 13)
    return r + 1


def ttl_blank(ws, r):
    ws.row_dimensions[r].height = 6
    return r + 1


# Title
ws_ttl.row_dimensions[1].height = 24
ws_ttl.merge_cells(start_row=1, start_column=1, end_row=1, end_column=2)
tc = ws_ttl.cell(row=1, column=1,
    value='TTL Patterns — Copy-ready Turtle blocks for agents and ConceptScheme attribution')
tc.font = Font(name='Calibri', bold=True, size=13, color=C_HEADER_FG)
tc.fill = fill(C_HEADER_BG)
tc.alignment = Alignment(horizontal='left', vertical='center')

r = 2
r = ttl_blank(ws_ttl, r)

# ── Prefixes ──────────────────────────────────────────────────────────────
r = ttl_section(ws_ttl, r, 'Standard Prefixes')
r = ttl_kv(ws_ttl, r, 'Prefix block',
    '@prefix schema:    <https://schema.org/> .\n'
    '@prefix prov:      <http://www.w3.org/ns/prov#> .\n'
    '@prefix dcat:      <http://www.w3.org/ns/dcat#> .\n'
    '@prefix isoroles:  <http://def.isotc211.org/iso19115-1/2014/'
    'CitationAndResponsiblePartyInformation/code/CI_RoleCode/> .\n'
    '@prefix cmns-av:   <https://www.omg.org/spec/Commons/AnnotationVocabulary/> .\n'
    '@prefix xsd:       <http://www.w3.org/2001/XMLSchema#> .')
r = ttl_blank(ws_ttl, r)

# ── Person ────────────────────────────────────────────────────────────────
r = ttl_section(ws_ttl, r, 'Person (schema:Person)')
r = ttl_kv(ws_ttl, r, 'Notes',
    '- Subject IRI is a vocab.geospecimens.org/org/ URI, not the ORCID.\n'
    '- ORCID is attached as schema:identifier.\n'
    '- Affiliation uses schema:memberOf (not schema:affiliation).\n'
    '- Repeat the block with a different schema:memberOf for each additional affiliation.')
r = ttl_kv(ws_ttl, r, 'Person block',
    '<https://vocab.geospecimens.org/org/ben-norton>\n'
    '    a                    schema:Person ;\n'
    '    schema:name          "Ben Norton" ;\n'
    '    schema:identifier    <https://orcid.org/0000-0002-5819-9134> ;\n'
    '    schema:email         "ben.norton@yale.edu" ;\n'
    '    schema:memberOf      <https://vocab.geospecimens.org/org/yale-university> ,\n'
    '                         <https://vocab.geospecimens.org/org/minext> ;\n'
    '.')
r = ttl_blank(ws_ttl, r)

# ── Organisation ─────────────────────────────────────────────────────────
r = ttl_section(ws_ttl, r, 'Organisation (schema:Organization)')
r = ttl_kv(ws_ttl, r, 'Notes',
    '- Subject IRI is a vocab.geospecimens.org/org/ URI.\n'
    '- Use both schema:url and schema:homepage.\n'
    '- cmns-av:acronym for abbreviated names.\n'
    '- schema:parentOrganization for parent bodies.')
r = ttl_kv(ws_ttl, r, 'Organisation block (named)',
    '<https://vocab.geospecimens.org/org/tdwg>\n'
    '    a                       schema:Organization ;\n'
    '    schema:name             "Biodiversity Information Standards" ;\n'
    '    schema:url              "https://www.tdwg.org"^^xsd:anyURI ;\n'
    '    schema:homepage         "https://www.tdwg.org"^^xsd:anyURI ;\n'
    '    cmns-av:acronym         "TDWG" ;\n'
    '.')
r = ttl_kv(ws_ttl, r, 'Organisation block (with parent)',
    '<https://vocab.geospecimens.org/org/minext>\n'
    '    a                       schema:Organization ;\n'
    '    schema:name             "Mineralogy Extension Task Group" ;\n'
    '    schema:url              "https://www.tdwg.org/community/esp/mineralogy/"^^xsd:anyURI ;\n'
    '    schema:homepage         "https://www.tdwg.org/community/esp/mineralogy/"^^xsd:anyURI ;\n'
    '    cmns-av:acronym         "MinExt" ;\n'
    '    schema:parentOrganization  <https://vocab.geospecimens.org/org/tdwg> ;\n'
    '.')
r = ttl_kv(ws_ttl, r, 'Organisation block (blank node)',
    '_:agent_mineralogy_extension_task_group\n'
    '    a                       schema:Organization ;\n'
    '    schema:name             "Mineralogy Extension Task Group" ;\n'
    '    schema:parentOrganization [\n'
    '        a            schema:Organization ;\n'
    '        schema:name  "Biodiversity Information Standards" ;\n'
    '    ] ;\n'
    '.')
r = ttl_blank(ws_ttl, r)

# ── ConceptScheme attribution ─────────────────────────────────────────────
r = ttl_section(ws_ttl, r, 'ConceptScheme — Role Attribution')
r = ttl_kv(ws_ttl, r, 'Notes',
    '- prov:qualifiedAssociation links an agent to the scheme with a role.\n'
    '- schema:creator / schema:publisher are added as direct predicates.\n'
    '- Both patterns may coexist on the same ConceptScheme.')
r = ttl_kv(ws_ttl, r, 'prov:qualifiedAssociation pattern',
    '<https://vocab.geospecimens.org/def/my-vocab>\n'
    '    a skos:ConceptScheme ;\n'
    '    schema:creator     <https://vocab.geospecimens.org/org/ben-norton> ;\n'
    '    schema:publisher   <https://vocab.geospecimens.org/org/tdwg> ;\n'
    '    prov:qualifiedAssociation [\n'
    '        a            prov:Association ;\n'
    '        prov:agent   <https://vocab.geospecimens.org/org/ben-norton> ;\n'
    '        prov:hadRole isoroles:editor ;\n'
    '    ] ;\n'
    '    prov:qualifiedAssociation [\n'
    '        a            prov:Association ;\n'
    '        prov:agent   <https://vocab.geospecimens.org/org/minext> ;\n'
    '        prov:hadRole isoroles:custodian , isoroles:contributor ;\n'
    '    ] ;\n'
    '.')
r = ttl_kv(ws_ttl, r, 'prov:qualifiedAttribution\n(alternative for entity)',
    '# qualifiedAttribution is the PROV-O predicate for prov:Entity targets.\n'
    '# ConceptScheme is an entity, so both forms are valid; prefer\n'
    '# qualifiedAssociation when following the VocPub pattern above.\n'
    '<https://vocab.geospecimens.org/def/my-vocab>\n'
    '    a skos:ConceptScheme ;\n'
    '    prov:qualifiedAttribution [\n'
    '        a            prov:Attribution ;\n'
    '        prov:agent   <https://orcid.org/0000-0002-5819-9134> ;\n'
    '        dcat:hadRole isoroles:custodian ;\n'
    '    ] ;\n'
    '.')
r = ttl_blank(ws_ttl, r)

# ── Role code forms ───────────────────────────────────────────────────────
r = ttl_section(ws_ttl, r, 'Role Code — Two Namespace Forms')
r = ttl_kv(ws_ttl, r, 'isoroles: (primary)',
    '# @prefix isoroles: <http://def.isotc211.org/iso19115-1/2014/\n'
    '#   CitationAndResponsiblePartyInformation/code/CI_RoleCode/> .\n'
    'prov:hadRole isoroles:editor ;')
r = ttl_kv(ws_ttl, r, 'ISO cat codelists\n(alternative full URI)',
    '# Authority: https://standards.iso.org/iso/19115/resources/Codelist/\n'
    '#            cat/codelists.xml#CI_RoleCode\n'
    'prov:hadRole <https://standards.iso.org/iso/19115/resources/Codelist/\n'
    '             cat/codelists.xml#CI_RoleCode-editor> ;')

print('TTL Patterns done')

# ════════════════════════════════════════════════════════════════════════════
ws_ag.sheet_view.tabSelected = True
wb.active = ws_ag

out_path = 'sources/AgentsTemplate.xlsx'
wb.save(out_path)
print(f'\nSaved: {out_path}')
