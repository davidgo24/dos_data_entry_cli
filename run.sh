#!/bin/bash
# Quick run: extract from Excel and open the data entry UI
cd "$(dirname "$0")"
source .venv/bin/activate

EXCEL="${1:-/Users/david/Downloads/3.9.26.xlsx}"
if [[ ! -f "$EXCEL" ]]; then
  echo "Usage: ./run.sh [path/to/dos.xlsx]"
  echo "Example: ./run.sh ~/Downloads/3.9.26.xlsx"
  exit 1
fi

python extract_dos_data.py "$EXCEL"
echo ""
echo "Opening UI..."
open index.html
