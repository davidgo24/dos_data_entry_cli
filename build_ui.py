#!/usr/bin/env python3
"""Generate index.html with embedded DOS data (no server needed)."""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DOS_JSON = SCRIPT_DIR / "dos_data.json"
OUT_HTML = SCRIPT_DIR / "index.html"


def main():
    if not DOS_JSON.exists():
        print(f"Run extract_dos_data.py first. Missing: {DOS_JSON}")
        return 1
    data = json.loads(DOS_JSON.read_text())
    html = generate_html(data)
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Built {OUT_HTML}")
    return 0


def generate_html(data: dict) -> str:
    data_js = json.dumps(data)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DOS Data Entry — Transit</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0f0f12;
      --surface: #18181c;
      --surface2: #232329;
      --border: #2e2e35;
      --text: #e8e8ec;
      --text-muted: #8b8b96;
      --accent: #22c55e;
      --accent-dim: #16a34a;
      --warn: #f59e0b;
      --skip: #6b7280;
      --radius: 10px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'DM Sans', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.5;
    }}
    .app {{
      display: flex;
      height: 100vh;
      overflow: hidden;
    }}
    .sidebar {{
      width: 280px;
      flex-shrink: 0;
      background: var(--surface);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    .sidebar-header {{
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--border);
      flex-shrink: 0;
    }}
    .sidebar-title {{
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .filter-bar {{
      display: flex;
      gap: 0.5rem;
      margin-top: 0.75rem;
    }}
    .filter-btn {{
      padding: 0.4rem 0.75rem;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: transparent;
      color: var(--text-muted);
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .filter-btn:hover {{ color: var(--text); border-color: var(--text-muted); }}
    .filter-btn.active {{
      background: var(--accent);
      border-color: var(--accent);
      color: var(--bg);
    }}
    .emp-list {{
      flex: 1;
      overflow-y: auto;
      padding: 0.5rem;
    }}
    .emp-item {{
      padding: 0.6rem 0.8rem;
      border-radius: var(--radius);
      cursor: pointer;
      transition: background 0.15s;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .emp-item:hover {{ background: var(--surface2); }}
    .emp-item.active {{ background: var(--surface2); border-left: 3px solid var(--accent); }}
    .emp-item.skip {{ opacity: 0.6; }}
    .emp-item .check {{
      width: 18px;
      height: 18px;
      border-radius: 4px;
      border: 2px solid var(--border);
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      color: var(--accent);
    }}
    .emp-item.done .check {{ background: var(--accent); border-color: var(--accent); color: var(--bg); }}
    .main {{
      flex: 1;
      overflow-y: auto;
      padding: 2rem 2.5rem;
    }}
    .main-inner {{
      max-width: 900px;
      margin: 0 auto;
    }}
    .emp-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 2rem;
    }}
    .emp-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 1.5rem;
      padding-bottom: 1.25rem;
      border-bottom: 1px solid var(--border);
    }}
    .emp-name {{
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--text);
    }}
    .emp-id {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      color: var(--text-muted);
    }}
    .badge {{
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
    }}
    .badge.operator {{ background: rgba(34, 197, 94, 0.2); color: var(--accent); }}
    .badge.supervisor {{ background: rgba(107, 114, 128, 0.3); color: var(--text-muted); }}
    .run-card {{
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem;
      margin-bottom: 1rem;
    }}
    .run-card:last-child {{ margin-bottom: 0; }}
    .run-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1rem;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    .run-paddle {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--accent);
    }}
    .run-block {{ color: var(--text-muted); font-size: 0.9rem; }}
    .run-times {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      margin-bottom: 1rem;
    }}
    @media (max-width: 600px) {{ .run-times {{ grid-template-columns: repeat(2, 1fr); }} }}
    .run-time {{
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }}
    .run-time-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
    }}
    .run-time-val {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 1rem;
      font-weight: 500;
    }}
    .run-time-val.hrs {{ color: var(--accent); }}
    .run-time-val.ot {{ color: var(--warn); }}
    .run-notes {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 0.75rem;
      padding-top: 0.75rem;
      border-top: 1px dashed var(--border);
    }}
    .run-notes span {{ display: block; margin-bottom: 0.2rem; }}
    .entry-section {{
      margin-top: 1.5rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--border);
    }}
    .entry-section h4 {{
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 1rem;
    }}
    .entry-row {{
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      align-items: center;
      margin-bottom: 1rem;
    }}
    .entry-row label {{
      font-size: 0.9rem;
      color: var(--text-muted);
      min-width: 120px;
    }}
    .entry-row input, .entry-row select {{
      padding: 0.5rem 0.75rem;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--surface2);
      color: var(--text);
      font-family: inherit;
      font-size: 0.9rem;
    }}
    .entry-row input:focus, .entry-row select:focus {{
      outline: none;
      border-color: var(--accent);
    }}
    .entry-row input[type="number"] {{ width: 80px; }}
    .nav-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      margin-top: 2rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--border);
    }}
    .nav-btn {{
      padding: 0.6rem 1.25rem;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text);
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .nav-btn:hover {{
      background: var(--surface2);
      border-color: var(--text-muted);
    }}
    .nav-btn.primary {{
      background: var(--accent);
      border-color: var(--accent);
      color: var(--bg);
    }}
    .nav-btn.primary:hover {{ background: var(--accent-dim); }}
    .progress {{
      font-size: 0.85rem;
      color: var(--text-muted);
    }}
    .empty-state {{
      text-align: center;
      padding: 4rem 2rem;
      color: var(--text-muted);
      font-size: 1.1rem;
    }}
    .empty-state p {{ margin: 0.5rem 0; }}
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-title">DOS Data Entry</div>
        <div class="filter-bar">
          <button class="filter-btn active" data-filter="operators">Operators</button>
          <button class="filter-btn" data-filter="all">All</button>
          <button class="filter-btn" id="clearProgress" title="Clear progress and entries for new day">Clear</button>
          <button class="filter-btn" id="exportBtn" title="Download entries as CSV">Export</button>
        </div>
      </div>
      <div class="emp-list" id="empList"></div>
    </aside>
    <main class="main">
      <div class="main-inner" id="mainContent"></div>
    </main>
  </div>
  <script>
    window.DOS_DATA = {data_js};

    const EMP = window.DOS_DATA.employees;
    const STORAGE_KEY = 'dos_data_entry';
    let filter = 'operators';
    let selectedIdx = 0;
    let processed = new Set(JSON.parse(localStorage.getItem(STORAGE_KEY + '_done') || '[]'));
    let entries = JSON.parse(localStorage.getItem(STORAGE_KEY + '_entries') || '{{}}');

    function filtered() {{
      if (filter === 'operators') return EMP.filter(e => !e.skip);
      return EMP;
    }}

    function renderList() {{
      const list = document.getElementById('empList');
      const F = filtered();
      list.innerHTML = F.map((e, i) => `
        <div class="emp-item ${{e.skip ? 'skip' : ''}} ${{processed.has(e.employee_id) ? 'done' : ''}} ${{i === selectedIdx ? 'active' : ''}}"
             data-idx="${{i}}" data-id="${{e.employee_id}}">
          <span class="check">${{processed.has(e.employee_id) ? '✓' : ''}}</span>
          <div>
            <div>${{e.name}}</div>
            <div class="emp-id" style="font-size:0.75rem;margin-top:2px">ID ${{e.employee_id}}${{e.skip ? ' · Skip' : ''}}</div>
          </div>
        </div>
      `).join('');
      list.querySelectorAll('.emp-item').forEach(el => {{
        el.addEventListener('click', () => {{ selectEmp(parseInt(el.dataset.idx)); }});
      }});
    }}

    function formatHrs(v) {{
      if (v == null) return '—';
      return Number(v).toFixed(2);
    }}

    function isOT(planned, actual) {{
      if (actual == null) return false;
      return actual > 8.01;
    }}

    function isShort(planned, actual) {{
      if (actual == null) return false;
      return actual < 7.99 && actual > 0;
    }}

    function renderEmp() {{
      const F = filtered();
      if (F.length === 0) {{
        document.getElementById('mainContent').innerHTML = `
          <div class="empty-state">
            <p>No employees match the current filter.</p>
            <p>Switch to "All" to see supervisors.</p>
          </div>
        `;
        return;
      }}
      const e = F[selectedIdx];
      const runsHtml = e.runs.map(r => {{
        const needsGuarantee = isShort(r.planned_hrs, r.actual_hrs);
        const needsOT = isOT(r.planned_hrs, r.actual_hrs);
        const notes = [r.labels, r.driver_notes, r.internal_notes].filter(Boolean).join(' · ');
        return `
          <div class="run-card">
            <div class="run-header">
              <span class="run-paddle">${{r.paddle}}</span>
              ${{r.block ? `<span class="run-block">Block ${{r.block}}</span>` : ''}}
            </div>
            <div class="run-times">
              <div class="run-time">
                <span class="run-time-label">Planned</span>
                <span class="run-time-val">${{r.planned_start}} – ${{r.planned_end}}</span>
              </div>
              <div class="run-time">
                <span class="run-time-label">Actual</span>
                <span class="run-time-val">${{r.actual_start}} – ${{r.actual_end}}</span>
              </div>
              <div class="run-time">
                <span class="run-time-label">Planned Hrs</span>
                <span class="run-time-val hrs">${{formatHrs(r.planned_hrs)}}</span>
              </div>
              <div class="run-time">
                <span class="run-time-label">Actual Hrs</span>
                <span class="run-time-val ${{needsOT ? 'ot' : 'hrs'}}">${{formatHrs(r.actual_hrs)}}${{needsGuarantee ? ' ⚠ Guarantee' : ''}}${{needsOT ? ' OT' : ''}}</span>
              </div>
            </div>
            ${{r.vehicle ? `<div class="run-time"><span class="run-time-label">Vehicle</span><span class="run-time-val">${{r.vehicle}}</span></div>` : ''}}
            ${{notes ? `<div class="run-notes">${{notes}}</div>` : ''}}
          </div>
        `;
      }}).join('');

      document.getElementById('mainContent').innerHTML = `
        <div class="emp-card">
          <div class="emp-header">
            <div>
              <div class="emp-name">${{e.name}}</div>
              <div class="emp-id">Employee ID: ${{e.employee_id}}</div>
            </div>
            <span class="badge ${{e.employee_type}}">${{e.skip ? 'Skip (Supervisor)' : 'Operator'}}</span>
          </div>
          <div class="runs">${{runsHtml}}</div>
          ${{!e.skip ? `
          <div class="entry-section">
            <h4>Data Entry</h4>
            <div class="entry-row">
              <label>Guarantee Hrs</label>
              <input type="number" step="0.25" min="0" max="8" placeholder="—" id="guaranteeHrs">
            </div>
            <div class="entry-row">
              <label>OT Type</label>
              <select id="otType">
                <option value="">— Select —</option>
                <option value="cte">CTE</option>
                <option value="lpi">LPI</option>
                <option value="paid_as_ot">Paid as OT</option>
              </select>
            </div>
            <div class="entry-row">
              <label>Notes</label>
              <input type="text" placeholder="Optional notes..." id="entryNotes" style="flex:1;min-width:200px">
            </div>
          </div>
          ` : ''}}
          <div class="nav-bar">
            <button class="nav-btn" id="btnPrev">← Previous</button>
            <div class="progress">
              ${{filtered().findIndex(x => x.employee_id === e.employee_id) + 1}} / ${{filtered().length}}
            </div>
            <div>
              ${{!e.skip ? `<button class="nav-btn primary" id="btnDone">Mark Done & Next</button>` : ''}}
              <button class="nav-btn" id="btnNext">Next →</button>
            </div>
          </div>
        </div>
      `;

      const id = e.employee_id;
      const gInput = document.getElementById('guaranteeHrs');
      const otSelect = document.getElementById('otType');
      const notesInput = document.getElementById('entryNotes');
      if (entries[id]) {{
        if (gInput) gInput.value = entries[id].guaranteeHrs ?? '';
        if (otSelect) otSelect.value = entries[id].otType ?? '';
        if (notesInput) notesInput.value = entries[id].notes ?? '';
      }}

      function saveEntry() {{
        if (e.skip) return;
        entries[id] = {{
          guaranteeHrs: gInput?.value ?? '',
          otType: otSelect?.value ?? '',
          notes: notesInput?.value ?? ''
        }};
        localStorage.setItem(STORAGE_KEY + '_entries', JSON.stringify(entries));
      }}

      document.getElementById('btnPrev')?.addEventListener('click', () => {{ saveEntry(); nav(-1); }});
      document.getElementById('btnNext')?.addEventListener('click', () => {{ saveEntry(); nav(1); }});
      document.getElementById('btnDone')?.addEventListener('click', () => {{
        saveEntry();
        processed.add(id);
        localStorage.setItem(STORAGE_KEY + '_done', JSON.stringify([...processed]));
        nav(1);
      }});
    }}

    function selectEmp(idx) {{
      selectedIdx = idx;
      renderList();
      renderEmp();
    }}

    function nav(delta) {{
      const F = filtered();
      selectedIdx = (selectedIdx + delta + F.length) % F.length;
      renderList();
      renderEmp();
    }}

    document.querySelectorAll('.filter-btn').forEach(btn => {{
      if (btn.id === 'clearProgress') return;
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        filter = btn.dataset.filter;
        selectedIdx = 0;
        renderList();
        renderEmp();
      }});
    }});

    document.getElementById('clearProgress')?.addEventListener('click', () => {{
      if (confirm('Clear all progress and saved entries? Use when starting a new day.')) {{
        processed.clear();
        entries = {{}};
        localStorage.removeItem(STORAGE_KEY + '_done');
        localStorage.removeItem(STORAGE_KEY + '_entries');
        renderList();
        renderEmp();
      }}
    }});

    document.getElementById('exportBtn')?.addEventListener('click', () => {{
      const rows = [['employee_id', 'name', 'guarantee_hrs', 'ot_type', 'notes']];
      EMP.filter(e => !e.skip && entries[e.employee_id]).forEach(e => {{
        const x = entries[e.employee_id];
        rows.push([e.employee_id, e.name, x.guaranteeHrs || '', x.otType || '', x.notes || '']);
      }});
      const csv = rows.map(r => r.map(c => `"${{String(c).replace(/"/g,'""')}}"`).join(',')).join('\\n');
      const a = document.createElement('a');
      a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
      a.download = 'dos_entries_' + new Date().toISOString().slice(0,10) + '.csv';
      a.click();
    }});

    renderList();
    renderEmp();
  </script>
</body>
</html>'''


if __name__ == "__main__":
    exit(main() or 0)
