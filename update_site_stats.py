"""
Cifrele din banda de sus a site-ului (assets/stats.js), numărate din fișierele repository-ului:
slide-uri de curs (EN), pagini de seminar (versiunea studenților, EN), Quantlets, grafice.
Numărul de întrebări de quiz se calculează în pagină, din băncile încărcate.

Rulare (după recompilarea PDF-urilor):  python3 update_site_stats.py
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import glob
import json
import os

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))


def pages(pattern):
    return sum(len(pymupdf.open(f)) for f in glob.glob(os.path.join(HERE, pattern)) if '_solutions' not in f)


stats = {
    'chapters': len(glob.glob(os.path.join(HERE, 'EN', 'Courses', 'chapter*.pdf'))),
    'slides': pages('EN/Courses/chapter*.pdf'),
    'seminar': pages('EN/Seminars/seminar*.pdf'),
    'quantlets': len(glob.glob(os.path.join(HERE, 'Quantlets', 'Ch_*', 'MFM_*'))),
    'charts': len(glob.glob(os.path.join(HERE, 'charts', '*.png'))),
}

with open(os.path.join(HERE, 'assets', 'stats.js'), 'w') as f:
    f.write('// Generat de update_site_stats.py; nu editați manual.\n')
    f.write('window.MFM_STATS = ' + json.dumps(stats) + ';\n')
print(stats)
