#!/usr/bin/env python3
"""
apply_nav_shell.py
Applies the BidScore-style app shell (header + collapsible sidebar + canvas
+ tool-switcher nav popover) to the remaining 14 PYL0N suite tools.
"""

import os, re

WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────────────────────────
# Shared CSS injected at end of each tool's <style> block
# ─────────────────────────────────────────────────────────────────────────────
SHELL_CSS = """
    /* ═══════════════ PYL0N NAV SHELL (auto-applied) ═══════════════ */
    :root { --navy:#1e3a6b; --sidebar-w:272px; }
    body { height:100vh!important; overflow:hidden!important; display:flex!important; flex-direction:column!important; }

    header {
      height:48px; flex-shrink:0;
      display:flex; align-items:center; justify-content:space-between;
      padding:0 20px; gap:12px;
      background:var(--surface); border-bottom:1px solid var(--border);
      position:relative; z-index:200;
    }
    [data-theme="dark"] header { background:rgba(28,28,26,0.97); }
    .hdr-left  { display:flex; align-items:center; gap:10px; min-width:0; }
    .hdr-right { display:flex; align-items:center; gap:4px; flex-shrink:0; }

    .hdr-logo {
      display:flex; align-items:center; justify-content:center;
      width:28px; height:28px; background:var(--navy); border-radius:7px;
      flex-shrink:0; text-decoration:none; transition:opacity 0.15s;
    }
    .hdr-logo:hover { opacity:0.8; }
    .hdr-logo svg { width:14px; height:14px; }

    .hdr-div { width:1px; height:18px; background:var(--border); flex-shrink:0; }

    .breadcrumb { display:flex; align-items:center; gap:5px; min-width:0; }
    .bc-btn {
      background:none; border:none; padding:0; cursor:pointer;
      font-size:13px; color:var(--muted); font-family:inherit;
      transition:color 0.15s; display:flex; align-items:center; gap:4px;
    }
    .bc-btn:hover { color:var(--text); }
    .bc-btn .bc-caret { font-size:9px; opacity:0.6; transition:transform 0.15s; }
    .bc-btn.open .bc-caret { transform:rotate(180deg); }
    .bc-sep { font-size:11px; color:var(--faint); flex-shrink:0; }
    .bc-current { font-size:13px; font-weight:700; color:var(--text); white-space:nowrap; }

    .hdr-icon-btn {
      width:30px; height:30px; border-radius:6px; border:none;
      background:transparent; color:var(--muted); cursor:pointer;
      display:flex; align-items:center; justify-content:center;
      transition:background 0.15s, color 0.15s; flex-shrink:0;
    }
    .hdr-icon-btn:hover { background:var(--bg); color:var(--text); }
    .hdr-icon-btn svg { width:15px; height:15px; pointer-events:none; }

    /* ── App body ── */
    .app-body { display:flex; flex:1; overflow:hidden; }

    /* ── Sidebar ── */
    .sidebar {
      width:var(--sidebar-w); flex-shrink:0;
      background:var(--surface); border-right:1px solid var(--border);
      display:flex; flex-direction:column; overflow:hidden;
      transition:width 0.22s ease;
    }
    .sidebar.collapsed { width:0; }
    .sidebar-inner { width:var(--sidebar-w); overflow-y:auto; flex:1; display:flex; flex-direction:column; }

    .sb-section { padding:18px 16px; border-bottom:1px solid var(--border); }
    .sb-section:last-child { border-bottom:none; }
    .sb-hd {
      font-size:9px; font-weight:700; letter-spacing:1.2px;
      text-transform:uppercase; color:var(--faint); margin-bottom:12px;
    }
    .sb-actions-grid { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
    .sb-btn {
      font-family:'DM Sans',sans-serif; font-size:11px; font-weight:500;
      padding:7px 10px; border-radius:7px; border:1.5px solid var(--border);
      background:var(--bg); color:var(--muted); cursor:pointer;
      white-space:nowrap; transition:all 0.15s; text-align:center;
      display:flex; align-items:center; justify-content:center; gap:4px;
    }
    .sb-btn:hover { border-color:var(--accent); color:var(--accent); background:var(--surface); }
    .sb-btn:disabled { opacity:0.35; pointer-events:none; }
    .sb-btn.full  { grid-column:1/-1; }
    .sb-btn.primary { background:var(--accent); color:#fff; border-color:var(--accent); font-weight:600; }
    .sb-btn.primary:hover { opacity:0.88; }
    .sb-btn.green { background:var(--green); color:#fff; border-color:var(--green); font-weight:600; }
    .sb-btn.green:hover { opacity:0.88; }
    .sb-btn.accent { background:none; color:var(--accent); border-color:var(--accent); font-weight:600; }
    .sb-btn.accent:hover { background:var(--accent); color:#fff; }

    /* ── Canvas ── */
    .canvas { flex:1; min-width:0; display:flex; flex-direction:column; overflow:hidden; }
    .canvas-body { flex:1; overflow-y:auto; }

    /* ── Nav popover ── */
    .nav-popover {
      position:fixed; top:49px; left:0; width:492px;
      background:var(--surface); border:1px solid var(--border);
      border-top:none; border-radius:0 0 14px 14px;
      box-shadow:0 12px 36px rgba(0,0,0,0.13);
      z-index:400; padding:14px;
      animation:navPopIn 0.16s ease;
    }
    @keyframes navPopIn {
      from { opacity:0; transform:translateY(-8px); }
      to   { opacity:1; transform:translateY(0); }
    }
    .nav-pop-hd {
      display:flex; align-items:center; justify-content:space-between;
      padding-bottom:10px; margin-bottom:10px; border-bottom:1px solid var(--border);
    }
    .nav-pop-title { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.1px; color:var(--faint); }
    .nav-pop-dash  { font-size:12px; font-weight:600; color:var(--accent); text-decoration:none; }
    .nav-pop-dash:hover { text-decoration:underline; }
    .nav-pop-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:3px; }
    .nav-tool-card {
      display:flex; align-items:center; gap:9px;
      padding:8px 9px; border-radius:8px;
      text-decoration:none; color:var(--text); transition:background 0.12s;
    }
    .nav-tool-card:hover { background:var(--bg); }
    .nav-tool-card.ntc-active { background:var(--bg); outline:1.5px solid var(--border); }
    .ntc-icon {
      width:28px; height:28px; border-radius:7px; flex-shrink:0;
      display:flex; align-items:center; justify-content:center;
      font-size:10px; font-weight:700; color:#fff; letter-spacing:-0.3px;
      font-family:'DM Mono',monospace;
    }
    .ntc-info { min-width:0; }
    .ntc-name { font-size:12px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .ntc-tag  { font-size:10px; color:var(--muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:1px; }

    /* ── Hide old toolbar chrome ── */
    .kb-hint, #autosave-label, .save-confirm { display:none !important; }
    #toolbar { display:none !important; }

    /* ── Print ── */
    @media print {
      header, .sidebar, .nav-popover { display:none !important; }
      body { height:auto!important; overflow:visible!important; display:block!important; }
      .app-body, .canvas, .canvas-body { display:block!important; overflow:visible!important; height:auto!important; }
    }
"""

# ─────────────────────────────────────────────────────────────────────────────
# Shared JS injected before last </script> in each tool
# ─────────────────────────────────────────────────────────────────────────────
SHELL_JS = """
/* ══ Tool nav popover ════════════════════════════════════════════════ */
const SUITE_TOOLS = [
  { name:'TimeCast',    file:'timecast.html',    color:'#2c4e87', abbr:'TC', tag:'Gantt timeline'    },
  { name:'ResourceCast',file:'resourcecast.html',color:'#0891b2', abbr:'RC', tag:'Resource planning' },
  { name:'OrgCast',     file:'orgcast.html',     color:'#7c3aed', abbr:'OC', tag:'Org chart'          },
  { name:'RFQCast',     file:'rfqcast.html',     color:'#d97706', abbr:'RQ', tag:'Supplier quotes'    },
  { name:'DORCast',     file:'dorcast.html',     color:'#059669', abbr:'DC', tag:'RACI matrix'        },
  { name:'RiskCast',    file:'riskcast.html',    color:'#dc2626', abbr:'RK', tag:'Risk register'      },
  { name:'CalcCast',    file:'calccast.html',    color:'#0369a1', abbr:'CC', tag:'Cost calculator'    },
  { name:'LetterCast',  file:'lettercast.html',  color:'#6366f1', abbr:'LC', tag:'Cover letters'      },
  { name:'CashFlow',    file:'cashflow.html',    color:'#0ea5e9', abbr:'CF', tag:'Cash flow'          },
  { name:'W2W Report',  file:'w2w-report.html',  color:'#10b981', abbr:'W2', tag:'Financial report'   },
  { name:'CVCast',      file:'cvcast.html',      color:'#b45309', abbr:'CV', tag:'CV builder'         },
  { name:'ForeCast',    file:'forecast.html',    color:'#8b5cf6', abbr:'FC', tag:'Pipeline monitor'   },
  { name:'BidScore',    file:'bidscore.html',    color:'#1e3a6b', abbr:'BS', tag:'Bid/No-Bid scoring' },
  { name:'ActionLog',   file:'actionlog.html',   color:'#ef4444', abbr:'AL', tag:'Action tracker'     },
  { name:'BidPack',     file:'bidpack.html',     color:'#334155', abbr:'BP', tag:'Bid assembler'      },
];
let _navOpen = false;
function _buildNavPopover() {
  const grid = document.getElementById('nav-pop-grid');
  if (!grid || grid.children.length) return;
  const current = location.pathname.split('/').pop() || 'index.html';
  grid.innerHTML = SUITE_TOOLS.map(t => {
    const active = t.file === current ? ' ntc-active' : '';
    return `<a class="nav-tool-card${active}" href="${t.file}">
      <div class="ntc-icon" style="background:${t.color}">${t.abbr}</div>
      <div class="ntc-info"><div class="ntc-name">${t.name}</div><div class="ntc-tag">${t.tag}</div></div>
    </a>`;
  }).join('');
}
function toggleNavPopover(e) { e && e.stopPropagation(); _navOpen ? closeNavPopover() : openNavPopover(); }
function openNavPopover() {
  _buildNavPopover();
  document.getElementById('nav-popover').style.display = 'block';
  document.getElementById('dashboard-btn').classList.add('open');
  _navOpen = true;
}
function closeNavPopover() {
  document.getElementById('nav-popover').style.display = 'none';
  document.getElementById('dashboard-btn').classList.remove('open');
  _navOpen = false;
}
function toggleSidebar() {
  const sb  = document.getElementById('sidebar');
  const btn = document.getElementById('sidebar-toggle-btn');
  const collapsed = sb.classList.toggle('collapsed');
  btn.style.opacity = collapsed ? '0.45' : '1';
}
"""

HEADER_HTML = """\
<header>
  <div class="hdr-left">
    <a class="hdr-logo" href="index.html" title="Dashboard">
      <svg viewBox="0 0 18 18" fill="none">
        <rect x="1" y="1" width="7" height="7" rx="1.5" fill="white"/>
        <rect x="10" y="1" width="7" height="7" rx="1.5" fill="white"/>
        <rect x="1" y="10" width="7" height="7" rx="1.5" fill="white"/>
        <rect x="10" y="10" width="7" height="7" rx="1.5" fill="white" opacity="0.4"/>
      </svg>
    </a>
    <div class="hdr-div"></div>
    <nav class="breadcrumb">
      <button class="bc-btn" id="dashboard-btn" onclick="toggleNavPopover(event)">Dashboard <span class="bc-caret">▾</span></button>
      <span class="bc-sep">›</span>
      <span class="bc-current">{tool_name}</span>
    </nav>
  </div>
  <div class="hdr-right">
    <button class="hdr-icon-btn" id="sidebar-toggle-btn" onclick="toggleSidebar()" title="Toggle sidebar">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <line x1="9" y1="3" x2="9" y2="21"/>
      </svg>
    </button>
    <button class="hdr-icon-btn" id="{theme_id}" onclick="toggleTheme()" title="Toggle dark mode" style="font-size:15px;">🌙</button>
  </div>
</header>"""

NAV_POPOVER_HTML = """\
<!-- ── Tool nav popover ── -->
<div id="nav-popover" class="nav-popover" style="display:none" onclick="event.stopPropagation()">
  <div class="nav-pop-hd">
    <span class="nav-pop-title">All Tools</span>
    <a href="index.html" class="nav-pop-dash">Dashboard →</a>
  </div>
  <div class="nav-pop-grid" id="nav-pop-grid"></div>
</div>"""

def sidebar_html(actions_inner):
    return f"""\
<aside class="sidebar" id="sidebar">
  <div class="sidebar-inner">
    <div class="sb-section">
      <div class="sb-hd">Actions</div>
      <div class="sb-actions-grid">
{actions_inner}
      </div>
    </div>
  </div>
</aside>"""

# ─────────────────────────────────────────────────────────────────────────────
# Per-tool configuration
# ─────────────────────────────────────────────────────────────────────────────
UNDO_REDO = """\
        <button class="sb-btn" id="btn-undo" onclick="undo()" disabled>↩ Undo</button>
        <button class="sb-btn" id="btn-redo" onclick="redo()" disabled>↪ Redo</button>"""

SAVE_LOAD = """\
        <button class="sb-btn" onclick="saveJSON()">💾 Save</button>
        <label class="sb-btn" style="cursor:pointer;">↑ Load<input type="file" accept=".json" style="display:none" onchange="loadJSON(this)"></label>"""

BACKUPS = """\
        <button class="sb-btn full" id="backup-btn" onclick="_showBackups()">⏱ Backups</button>"""

TOOLS = {
    'timecast': {
        'name': 'TimeCast',
        'theme_id': 'theme-btn',
        'canvas_selector': '#editor',   # what to wrap in canvas
        'extra_before_canvas': ['#screen-hint'],  # elements to include before canvas-body
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <button class="sb-btn" onclick="exportHTML()">HTML</button>
        <button class="sb-btn full" id="backup-btn" onclick="_showBackups()">⏱ Backups</button>
        <button class="sb-btn full primary" onclick="generate()">Generate Chart ›</button>""",
    },
    'resourcecast': {
        'name': 'ResourceCast',
        'theme_id': 'theme-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <button class="sb-btn" onclick="exportHTML()">HTML</button>
        <button class="sb-btn full" id="backup-btn" onclick="_showBackups()">⏱ Backups</button>
        <button class="sb-btn full primary" onclick="generate()">Generate Report ›</button>""",
    },
    'orgcast': {
        'name': 'OrgCast',
        'theme_id': 'theme-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <button class="sb-btn" onclick="exportExcel()">Excel</button>
        <button class="sb-btn" onclick="exportHTML()">HTML</button>
        <button class="sb-btn" onclick="exportPNG()">PNG</button>
        <button class="sb-btn full" id="backup-btn" onclick="_showBackups()">⏱ Backups</button>
        <button class="sb-btn full primary" onclick="generate()">Generate Chart ›</button>""",
    },
    'rfqcast': {
        'name': 'RFQCast',
        'theme_id': 'theme-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <label class="sb-btn full" style="cursor:pointer;">↑ Import Excel<input type="file" accept=".xlsx,.xls" style="display:none" onchange="importExcel(this)"></label>
        <button class="sb-btn" onclick="exportExcel()">Excel</button>
        <button class="sb-btn" onclick="exportHTML()">HTML</button>
        <button class="sb-btn full" id="backup-btn" onclick="_showBackups()">⏱ Backups</button>
        <button class="sb-btn full primary" onclick="generate()">Generate Report ›</button>""",
    },
    'dorcast': {
        'name': 'DORCast',
        'theme_id': 'theme-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <button class="sb-btn full accent" onclick="openModal()">⬇ Load Template</button>
        <label class="sb-btn full" style="cursor:pointer;">↑ Import Excel<input type="file" accept=".xlsx,.xls" style="display:none" onchange="importExcel(this)"></label>
        <button class="sb-btn" onclick="exportExcel()">Excel</button>
        <button class="sb-btn" onclick="exportHTML()">HTML</button>
        <button class="sb-btn full" id="backup-btn" onclick="_showBackups()">⏱ Backups</button>
        <button class="sb-btn full primary" onclick="generate()">Generate Matrix ›</button>""",
    },
    'riskcast': {
        'name': 'RiskCast',
        'theme_id': 'theme-toggle-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <button class="sb-btn" onclick="exportExcel()">Excel</button>
        <button class="sb-btn" onclick="exportPDF()">PDF</button>
        <button class="sb-btn full" id="backup-btn" onclick="_showBackups()">⏱ Backups</button>
        <button class="sb-btn full primary" onclick="generate()">Generate Register ›</button>""",
    },
    'calccast': {
        'name': 'CalcCast',
        'theme_id': 'theme-toggle-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <button class="sb-btn accent" onclick="SuiteManager.setReturnPath('calccast.html','CalcCast');location.href='w2w-report.html'">W2W</button>
        <button class="sb-btn accent" onclick="SuiteManager.setReturnPath('calccast.html','CalcCast');location.href='cashflow.html'">CashFlow</button>
        <button class="sb-btn" onclick="exportExcel()">Excel</button>
        <button class="sb-btn" onclick="exportHTML()">HTML</button>
        <button class="sb-btn" onclick="exportPDF()">PDF</button>
        <button class="sb-btn full" id="backup-btn" onclick="_showBackups()">⏱ Backups</button>
        <button class="sb-btn full primary" onclick="generate()">Generate Report ›</button>""",
    },
    'lettercast': {
        'name': 'LetterCast',
        'theme_id': 'theme-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <button class="sb-btn full" id="backup-btn" onclick="_showBackups()">⏱ Backups</button>
        <button class="sb-btn full green" onclick="exportPDF()">⬇ Export PDF</button>
        <button class="sb-btn full primary" onclick="generate()">Preview Letter ›</button>""",
    },
    'cashflow': {
        'name': 'CashFlow',
        'theme_id': 'theme-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <button class="sb-btn full accent" onclick="loadSuiteData(); simulate();">↺ Refresh Data</button>""",
    },
    'w2w-report': {
        'name': 'W2W Report',
        'theme_id': 'theme-toggle-btn',
        'canvas_selector': '#tab-nav',   # special: wrap tab-nav + main-content
        'canvas_end_selector': '#main-content',  # wrap up to and including this
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + """
        <button class="sb-btn" onclick="saveJSON()">💾 Save</button>
        <button class="sb-btn" onclick="loadJSONFile()">↑ Load</button>
        <button class="sb-btn full accent" onclick="refreshAll()">↺ Refresh from CalcCast</button>""",
    },
    'cvcast': {
        'name': 'CVCast',
        'theme_id': 'theme-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <button class="sb-btn" onclick="exportHTML()">HTML</button>
        <button class="sb-btn full" id="backup-btn" onclick="_showBackups()">⏱ Backups</button>
        <button class="sb-btn full green" onclick="exportPDF()">⬇ Export PDF</button>
        <button class="sb-btn full primary" onclick="generate()">Preview CV ›</button>""",
    },
    'forecast': {
        'name': 'ForeCast',
        'theme_id': 'theme-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <label class="sb-btn full accent" style="cursor:pointer;">📥 Import Salesforce<input type="file" accept=".xlsx,.xls" style="display:none" onchange="importSalesforce(this)"></label>
        <button class="sb-btn" onclick="exportExcel()">Excel</button>
        <button class="sb-btn green" onclick="exportPDF()">PDF</button>""",
    },
    'actionlog': {
        'name': 'ActionLog',
        'theme_id': 'theme-toggle-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <button class="sb-btn" onclick="exportExcel()">Excel</button>
        <button class="sb-btn" onclick="exportHTML()">HTML</button>
        <button class="sb-btn" onclick="exportPDF()">PDF</button>
        <button class="sb-btn full primary" onclick="generate()">Preview ›</button>""",
    },
    'bidpack': {
        'name': 'BidPack',
        'theme_id': 'theme-toggle-btn',
        'canvas_selector': '#editor',
        'extra_before_canvas': [],
        'actions': UNDO_REDO + '\n' + SAVE_LOAD + """
        <button class="sb-btn" onclick="exportHTML()">HTML</button>
        <button class="sb-btn" onclick="exportPDF()">PDF</button>
        <button class="sb-btn full accent" style="font-weight:600;" onclick="exportPPTX()">📊 PPTX</button>
        <button class="sb-btn full primary" onclick="generate()">Assemble ›</button>""",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def find_div_end(html, start):
    """Return the index just after the closing </div> matching the <div> at `start`."""
    depth = 0
    i = start
    while i < len(html):
        if html[i:i+4].lower() == '<div':
            depth += 1
            i += 4
        elif html[i:i+6].lower() == '</div>':
            depth -= 1
            i += 6
            if depth == 0:
                return i
        else:
            i += 1
    raise ValueError(f"Unmatched <div> starting at {start}")


def inject_css(html, css):
    """Inject CSS just before the last </style>."""
    pos = html.rfind('</style>')
    if pos == -1:
        return html
    return html[:pos] + css + '\n  ' + html[pos:]


def inject_js(html, js):
    """Inject JS just before the last </script>."""
    pos = html.rfind('</script>')
    if pos == -1:
        return html
    return html[:pos] + js + '\n' + html[pos:]


def add_nav_close_listener(html):
    """Add the click-to-close listener for the nav popover inside DOMContentLoaded."""
    # Inject at the end of the last DOMContentLoaded handler (before its closing });)
    # We look for the last addEventListener DOMContentLoaded block
    pattern = r"(document\.addEventListener\('DOMContentLoaded'[\s\S]*?)(}\s*\);?\s*</script>)"
    match = list(re.finditer(pattern, html))
    if match:
        m = match[-1]
        close_js = "\n  document.addEventListener('click', () => { if (_navOpen) closeNavPopover(); });\n  document.addEventListener('keydown', e => { if (e.key === 'Escape' && _navOpen) closeNavPopover(); });\n"
        new_content = m.group(1) + close_js + m.group(2)
        html = html[:m.start()] + new_content + html[m.end():]
    return html


def transform_tool(slug, config, html):
    tool_name = config['name']
    theme_id  = config['theme_id']

    # 1. Inject CSS
    html = inject_css(html, SHELL_CSS)

    # 2. Inject JS (nav popover + toggleSidebar)
    html = inject_js(html, SHELL_JS)

    # 3. Add close listener
    html = add_nav_close_listener(html)

    # 4. Build new header + nav popover HTML strings
    hdr_html = HEADER_HTML.format(tool_name=tool_name, theme_id=theme_id)
    sb_html  = sidebar_html(config['actions'])

    # 5. Build the full shell injection:
    # We'll insert immediately after <body> tag (before the toolbar div)
    # Actually we'll insert right before the toolbar div.

    canvas_sel = config['canvas_selector']

    # Find toolbar start
    tb_match = re.search(r'<div id="toolbar"[^>]*>', html)
    if not tb_match:
        print(f"  WARNING: no toolbar found in {slug}.html, skipping")
        return html

    tb_start = tb_match.start()
    tb_end   = find_div_end(html, tb_start)

    # For w2w-report: canvas wraps #tab-nav ... end of #main-content
    if slug == 'w2w-report':
        # Find #tab-nav start
        tab_match = re.search(r'<div id="tab-nav"[^>]*>', html)
        # Find #main-content and its end
        mc_match  = re.search(r'<div id="main-content"[^>]*>', html)
        if not tab_match or not mc_match:
            print(f"  WARNING: w2w-report special elements not found")
            return html
        canvas_content_start = tab_match.start()
        canvas_content_end   = find_div_end(html, mc_match.start())
        canvas_content = html[canvas_content_start:canvas_content_end]

        # Also look for #screen-hint if present (not in w2w but just in case)
        before_canvas = ''

        app_body = (
            '\n<div class="app-body">\n' +
            sb_html + '\n' +
            '  <div class="canvas">\n    <div class="canvas-body">\n' +
            before_canvas +
            canvas_content +
            '\n    </div>\n  </div>\n</div>\n'
        )

        html = (
            html[:tb_start] +
            hdr_html + '\n' +
            NAV_POPOVER_HTML + '\n' +
            app_body +
            html[canvas_content_end:]
        )
        return html

    # Standard tools: canvas wraps #editor (and subsequent #output if present)

    # Find canvas_selector start
    cs_match = re.search(r'<div id="' + re.escape(canvas_sel.lstrip('#')) + r'"[^>]*>', html)
    if not cs_match:
        print(f"  WARNING: canvas selector {canvas_sel} not found in {slug}.html")
        return html

    canvas_start = cs_match.start()

    # Check for #screen-hint between toolbar and canvas (timecast only)
    extra_before = config.get('extra_before_canvas', [])
    screen_hint_html = ''
    insert_after_toolbar = tb_end

    for extra_sel in extra_before:
        extra_match = re.search(r'<div[^>]+id="' + re.escape(extra_sel.lstrip('#')) + r'"[^>]*>', html)
        if extra_match and tb_end <= extra_match.start() < canvas_start:
            # This element is between toolbar and canvas - it goes at top of canvas
            extra_start = extra_match.start()
            extra_end   = find_div_end(html, extra_start)
            screen_hint_html = html[extra_start:extra_end]
            # We'll remove it from its original position and put it in canvas-body
            html = html[:extra_start] + html[extra_end:]
            # Recalculate canvas_start after removal
            cs_match2 = re.search(r'<div id="' + re.escape(canvas_sel.lstrip('#')) + r'"[^>]*>', html)
            canvas_start = cs_match2.start()

    # Find the end of the canvas content.
    # For tools with #output, include it too.
    canvas_div_end = find_div_end(html, canvas_start)
    content_end = canvas_div_end

    # Check if there's an #output div right after
    output_match = re.search(r'\s*<div id="output"[^>]*>', html[content_end:content_end+200])
    if output_match:
        output_start_abs = content_end + output_match.start()
        output_end_abs   = find_div_end(html, output_start_abs)
        content_end = output_end_abs

    canvas_content = html[canvas_start:content_end]

    app_body = (
        '\n<div class="app-body">\n' +
        sb_html + '\n' +
        '  <div class="canvas">\n    <div class="canvas-body">\n' +
        (screen_hint_html + '\n' if screen_hint_html else '') +
        canvas_content +
        '\n    </div>\n  </div>\n</div>\n'
    )

    # Also grab anything between tb_end and canvas_start (whitespace/comments) to discard
    html = (
        html[:tb_start] +
        hdr_html + '\n' +
        NAV_POPOVER_HTML + '\n' +
        app_body +
        html[content_end:]
    )

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

        html = transform_tool(slug, config, html)

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  OK: {fname}")

    print("\nDone.")


if __name__ == '__main__':
    main()
