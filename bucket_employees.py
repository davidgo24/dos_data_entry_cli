#!/usr/bin/env python3
"""
Extract and bucket all employees from transit DOS (Days of Service) Excel file.
Classifies each employee as Operator or Supervisor based on section placement.
Row with "SUPERVISORS" in first column marks the boundary.
"""

import openpyxl
import json
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class EmployeeProfile:
    name: str
    employee_id: str
    employee_type: str  # "operator" | "supervisor" | "both" (appears in both sections)
    appearances: list  # List of (row_idx, role, paddle/block, section) for audit trail
    notes: list  # Any Labels, Driver Notes, Internal Notes that might be relevant


def is_valid_name(name: str) -> bool:
    """Filter out empty strings, headers, and non-name values."""
    if not name or not isinstance(name, str):
        return False
    name = name.strip()
    if not name or len(name) < 3:
        return False
    # Skip headers and section labels
    skip = {"primary driver name", "alternative driver name", "supervisors", "absent"}
    if name.lower() in skip:
        return False
    # Must look like "Last, First" (comma-separated name)
    if "," in name and any(c.isalpha() for c in name):
        return True
    return False


def normalize_name(name: str) -> str:
    """Normalize name for deduplication (strip, consistent spacing)."""
    return " ".join(name.strip().split())


def get_section_label(row_idx: int, paddle_val) -> str:
    """Human-readable section for the row."""
    if row_idx < 99:
        return "operators"  # Before SUPERVISORS header
    return "supervisors"


def extract_employees(excel_path: str) -> list[EmployeeProfile]:
    """Read Excel and build employee profiles with operator/supervisor bucketing."""
    wb = openpyxl.load_workbook(excel_path, read_only=True)
    ws = wb["Table 1"]

    # Column indices (0-based): Primary Driver Name=9, Primary ID=10, Alt Name=11, Alt ID=12
    # Labels=13, Driver Notes=14, Internal Notes=15, Paddle=0
    PRIMARY_NAME = 9
    PRIMARY_ID = 10
    ALT_NAME = 11
    ALT_ID = 12
    LABELS = 13
    DRIVER_NOTES = 14
    INTERNAL_NOTES = 15
    PADDLE = 0

    # Collect all appearances: (name, id, row_idx, role, paddle, in_supervisor_section)
    seen = set()  # (name, id) for dedup
    raw_appearances = []  # (name, id, row_idx, role, paddle, is_supervisor_row, notes)

    supervisor_header_row = None
    absent_header_row = None
    for row_idx, row in enumerate(ws.iter_rows(values_only=True)):
        row = list(row)
        paddle = str(row[PADDLE] or "").strip()

        # Find SUPERVISORS header and ABSENT row
        # Only rows between SUPERVISORS and ABSENT are actual supervisor shifts (OPS, Open, Closing, Field 1-4, MID/OPS)
        # ABSENT subsection lists both operators and supervisors who are absent - don't use for classification
        if paddle.upper() == "SUPERVISORS":
            supervisor_header_row = row_idx
            continue
        if paddle.upper() == "ABSENT":
            absent_header_row = row_idx
        # Supervisor section = after SUPERVISORS header, before ABSENT header
        after_supervisor = supervisor_header_row is not None and row_idx > supervisor_header_row
        before_absent = absent_header_row is None or row_idx < absent_header_row
        is_supervisor_section = after_supervisor and before_absent

        # Primary driver
        pname = str(row[PRIMARY_NAME] or "").strip()
        pid = str(row[PRIMARY_ID] or "").strip()
        if is_valid_name(pname):
            notes = []
            if row[LABELS]:
                notes.append(f"Labels: {row[LABELS]}")
            if row[DRIVER_NOTES]:
                notes.append(f"Driver: {row[DRIVER_NOTES]}")
            if row[INTERNAL_NOTES]:
                notes.append(f"Internal: {row[INTERNAL_NOTES]}")
            raw_appearances.append((normalize_name(pname), pid, row_idx, "primary", paddle, is_supervisor_section, notes))

        # Alternative driver
        aname = str(row[ALT_NAME] or "").strip()
        aid = str(row[ALT_ID] or "").strip()
        if is_valid_name(aname):
            notes = []
            if row[LABELS]:
                notes.append(f"Labels: {row[LABELS]}")
            if row[DRIVER_NOTES]:
                notes.append(f"Driver: {row[DRIVER_NOTES]}")
            if row[INTERNAL_NOTES]:
                notes.append(f"Internal: {row[INTERNAL_NOTES]}")
            raw_appearances.append((normalize_name(aname), aid, row_idx, "alt", paddle, is_supervisor_section, notes))

    wb.close()

    # Group by (name, id) and determine type
    by_employee: dict[tuple[str, str], dict] = defaultdict(lambda: {"appearances": [], "notes": [], "in_operator": False, "in_supervisor": False})
    for name, eid, row_idx, role, paddle, is_super, notes in raw_appearances:
        key = (name, eid)
        by_employee[key]["name"] = name
        by_employee[key]["id"] = eid
        by_employee[key]["appearances"].append({
            "row": row_idx,
            "role": role,
            "paddle_block": paddle,
            "section": "supervisors" if is_super else "operators",
        })
        by_employee[key]["notes"].extend(notes)
        if is_super:
            by_employee[key]["in_supervisor"] = True
        else:
            by_employee[key]["in_operator"] = True

    # Build profiles with employee_type
    profiles = []
    for (name, eid), data in sorted(by_employee.items(), key=lambda x: (x[1]["name"].lower(), x[1]["id"])):
        in_op = data["in_operator"]
        in_sup = data["in_supervisor"]
        if in_op and in_sup:
            emp_type = "both"  # Appears in both sections
        elif in_sup:
            emp_type = "supervisor"
        else:
            emp_type = "operator"

        # Dedupe notes
        all_notes = list(dict.fromkeys(data["notes"]))  # preserve order, remove dupes
        profiles.append(EmployeeProfile(
            name=data["name"],
            employee_id=eid,
            employee_type=emp_type,
            appearances=data["appearances"],
            notes=all_notes[:20],  # Cap for readability
        ))
    return profiles


def main():
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "/Users/david/Downloads/3.9.26.xlsx"
    if not Path(path).exists():
        print(f"File not found: {path}")
        sys.exit(1)

    profiles = extract_employees(path)

    # Summary by type
    by_type = defaultdict(list)
    for p in profiles:
        by_type[p.employee_type].append(p.name)

    print("=" * 70)
    print("EMPLOYEE BUCKETING SUMMARY")
    print("=" * 70)
    print(f"Total unique employees: {len(profiles)}")
    print(f"  Operators only:     {len(by_type['operator'])}")
    print(f"  Supervisors only:  {len(by_type['supervisor'])}")
    print(f"  Both sections:     {len(by_type['both'])}  (supervisor who also covered runs)")
    print()

    # Write outputs to project folder (same dir as script) for easier access
    out_dir = Path(__file__).resolve().parent
    out_json = out_dir / "employee_profiles.json"
    with open(out_json, "w") as f:
        json.dump([asdict(p) for p in profiles], f, indent=2)
    print(f"Full profiles written to: {out_json}")

    # Write simple CSV for quick review
    out_csv = out_dir / "employee_profiles.csv"
    with open(out_csv, "w") as f:
        f.write("name,employee_id,type,appearance_count,suggest_skip\n")
        for p in profiles:
            skip = "yes" if p.employee_type in ("supervisor", "both") else "no"
            f.write(f'"{p.name}",{p.employee_id},{p.employee_type},{len(p.appearances)},{skip}\n')
    print(f"CSV summary written to: {out_csv}")

    # Print table
    print()
    print("-" * 70)
    print("OPERATORS (process for data entry)")
    print("-" * 70)
    for p in sorted(profiles, key=lambda x: x.name):
        if p.employee_type == "operator":
            print(f"  {p.name} (ID: {p.employee_id})")

    print()
    print("-" * 70)
    print("SUPERVISORS (skip for data entry)")
    print("-" * 70)
    for p in sorted(profiles, key=lambda x: x.name):
        if p.employee_type in ("supervisor", "both"):
            print(f"  {p.name} (ID: {p.employee_id}) [{p.employee_type}]")


if __name__ == "__main__":
    main()
