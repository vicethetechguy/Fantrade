#!/usr/bin/env python3
"""
tools/align_remaining_ftickers.py
Converts all remaining $Name tickers in club_pages.py, pages3.py, pages.py, and common.py to F-tickers.
"""
import re

MAPPINGS = {
    '$Saka': 'FSAKA',
    '$Haaland': 'FHLND',
    '$Mbappe': 'FKM7',
    '$Vinicius': 'FVJR',
    '$Bellingham': 'FBEL',
    '$Palmer': 'FPLMR',
    '$Yamal': 'FYAML',
    '$Musiala': 'FMUS',
    '$Wirtz': 'FWRTZ',
    '$Rodri': 'FRODR',
    '$Foden': 'FFODN',
    '$Pedri': 'FPEDR',
    '$Saliba': 'FSALI',
    '$Bruno': 'FBRN',
    '$Jackson': 'FJACK',
    '$Arteta': 'FARTA',
    '$Pep': 'FPEP',
    '$Maresca': 'FMARS',
}

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    for old, new in MAPPINGS.items():
        content = content.replace(old, new)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath}")

for path in ['tools/club_pages.py', 'tools/pages3.py', 'tools/pages.py', 'tools/common.py']:
    update_file(path)

print("All remaining files updated with F-tickers.")
