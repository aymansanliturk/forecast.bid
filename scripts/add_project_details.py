#!/usr/bin/env python3
"""
add_project_details.py
Adds "Project Details" section to each tool's sidebar by moving the
project-metadata fields out of the canvas editor into the sidebar.
Also fixes TimeCast's double-sidebar by auto-collapsing when chart is generated.
"""

import os, re

WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── sb-field helper ──────────────────────────────────────────────────────────
def sf(label, input_html):
    return f'        <div class="sb-field"><label>{label}</label>{input_html}</div>'

def sf_input(label, id_, placeholder='', oninput='', type_='text', value=''):
    val = f' value="{value}"' if value else ''
    oi  = f' oninput="{oninput}"' if oninput else ''
    ph  = f' placeholder="{placeholder}"' if placeholder else ''
    return sf(label, f'<input type="{type_}" id="{id_}"{val}{ph}{oi}>')

def sf_date(label, id_, oninput=''):
    oi = f' oninput="{oninput}"' if oninput else ''
    return sf(label, f'<input type="date" id="{id_}"{oi}>')

def sf_select(label, id_, options_html, onchange=''):
    oc = f' onchange="{onchange}"' if onchange else ''
    return sf(label, f'<select id="{id_}"{oc}>{options_html}</select>')

def proj_details_section(fields_html):
    return f'''\
      <div class="sb-section">
        <div class="sb-hd">Project Details</div>
{fields_html}
      </div>'''


# ─────────────────────────────────────────────────────────────────────────────
# Per-tool: sidebar project fields HTML + canvas strings to remove
# ─────────────────────────────────────────────────────────────────────────────

TOOLS = {}

# ── TimeCast ─────────────────────────────────────────────────────────────────
TOOLS['timecast'] = {
    'proj_fields': '\n'.join([
        sf_input('Chart Title',  'proj-title',  'Auto-synced with project name',
                 oninput='_scheduleSnap(); syncTitleFromProject()'),
        sf_input('Project No.',  'proj-num',    'e.g. PRJ-001',
                 oninput="_scheduleSnap(); SuiteManager.write({projNum:this.value.trim()},'timecast')"),
        sf_input('Date',         'proj-date',   'e.g. 2025-06-01',
                 oninput='_scheduleSnap()'),
        sf_select('View Scale', 'view-scale',
                  '<option value="monthly">Monthly</option><option value="weekly">Weekly</option><option value="quarterly">Quarterly</option>',
                  onchange='generate()'),
    ]),
    # Strings to strip from editor (the old chart-info section)
    'canvas_remove': [
        # The chart title + proj-num + proj-date fields block
        (r'<div class="section-title">Chart Information</div>\s*<div[^>]*>', None),  # handled with find_section
    ],
    'use_find_section': 'Chart Information',   # strip whole section matching this title
    # TimeCast: auto-collapse app sidebar when chart is generated
    'generate_collapse': True,
}

# ── ResourceCast ──────────────────────────────────────────────────────────────
TOOLS['resourcecast'] = {
    'proj_fields': '\n'.join([
        sf_input('Project Name', 'proj-name',   'e.g. Offshore Substation',
                 oninput="_scheduleSnap(); const _v=this.value.trim(); if(_v) SuiteManager.write({projectName:_v},'resourcecast')"),
        sf_input('Project No.',  'proj-num',    'e.g. PRJ-001',
                 oninput="_scheduleSnap(); SuiteManager.write({projNum:this.value.trim()},'resourcecast')"),
        sf_date( 'Start Date',   'proj-date',   oninput='_scheduleSnap(); rebuildMonthlyGrid()'),
    ]),
    'use_find_section': 'Project Information',
}

# ── OrgCast ───────────────────────────────────────────────────────────────────
TOOLS['orgcast'] = {
    'proj_fields': '\n'.join([
        sf_input('Chart Title',  'chart-title', 'Project Organisation Chart',
                 value='Project Organisation Chart',
                 oninput='_scheduleSnap()'),
        sf_input('Project No.',  'proj-num',    'e.g. PRJ-001',
                 oninput="_scheduleSnap(); SuiteManager.write({projNum:this.value.trim()},'orgcast')"),
        sf_input('Revision',     'chart-rev',   value='Rev. 1.0',
                 oninput='_scheduleSnap()'),
        sf_date( 'Date',         'chart-date',  oninput='_scheduleSnap()'),
        sf_select('Format', 'format-select',
                  '<option value="a4-landscape">A4 Landscape</option><option value="a4-portrait">A4 Portrait</option><option value="a3-landscape">A3 Landscape</option>',
                  onchange='changeFormat()'),
    ]),
    'use_find_section': 'Chart info',
}

# ── RFQCast ───────────────────────────────────────────────────────────────────
TOOLS['rfqcast'] = {
    'proj_fields': '\n'.join([
        sf_input('Project Name', 'proj-name',   'e.g. Alpha 132kV Substation',
                 oninput="const _v=this.value.trim();if(_v&&_v!=='Project Name')SuiteManager.write({projectName:_v},'rfqcast')"),
        sf_input('Project No.',  'proj-num',    'e.g. PRJ-001',
                 oninput="_scheduleSnap(); SuiteManager.write({projNum:this.value.trim()},'rfqcast')"),
    ]),
    'use_find_section': 'Project Information',
}

# ── DORCast ───────────────────────────────────────────────────────────────────
TOOLS['dorcast'] = {
    'proj_fields': '\n'.join([
        sf_input('Document Title', 'doc-title', value='Division of Responsibilities',
                 oninput='_scheduleSnap()'),
        sf_input('Project No.',    'proj-num',  'e.g. PRJ-001',
                 oninput="_scheduleSnap(); SuiteManager.write({projNum:this.value.trim()},'dorcast')"),
        sf_input('Revision',       'doc-rev',   value='Rev. 0',
                 oninput='_scheduleSnap()'),
        sf_date( 'Date',           'doc-date',  oninput='_scheduleSnap()'),
    ]),
    'use_find_section': 'Document Information',
}

# ── RiskCast ──────────────────────────────────────────────────────────────────
TOOLS['riskcast'] = {
    'proj_fields': '\n'.join([
        sf_input('Document Title', 'doc-title', value='Risk Register',
                 oninput='_scheduleSnap()'),
        sf_input('Project No.',    'proj-num',  'e.g. PRJ-001',
                 oninput="_scheduleSnap(); SuiteManager.write({projNum:this.value.trim()},'riskcast')"),
        sf_input('Revision',       'doc-rev',   value='Rev. 0',
                 oninput='_scheduleSnap()'),
        sf_date( 'Date',           'doc-date',  oninput='_scheduleSnap()'),
    ]),
    'use_find_section': 'Document Information',
}

# ── CalcCast ──────────────────────────────────────────────────────────────────
TOOLS['calccast'] = {
    'proj_fields': '\n'.join([
        sf_input('Project Name', 'proj-name',  'e.g. Hornsea 4 HVDC Link',
                 oninput="_scheduleSnap(); const _v=this.value.trim(); if(_v) SuiteManager.write({projectName:_v},'calccast')"),
        sf_input('LOA / Bid ID', 'loa-id',     'e.g. LOA-2025-0042',
                 oninput='_scheduleSnap()'),
        sf_input('Project Type', 'proj-type',  'e.g. Offshore Substation',
                 oninput='_scheduleSnap()'),
    ]),
    'use_find_section': 'Global Parameters',
    'section_fields_only': True,  # only remove the proj-name/loa-id/proj-type fields, not the whole section
}

# ── LetterCast ────────────────────────────────────────────────────────────────
TOOLS['lettercast'] = {
    'proj_fields': '\n'.join([
        sf_input('Project Name', 'proj-name',    'e.g. UK Substation Package 2025',
                 oninput='onProjName()'),
        sf_input('Reference',    'doc-ref',      'e.g. Rev.A · OFR-2025-001',
                 oninput='_scheduleSnap()'),
        sf_date( 'Date',         'letter-date',  oninput='_scheduleSnap()'),
    ]),
    'use_find_section': 'Document Info',
    'section_fields_only': True,
}

# ── CVCast ────────────────────────────────────────────────────────────────────
TOOLS['cvcast'] = {
    'proj_fields': '\n'.join([
        sf_input('Full Name',    'cv-name',      'e.g. Ayman Şanlıtürk',
                 oninput='autoSave()'),
        sf_input('Job Title',    'cv-jobtitle',  'e.g. Senior Bid Manager',
                 oninput='autoSave()'),
        sf_input('Location',     'cv-location',  'e.g. Copenhagen, Denmark',
                 oninput='autoSave()'),
    ]),
    'use_find_section': 'Personal Info',
    'section_fields_only': True,
}

# ── ForeCast ──────────────────────────────────────────────────────────────────
TOOLS['forecast'] = {
    'proj_fields': '\n'.join([
        sf_input('Pipeline Name', 'proj-name', 'e.g. 2025 EMEA Pipeline',
                 oninput='_scheduleSnap()'),
    ]),
    'use_find_section': None,
    'canvas_remove_exact': [
        # The meta-row with proj-name
        r'<div class="meta-row">\s*<label>Pipeline Name</label>\s*<input[^>]+id="proj-name"[^>]*>\s*</div>',
    ],
}

# ── ActionLog ─────────────────────────────────────────────────────────────────
TOOLS['actionlog'] = {
    'proj_fields': '\n'.join([
        sf_input('Project Name', 'proj-name', 'Project name',
                 oninput='_scheduleSnap();_suiteWrite()'),
    ]),
    'use_find_section': None,
    'canvas_remove_exact': [
        r'<div class="proj-bar">\s*<label>Project</label>\s*<input[^>]+id="proj-name"[^>]*>\s*</div>',
    ],
}

# ── BidPack ───────────────────────────────────────────────────────────────────
TOOLS['bidpack'] = {
    'proj_fields': '\n'.join([
        sf_input('Project Name',  'proj-name',     'e.g. Offshore Wind Farm EPC',
                 oninput='_scheduleSnap()'),
        sf_input('Customer',      'customer',      'e.g. Acme Energy Ltd',
                 oninput='_scheduleSnap()'),
        sf_input('Prepared By',   'prepared-by',   'Name or Department',
                 oninput='_scheduleSnap()'),
    ]),
    'use_find_section': 'Document Details',
    'section_fields_only': True,
}

# CashFlow and W2W-Report: no project fields to move (they read from CalcCast)

# ─────────────────────────────────────────────────────────────────────────────
# HTML manipulation helpers
# ─────────────────────────────────────────────────────────────────────────────

def find_div_end(html, start):
    depth, i = 0, start
    while i < len(html):
        if html[i:i+4].lower() == '<div':
            depth += 1; i += 4
        elif html[i:i+6].lower() == '</div>':
            depth -= 1; i += 6
            if depth == 0: return i
        else:
            i += 1
    raise ValueError(f"Unmatched <div> at {start}")


def strip_section_by_title(html, title_text):
    """Remove a <div class="section"> that contains the given section title."""
    # Find the section containing this title
    # Titles appear as: section-title, section-hd > section-title, or similar
    escaped = re.escape(title_text)
    m = re.search(
        r'<div[^>]+class="[^"]*section[^"]*"[^>]*>(?:(?!<div).|\n)*?' + escaped,
        html
    )
    if not m:
        return html, False
    # Walk back to find the opening <div class="section..."> that contains this match
    # The match start might be inside a nested div; find the outermost section div before it
    before = html[:m.start()]
    # Find last <div class="section..." before match
    sec_opens = list(re.finditer(r'<div[^>]+class="[^"]*section[^"]*"', before))
    if not sec_opens:
        return html, False
    sec_open = sec_opens[-1]
    sec_start = sec_open.start()
    sec_end   = find_div_end(html, sec_start)
    return html[:sec_start] + html[sec_end:], True


def strip_specific_fields(html, field_ids):
    """Remove <label> blocks that contain specific input IDs from the editor."""
    for fid in field_ids:
        # Match <label>...<input ...id="fid"...>...</label>
        pattern = r'<label[^>]*>(?:(?!</?label).)*?id="' + re.escape(fid) + r'"(?:(?!</?label).)*?</label>'
        html = re.sub(pattern, '', html, flags=re.DOTALL)
        # Also try <div class="...field...">...<input id="fid"...>...</div>
        # by finding the input and removing its wrapping field div
        m = re.search(r'<input[^>]+id="' + re.escape(fid) + r'"', html)
        if m:
            # Walk back to find wrapping <div class="*field*"> or <div class="meta-field">
            before = html[:m.start()]
            divs = list(re.finditer(r'<div[^>]+class="[^"]*(?:field|meta)[^"]*"', before))
            if divs:
                d = divs[-1]
                d_end = find_div_end(html, d.start())
                html = html[:d.start()] + html[d_end:]
    return html


def inject_proj_section_in_sidebar(html, proj_section_html):
    """Insert the project details section before the Actions section in the sidebar."""
    # Find the sidebar Actions section
    actions_marker = '<div class="sb-hd">Actions</div>'
    pos = html.find(actions_marker)
    if pos == -1:
        return html
    # Walk back to find the opening <div class="sb-section"> for Actions
    before = html[:pos]
    sec_open = before.rfind('<div class="sb-section">')
    if sec_open == -1:
        return html
    return html[:sec_open] + proj_section_html + '\n' + html[sec_open:]


def add_generate_collapse(html):
    """In TimeCast: auto-collapse app sidebar when generate() is called,
    restore when goBack() is called."""
    # Find generate() function and inject collapse before its closing brace
    # We look for the renderChart call (which is always at the end of generate logic)
    # Actually we'll inject right after the generate() function opens the output view
    # TimeCast's generate() ends by hiding editor and showing output
    inject_gen = "\n  document.getElementById('sidebar').classList.add('collapsed');"
    inject_back = "\n  document.getElementById('sidebar').classList.remove('collapsed');"

    # After "editor.style.display = 'none'" in generate()
    html = html.replace(
        "editor.style.display = 'none'",
        "editor.style.display = 'none'" + inject_gen,
        1  # only first occurrence
    )
    # In goBack(), before or after editor is shown again
    # TimeCast's goBack typically does: output.style.display='none'; editor.style.display='block'
    html = re.sub(
        r"(function goBack\(\)\s*\{)",
        r"\1" + inject_back,
        html, count=1
    )
    return html


def also_hide_reorder_sidebar_css(html):
    """When app sidebar is shown, the reorder-sidebar still needs its own space.
    Ensure .reorder-sidebar has a fixed width and doesn't compete.
    We override its width to be more compact."""
    # The reorder sidebar in TimeCast is inside the Gantt output.
    # We just ensure it has correct overflow/width behavior.
    # Nothing to do here — the reorder sidebar has its own styling.
    return html


# ─────────────────────────────────────────────────────────────────────────────
# Main transformation
# ─────────────────────────────────────────────────────────────────────────────

def transform(slug, config, html):
    proj_fields_html = config.get('proj_fields', '')
    if not proj_fields_html:
        return html

    proj_section = proj_details_section(proj_fields_html)

    # 1. Remove project fields from canvas editor FIRST (before injecting into
    #    sidebar — otherwise strip_specific_fields finds the sidebar copy first)
    use_section = config.get('use_find_section')
    section_fields_only = config.get('section_fields_only', False)

    if use_section and not section_fields_only:
        html, found = strip_section_by_title(html, use_section)
        if not found:
            print(f"  WARNING: section '{use_section}' not found in {slug}.html")
    elif use_section and section_fields_only:
        field_ids = re.findall(r'\bid="([^"]+)"', proj_fields_html)
        html = strip_specific_fields(html, field_ids)

    for pattern in config.get('canvas_remove_exact', []):
        html = re.sub(pattern, '', html, flags=re.DOTALL)

    # 2. Now inject project details section into sidebar (IDs are now unique)
    html = inject_proj_section_in_sidebar(html, proj_section)

    # 3. TimeCast special: auto-collapse sidebar on generate
    if config.get('generate_collapse'):
        html = add_generate_collapse(html)

    return html


def main():
    for slug, config in TOOLS.items():
        fname = f"{slug}.html"
        fpath = os.path.join(WORK_DIR, fname)
        if not os.path.exists(fpath):
            print(f"SKIP: {fname} not found")
            continue
        print(f"Processing {fname}...")
        with open(fpath, 'r', encoding='utf-8') as f:
            html = f.read()
        html = transform(slug, config, html)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  OK")

    print("\nDone.")

if __name__ == '__main__':
    main()
