#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_berlin_gap_overwrite.py — Overwrite Berlin leads 212-271 with Elite-standard messages.

Runs sniper_engine.py with:
  --ids 212,213,...,271
  --force          (bypass status=new filter — these are READY TO SEND already)
  --ab empathy     (empathy-first structure)
  --city Berlin    (context)

UA leads detected automatically → bilingual DE+UA message, no GPT call.
"""
import subprocess, sys, os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENGINE = os.path.join(_ROOT, 'scripts', 'sniper_engine.py')

IDS = list(range(212, 272))   # 212 to 271 inclusive = 60 IDs
IDS_STR = ','.join(str(i) for i in IDS)

cmd = [
    sys.executable, _ENGINE,
    '--ids', IDS_STR,
    '--force',
    '--ab', 'empathy',
    '--city', 'Berlin',
    '--delay', '1.5',
]

if '--dry-run' in sys.argv:
    cmd.append('--dry-run')

print('Berlin Gap Overwrite — IDs 212-271')
print('Command:', ' '.join(cmd))
print()
subprocess.run(cmd, check=True)
