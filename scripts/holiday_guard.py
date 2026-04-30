#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
holiday_guard.py — German public holiday calendar for Bavaria and Berlin.

Usage as a library:
    from scripts.holiday_guard import check_today, HolidayGuard

    guard = HolidayGuard()
    if guard.is_blocked():
        guard.log_and_exit()          # prints message + sys.exit(0)

    # or just check without exiting:
    blocked, name = guard.check()
    if blocked:
        print(f'Holiday: {name}')

Stand-alone:
    python3 scripts/holiday_guard.py             # check today
    python3 scripts/holiday_guard.py 2026-05-01  # check specific date
    python3 scripts/holiday_guard.py --json      # machine-readable
    python3 scripts/holiday_guard.py --list      # print full calendar
"""

import sys, os, re, argparse
from datetime import date, timedelta

# ── Easter calculation (Gaussian algorithm) ───────────────────────────────────
def _easter(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day   = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


# ── Holiday builder ────────────────────────────────────────────────────────────
def _build_holidays(year: int) -> dict[date, dict]:
    """
    Returns {date: {'name_de': ..., 'name_en': ..., 'regions': set()}}
    Regions: 'all', 'bavaria', 'berlin'
    """
    E   = _easter(year)
    hols: dict[date, dict] = {}

    def add(d: date, name_de: str, name_en: str, *regions):
        if d not in hols:
            hols[d] = {'name_de': name_de, 'name_en': name_en, 'regions': set()}
        hols[d]['regions'].update(regions)

    # ── Federal holidays (all states) ─────────────────────────────────────────
    add(date(year, 1,  1),  'Neujahr',                      'New Year\'s Day',            'all')
    add(date(year, 5,  1),  'Tag der Arbeit',               'Labour Day',                 'all')
    add(date(year, 10, 3),  'Tag der Deutschen Einheit',    'German Unity Day',           'all')
    add(date(year, 12, 25), '1. Weihnachtstag',             'Christmas Day',              'all')
    add(date(year, 12, 26), '2. Weihnachtstag',             'Boxing Day',                 'all')

    # ── Easter-relative (all states) ──────────────────────────────────────────
    add(E - timedelta(days=2),  'Karfreitag',               'Good Friday',                'all')
    add(E,                       'Ostersonntag',             'Easter Sunday',              'all')
    add(E + timedelta(days=1),  'Ostermontag',              'Easter Monday',              'all')
    add(E + timedelta(days=39), 'Christi Himmelfahrt',      'Ascension Day',              'all')
    add(E + timedelta(days=49), 'Pfingstsonntag',           'Whit Sunday',                'all')
    add(E + timedelta(days=50), 'Pfingstmontag',            'Whit Monday',                'all')

    # ── Bavaria (Bayern) only ─────────────────────────────────────────────────
    add(date(year, 1,  6),  'Heilige Drei Könige',          'Epiphany',                   'bavaria')
    add(date(year, 8, 15),  'Mariä Himmelfahrt',            'Assumption of Mary',         'bavaria')
    add(date(year, 11, 1),  'Allerheiligen',                'All Saints\' Day',           'bavaria')
    add(E + timedelta(days=60), 'Fronleichnam',             'Corpus Christi',             'bavaria')

    # ── Berlin only ───────────────────────────────────────────────────────────
    add(date(year, 3,  8),  'Internationaler Frauentag',    'International Women\'s Day', 'berlin')
    add(date(year, 10, 31), 'Reformationstag',              'Reformation Day',            'berlin')

    return hols


# ── Main class ─────────────────────────────────────────────────────────────────
class HolidayGuard:
    """
    Holiday guard for Vermarkter dispatch scripts.

    Checks Bavaria + Berlin (union — blocked if holiday in either region).
    Call check() to test a date; call log_and_exit() to abort a script.
    """

    # German month names for the log message
    _MONTHS_DE = [
        '', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
        'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember',
    ]
    _MONTHS_EN = [
        '', 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December',
    ]

    def __init__(self, regions=('bavaria', 'berlin', 'all')):
        self.regions = set(regions)
        self._year   = None
        self._hols   = {}

    def _ensure_year(self, year: int):
        if year != self._year:
            self._hols = _build_holidays(year)
            self._year = year

    def check(self, target: date | None = None) -> tuple[bool, str | None]:
        """
        Returns (is_blocked: bool, holiday_name_en: str | None).
        Checks Bavaria ∪ Berlin — blocked if holiday in either.
        """
        if target is None:
            target = date.today()
        self._ensure_year(target.year)

        entry = self._hols.get(target)
        if entry is None:
            return False, None

        # Blocked if the holiday applies to any of our regions
        if entry['regions'] & self.regions:
            return True, entry['name_en']
        return False, None

    def today_info(self) -> dict:
        """Return full info dict about today (used by dashboard)."""
        today = date.today()
        self._ensure_year(today.year)
        blocked, name = self.check(today)
        entry = self._hols.get(today, {})
        return {
            'blocked':   blocked,
            'name_en':   name,
            'name_de':   entry.get('name_de') if entry else None,
            'date':      today.isoformat(),
            'regions':   sorted(entry.get('regions', set())) if entry else [],
        }

    def next_holiday(self) -> dict | None:
        """Return info about the next upcoming holiday from today."""
        today = date.today()
        self._ensure_year(today.year)
        # Check this year + next (covers Dec 31 edge case)
        for yr in (today.year, today.year + 1):
            self._ensure_year(yr)
            for d in sorted(self._hols):
                if d > today:
                    e = self._hols[d]
                    if e['regions'] & self.regions:
                        return {
                            'date':    d.isoformat(),
                            'name_en': e['name_en'],
                            'name_de': e['name_de'],
                            'days_away': (d - today).days,
                        }
        return None

    def log_and_exit(self, target: date | None = None, script_name: str = ''):
        """
        Print canonical block message and exit with code 0.
        Called by dispatch scripts when is_blocked() is True.
        """
        if target is None:
            target = date.today()
        _, name = self.check(target)
        # Format: "Today is May 1st. Dispatch blocked. Security first."
        month = self._MONTHS_EN[target.month]
        day   = target.day
        suffix = {1:'st', 2:'nd', 3:'rd'}.get(day if day < 20 else day % 10, 'th')
        msg = f'Today is {month} {day}{suffix}. Dispatch blocked. Security first.'
        if name:
            msg += f'  [{name}]'
        if script_name:
            msg = f'[{script_name}] {msg}'
        print(msg, flush=True)
        # Also write to log if _ROOT available
        try:
            _ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_path = os.path.join(_ROOT, 'logs', 'holiday_guard.log')
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f'[{ts}] {msg}\n')
        except Exception:
            pass
        sys.exit(0)

    def is_blocked(self, target: date | None = None) -> bool:
        blocked, _ = self.check(target)
        return blocked

    def year_calendar(self, year: int | None = None) -> list[dict]:
        """Return all holidays for a year as a sorted list."""
        if year is None:
            year = date.today().year
        self._ensure_year(year)
        result = []
        for d in sorted(self._hols):
            if d.year == year:
                e = self._hols[d]
                if e['regions'] & self.regions:
                    result.append({
                        'date':    d.isoformat(),
                        'name_de': e['name_de'],
                        'name_en': e['name_en'],
                        'regions': sorted(e['regions']),
                    })
        return result


# ── Module-level convenience functions ────────────────────────────────────────
_guard = HolidayGuard()

def check_today() -> tuple[bool, str | None]:
    """Module-level shortcut: (blocked, name)."""
    return _guard.check()

def guard_dispatch(script_name: str = ''):
    """
    Drop-in one-liner for any dispatch script.
    Exits with code 0 if today is a holiday.
    """
    blocked, _ = _guard.check()
    if blocked:
        _guard.log_and_exit(script_name=script_name)


# ── CLI ────────────────────────────────────────────────────────────────────────
def _ordinal(n: int) -> str:
    return str(n) + {1:'st',2:'nd',3:'rd'}.get(n if n < 20 else n % 10, 'th')


def main():
    p = argparse.ArgumentParser(description='holiday_guard — German holiday checker')
    p.add_argument('date', nargs='?', default=None, help='Date to check (YYYY-MM-DD)')
    p.add_argument('--json',   action='store_true', help='JSON output')
    p.add_argument('--list',   action='store_true', help='List full year calendar')
    p.add_argument('--year',   type=int, default=None, help='Year for --list')
    args = p.parse_args()

    import json as _json
    g = HolidayGuard()

    if args.list:
        year = args.year or date.today().year
        cal  = g.year_calendar(year)
        if args.json:
            print(_json.dumps(cal, ensure_ascii=False, indent=2))
        else:
            print(f'\nGerman Holidays {year} (Bavaria + Berlin)')
            print('─' * 52)
            for h in cal:
                regs = ', '.join(h['regions'])
                print(f"  {h['date']}  {h['name_de']:<32}  [{regs}]")
            print()
        return

    target = date.fromisoformat(args.date) if args.date else date.today()
    blocked, name = g.check(target)
    info = {
        'date':    target.isoformat(),
        'blocked': blocked,
        'holiday': name,
    }

    if args.json:
        print(_json.dumps(info, ensure_ascii=False))
        return

    if blocked:
        month = HolidayGuard._MONTHS_EN[target.month]
        msg = f'Today is {month} {_ordinal(target.day)}. Dispatch blocked. Security first.  [{name}]'
        print(msg)
        sys.exit(1)   # non-zero exit when blocked (useful in shell scripts)
    else:
        nxt = g.next_holiday()
        print(f'  {target.isoformat()} — clear, no holiday.')
        if nxt:
            print(f'  Next holiday: {nxt["name_en"]} on {nxt["date"]} ({nxt["days_away"]}d away)')


if __name__ == '__main__':
    main()
