#!/usr/bin/env python3
"""
Extract full DOS (Days of Service) data for the data entry UI.
Builds rich per-employee records with all run/segment details.
"""

import openpyxl
import json
from pathlib import Path
from collections import defaultdict


def is_valid_name(name: str) -> bool:
    if not name or not isinstance(name, str):
        return False
    name = name.strip()
    if not name or len(name) < 3:
        return False
    skip = {"primary driver name", "alternative driver name", "supervisors", "absent"}
    if name.lower() in skip:
        return False
    return "," in name and any(c.isalpha() for c in name)


def normalize_name(name: str) -> str:
    return " ".join(name.strip().split())


def extract_dos_data(excel_path: str) -> dict:
    """Extract full run data per employee for UI."""
    wb = openpyxl.load_workbook(excel_path, read_only=True)
    ws = wb["Table 1"]

    # Column indices (0-based)
    COLS = {
        "paddle": 0,
        "block": 1,
        "planned_start": 2,
        "planned_end": 3,
        "planned_hrs": 4,
        "vehicle": 5,
        "actual_start": 6,
        "actual_end": 7,
        "actual_hrs": 8,
        "primary_name": 9,
        "primary_id": 10,
        "alt_name": 11,
        "alt_id": 12,
        "labels": 13,
        "driver_notes": 14,
        "internal_notes": 15,
        "cancelled": 16,
    }

    supervisor_header_row = None
    absent_header_row = None
    by_employee = defaultdict(lambda: {"runs": [], "in_supervisor_section": False, "in_operator_section": False})

    for row_idx, row in enumerate(ws.iter_rows(values_only=True)):
        row = list(row)
        paddle = str(row[COLS["paddle"]] or "").strip()

        if paddle.upper() == "SUPERVISORS":
            supervisor_header_row = row_idx
            continue
        if paddle.upper() == "ABSENT":
            absent_header_row = row_idx

        after_supervisor = supervisor_header_row is not None and row_idx > supervisor_header_row
        before_absent = absent_header_row is None or row_idx < absent_header_row
        is_supervisor_row = after_supervisor and before_absent

        run = {
            "paddle": paddle,
            "block": str(row[COLS["block"]] or "").strip(),
            "planned_start": str(row[COLS["planned_start"]] or "").strip(),
            "planned_end": str(row[COLS["planned_end"]] or "").strip(),
            "planned_hrs": row[COLS["planned_hrs"]],
            "vehicle": str(row[COLS["vehicle"]] or "").strip(),
            "actual_start": str(row[COLS["actual_start"]] or "").strip(),
            "actual_end": str(row[COLS["actual_end"]] or "").strip(),
            "actual_hrs": row[COLS["actual_hrs"]],
            "labels": str(row[COLS["labels"]] or "").strip().replace("\n", " "),
            "driver_notes": str(row[COLS["driver_notes"]] or "").strip().replace("\n", " "),
            "internal_notes": str(row[COLS["internal_notes"]] or "").strip().replace("\n", " "),
            "cancelled": str(row[COLS["cancelled"]] or "").strip(),
        }
        # Convert numeric
        for k in ("planned_hrs", "actual_hrs"):
            try:
                run[k] = float(run[k]) if run[k] else None
            except (TypeError, ValueError):
                run[k] = None

        # Primary driver
        pname = str(row[COLS["primary_name"]] or "").strip()
        pid = str(row[COLS["primary_id"]] or "").strip()
        if is_valid_name(pname):
            key = (normalize_name(pname), pid)
            by_employee[key]["name"] = pname
            by_employee[key]["employee_id"] = pid
            by_employee[key]["runs"].append({**run, "role": "primary"})
            if is_supervisor_row:
                by_employee[key]["in_supervisor_section"] = True
            else:
                by_employee[key]["in_operator_section"] = True

        # Alt driver
        aname = str(row[COLS["alt_name"]] or "").strip()
        aid = str(row[COLS["alt_id"]] or "").strip()
        if is_valid_name(aname):
            key = (normalize_name(aname), aid)
            by_employee[key]["name"] = aname
            by_employee[key]["employee_id"] = aid
            by_employee[key]["runs"].append({**run, "role": "alt"})
            if is_supervisor_row:
                by_employee[key]["in_supervisor_section"] = True
            else:
                by_employee[key]["in_operator_section"] = True

    wb.close()

    # Build final list with employee_type
    employees = []
    for (name, eid), data in sorted(by_employee.items(), key=lambda x: (x[1]["name"].lower(), x[1]["employee_id"])):
        in_op = data["in_operator_section"]
        in_sup = data["in_supervisor_section"]
        if in_op and in_sup:
            emp_type = "both"
        elif in_sup:
            emp_type = "supervisor"
        else:
            emp_type = "operator"
        employees.append({
            "name": data["name"],
            "employee_id": data["employee_id"],
            "employee_type": emp_type,
            "skip": emp_type in ("supervisor", "both"),
            "runs": data["runs"],
        })
    return {"employees": employees, "date": "3/9/2026"}


def main():
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "/Users/david/Downloads/3.9.26.xlsx"
    if not Path(path).exists():
        print(f"File not found: {path}")
        return 1
    data = extract_dos_data(path)
    out_dir = Path(__file__).resolve().parent
    out_json = out_dir / "dos_data.json"
    with open(out_json, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Extracted {len(data['employees'])} employees to {out_json}")

    # Auto-build UI if build_ui exists
    build_ui = out_dir / "build_ui.py"
    if build_ui.exists():
        import subprocess
        subprocess.run([sys.executable, str(build_ui)], check=False)
    return 0


if __name__ == "__main__":
    exit(main() or 0)
