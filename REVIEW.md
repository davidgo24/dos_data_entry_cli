# DOS Data Entry — App Review

## Top 3 Urgent Fixes

### 1. Remove debug console statements
The `renderEmp` function has `console.log` and `console.warn` calls left from debugging. These clutter the browser console and can leak internal state. Remove them for production.

**Location:** `static/index.html` lines 587, 599, 707, 759, 970

### 2. Guard against missing `emp.runs` in export
In `doExport`, `emp.runs.map(...)` will throw if an employee has no `runs` array (e.g. malformed data or edge case). Add a guard: `(emp.runs || []).map(...)`.

**Location:** `static/index.html` line 1135

### 3. Fix favicon 404
Browsers request `/favicon.ico` by default, causing a 404 and console noise. Add a minimal favicon (e.g. inline data URI in `<link>`) or a static file to silence the error.

**Location:** `static/index.html` `<head>` — add `<link rel="icon" href="data:image/svg+xml,...">` or serve a favicon.

---

## Top 3 Improvement Suggestions

### 1. Warn when export has no data
When `e` (export all) or `Shift+e` (export done only) is pressed and there are no TCP rows to export (e.g. no runs included, or no one marked done for Shift+e), the app still downloads a CSV with only headers. Consider showing a status message like "No data to export" and skipping the download instead of offering an empty file.

### 2. Validate custom segments before export
When "Use custom segments" is checked for an employee but no valid segments exist (missing code, start, or end), that employee is silently skipped. Consider:
- Showing a warning in the status bar when such employees are encountered
- Or validating on blur/save and showing an inline error

### 3. Add 1000 (GUAR) to custom labor options
The custom segment labor dropdown includes 1020, 1013, 3002, etc., but not **1000** (guarantee). Short runs often use 1000 GUAR. Add it to `CUSTOM_LABOR_OPTIONS` for consistency with the segment logic.

---

## Summary

| Priority | Item |
|----------|------|
| Urgent   | Remove console.log/warn/error from renderEmp |
| Urgent   | Guard `emp.runs` in doExport |
| Urgent   | Add favicon to fix 404 |
| Improve  | Skip download and show message when export is empty |
| Improve  | Validate/warn for invalid custom segments |
| Improve  | Add 1000 GUAR to custom labor options |
