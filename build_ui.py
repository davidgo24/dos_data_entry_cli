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
      --highlight: #38bdf8;
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
    .sidebar-date {{
      font-size: 0.8rem;
      color: var(--accent);
      margin-top: 0.25rem;
    }}
    .filter-bar {{
      display: flex;
      gap: 0.5rem;
      margin-top: 0.75rem;
      flex-wrap: wrap;
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
      min-width: 0;
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
    .emp-item:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
    .emp-item.active:focus-visible {{ outline-color: var(--highlight); }}
    .emp-item.active {{ background: var(--surface2); border-left: 3px solid var(--highlight); }}
    .emp-item.active > div > div:first-child {{ color: var(--highlight); font-weight: 600; }}
    .emp-item.active .emp-id {{ color: var(--highlight); }}
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
      min-width: 0;
      overflow-y: auto;
      padding: 2rem 2.5rem;
    }}
    .main-inner {{
      max-width: 900px;
      margin: 0 auto;
      min-width: 0;
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
      color: var(--highlight);
    }}
    .emp-id {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      color: var(--text-muted);
    }}
    .emp-header .emp-id {{
      font-size: 1rem;
      color: var(--highlight);
      background: rgba(56, 189, 248, 0.15);
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      display: inline-block;
      margin-top: 0.35rem;
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
      grid-template-columns: repeat(2, 1fr);
      gap: 1.25rem;
      margin-bottom: 1rem;
    }}
    .run-group {{
      background: rgba(0,0,0,0.2);
      border-radius: 8px;
      padding: 1rem;
      border: 1px solid var(--border);
    }}
    .run-group-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 0.5rem;
    }}
    .run-group-time {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 1rem;
      font-weight: 500;
      margin-bottom: 0.35rem;
    }}
    .run-group-hrs {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.95rem;
    }}
    .run-group-hrs.hrs {{ color: var(--accent); }}
    .run-group-hrs.ot {{ color: var(--warn); }}
    .actual-segments {{ margin-top: 0.5rem; }}
    .segment-line {{ font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin-bottom: 0.35rem; }}
    .segment-line:last-child {{ margin-bottom: 0; }}
    .segment-line .seg-code {{ color: var(--text-muted); font-size: 0.8rem; margin-right: 0.4rem; }}
    .segment-line.guar .seg-code {{ color: var(--accent); }}
    .segment-line.ot .seg-code {{ color: var(--warn); }}
    .segment-total {{ font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem; padding-top: 0.35rem; border-top: 1px dashed var(--border); }}
    .run-time {{
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
      margin-top: 0.5rem;
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
    .note-banner {{
      background: rgba(245, 158, 11, 0.12);
      border-left: 4px solid var(--warn);
      padding: 0.75rem 1rem;
      margin-top: 0.5rem;
      border-radius: 0 6px 6px 0;
    }}
    .note-banner:first-of-type {{ margin-top: 0.75rem; }}
    .note-banner-label {{
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--warn);
      margin-bottom: 0.25rem;
    }}
    .note-banner-content {{
      font-size: 0.9rem;
      color: var(--text);
    }}
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
      min-width: 80px;
    }}
    .entry-row input {{
      padding: 0.5rem 0.75rem;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--surface2);
      color: var(--text);
      font-family: inherit;
      font-size: 0.9rem;
      flex: 1;
      min-width: 0;
    }}
    .entry-row input:focus {{
      outline: none;
      border-color: var(--accent);
    }}
    .nav-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
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
    @media (max-width: 1100px) {{
      .sidebar {{ width: 240px; }}
      .main {{ padding: 1.25rem 1.5rem; }}
      .emp-card {{ padding: 1.5rem; }}
      .run-times {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 900px) {{
      .sidebar {{ width: 220px; }}
      .sidebar-header {{ padding: 0.75rem 1rem; }}
      .main {{ padding: 1rem; }}
      .emp-card {{ padding: 1.25rem; }}
      .emp-name {{ font-size: 1.25rem; }}
    }}
    @media (max-width: 700px) {{
      .sidebar {{ width: 200px; }}
      .main {{ padding: 0.75rem 1rem; }}
      .emp-card {{ padding: 1rem; }}
    }}
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-title">DOS Data Entry</div>
        <div class="sidebar-date" id="dosDate"></div>
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
    function esc(v) {{ if (v == null || v === undefined) return ''; return String(v).replace(/\\\\/g,'\\\\\\\\').replace(/`/g,'\\\\`').replace(/\\${{/g,'\\\\${{'); }}
    let filter = 'operators';
    let selectedIdx = 0;
    let processed = new Set(JSON.parse(localStorage.getItem(STORAGE_KEY + '_done') || '[]'));
    let entries = JSON.parse(localStorage.getItem(STORAGE_KEY + '_entries') || '{{}}');

    function updateScheduleDate() {{
      const el = document.getElementById('dosDate');
      const d = window.DOS_DATA && window.DOS_DATA.date;
      if (el && d) el.textContent = 'Schedule: ' + d;
    }}

    function filtered() {{
      if (filter === 'operators') return EMP.filter(e => !e.skip);
      return EMP;
    }}

    function renderList() {{
      const list = document.getElementById('empList');
      const F = filtered();
      list.innerHTML = F.map((e, i) => `
        <div class="emp-item ${{e.skip ? 'skip' : ''}} ${{processed.has(e.employee_id) ? 'done' : ''}} ${{i === selectedIdx ? 'active' : ''}}"
             data-idx="${{i}}" data-id="${{esc(e.employee_id)}}" tabindex="0" role="button">
          <span class="check">${{processed.has(e.employee_id) ? '✓' : ''}}</span>
          <div>
            <div>${{esc(e.name)}}</div>
            <div class="emp-id" style="font-size:0.75rem;margin-top:2px">ID ${{esc(e.employee_id)}}${{e.skip ? ' · Skip' : ''}}</div>
          </div>
        </div>
      `).join('');
      list.querySelectorAll('.emp-item').forEach(el => {{
        el.addEventListener('click', () => {{ selectEmp(parseInt(el.dataset.idx)); }});
        el.addEventListener('keydown', (ev) => {{ if (ev.key === 'Enter' || ev.key === ' ') {{ ev.preventDefault(); selectEmp(parseInt(el.dataset.idx)); }} }});
      }});
      const activeItem = list.querySelector('.emp-item.active');
      if (activeItem) activeItem.focus();
    }}

    function formatHrs(v) {{
      if (v == null) return '—';
      return Number(v).toFixed(2);
    }}
    function hrsToHMM(v) {{
      if (v == null) return '—';
      const h = Math.floor(v);
      const m = Math.round((v - h) * 60);
      return m < 10 ? h + ':0' + m : h + ':' + m;
    }}

    function isOT(planned, actual) {{
      if (actual == null) return false;
      return actual > 8.01;
    }}

    function isShort(planned, actual) {{
      if (actual == null) return false;
      return actual < 7.99 && actual > 0;
    }}

    function parseTime(s) {{
      if (!s || typeof s !== 'string') return 0;
      const [h, m] = s.split(':').map(x => parseInt(x, 10) || 0);
      return h * 60 + m;
    }}
    function formatTime(mins) {{
      const h = Math.floor(mins / 60) % 24;
      const m = Math.round(mins % 60);
      return String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0');
    }}
    function getActualSegments(r) {{
      const ah = r.actual_hrs;
      if (ah == null || ah <= 0) return null;
      if (ah >= 7.99 && ah <= 8.01) {{
        return [{{ code: '1020 REG', start: r.actual_start, end: r.actual_end, type: 'reg' }}];
      }}
      if (ah < 8) {{
        const guarHrs = 8 - ah;
        const endMins = parseTime(r.actual_end) + Math.round(guarHrs * 60);
        const guarEnd = formatTime(endMins);
        return [
          {{ code: '1020 REG', start: r.actual_start, end: r.actual_end, type: 'reg' }},
          {{ code: '1000 GUAR', start: r.actual_end, end: guarEnd, type: 'guar' }}
        ];
      }}
      const regEndMins = parseTime(r.actual_start) + 8 * 60;
      const regEnd = formatTime(regEndMins);
      return [
        {{ code: '1020 REG', start: r.actual_start, end: regEnd, type: 'reg' }},
        {{ code: '1013 OT1.5', start: regEnd, end: r.actual_end, type: 'ot' }}
      ];
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
        const segments = getActualSegments(r);
        const noteBanners = [];
        if (r.driver_notes) noteBanners.push(`<div class="note-banner"><div class="note-banner-label">Driver Notes:</div><div class="note-banner-content">${{esc(r.driver_notes)}}</div></div>`);
        if (r.internal_notes) noteBanners.push(`<div class="note-banner"><div class="note-banner-label">Internal Notes:</div><div class="note-banner-content">${{esc(r.internal_notes)}}</div></div>`);
        if (r.labels) noteBanners.push(`<div class="note-banner"><div class="note-banner-label">Labels:</div><div class="note-banner-content">${{esc(r.labels)}}</div></div>`);
        let actualHtml;
        if (segments && segments.length > 0) {{
          actualHtml = '<div class="actual-segments">' + segments.map(s => `<div class="segment-line ${{s.type}}"><span class="seg-code">${{esc(s.code)}}</span>${{esc(s.start)}} – ${{esc(s.end)}}</div>`).join('') + '<div class="segment-total">' + hrsToHMM(r.actual_hrs) + '</div></div>';
        }} else {{
          const needsG = isShort(r.planned_hrs, r.actual_hrs);
          const needsOT = isOT(r.planned_hrs, r.actual_hrs);
          actualHtml = `<div class="run-group-time">${{esc(r.actual_start)}} – ${{esc(r.actual_end)}}</div><div class="run-group-hrs ${{needsOT ? 'ot' : 'hrs'}}">${{formatHrs(r.actual_hrs)}} hrs${{needsG ? ' ⚠ Guarantee' : ''}}${{needsOT ? ' OT' : ''}}</div>`;
        }}
        return `
          <div class="run-card">
            <div class="run-header">
              <span class="run-paddle">${{esc(r.paddle)}}</span>
              ${{r.block ? `<span class="run-block">Block ${{esc(r.block)}}</span>` : ''}}
            </div>
            <div class="run-times">
              <div class="run-group">
                <div class="run-group-label">Planned</div>
                <div class="run-group-time">${{esc(r.planned_start)}} – ${{esc(r.planned_end)}}</div>
                <div class="run-group-hrs hrs">${{formatHrs(r.planned_hrs)}} hrs</div>
              </div>
              <div class="run-group">
                <div class="run-group-label">Actual</div>
                ${{actualHtml}}
              </div>
            </div>
            ${{r.vehicle ? `<div class="run-time"><span class="run-time-label">Vehicle</span><span class="run-time-val">${{esc(r.vehicle)}}</span></div>` : ''}}
            ${{noteBanners.join('')}}
          </div>
        `;
      }}).join('');

      document.getElementById('mainContent').innerHTML = `
        <div class="emp-card">
          <div class="emp-header">
            <div>
              <div class="emp-name">${{esc(e.name)}}</div>
              <div class="emp-id">Employee ID: ${{esc(e.employee_id)}}</div>
            </div>
            <span class="badge ${{e.employee_type}}">${{e.skip ? 'Skip (Supervisor)' : 'Operator'}}</span>
          </div>
          <div class="runs">${{runsHtml}}</div>
          ${{!e.skip ? `
          <div class="entry-section">
            <h4>Notes</h4>
            <div class="entry-row">
              <label>Notes</label>
              <input type="text" placeholder="Optional notes for this employee..." id="entryNotes">
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
      const notesInput = document.getElementById('entryNotes');
      if (entries[id] && notesInput) notesInput.value = entries[id].notes ?? '';

      function saveEntry() {{
        if (e.skip) return;
        entries[id] = {{ notes: notesInput?.value ?? '' }};
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
      const rows = [['employee_id', 'name', 'notes']];
      EMP.filter(e => !e.skip && entries[e.employee_id]).forEach(e => {{
        const x = entries[e.employee_id];
        rows.push([e.employee_id, e.name, x.notes || '']);
      }});
      const csv = rows.map(r => r.map(c => `"${{String(c).replace(/"/g,'""')}}"`).join(',')).join('\\n');
      const a = document.createElement('a');
      a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
      a.download = 'dos_entries_' + new Date().toISOString().slice(0,10) + '.csv';
      a.click();
    }});

    updateScheduleDate();
    renderList();
    renderEmp();
  </script>
</body>
</html>'''


if __name__ == "__main__":
    exit(main() or 0)
