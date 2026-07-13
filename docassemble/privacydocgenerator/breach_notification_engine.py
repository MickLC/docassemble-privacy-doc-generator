"""
breach_notification_engine.py

Looks up per-state breach notification requirements for the states an
interview says a matter's affected consumers are in. The source JSON is a
deliberately incomplete, not-yet-attorney-verified dataset (see its own
_meta block for current coverage) — see data/sources/breach_notification_law.json
and BUILD_PLAN_PHASE6.md Phase 2 for the full attorney-verified backfill.

No docassemble.base.util import here on purpose, so this module can be
unit-tested with plain python3.
"""

import json
import os

_SOURCE = os.path.join(
    os.path.dirname(__file__), 'data', 'sources', 'breach_notification_law.json'
)

_cache = None


def _load():
    global _cache
    if _cache is None:
        with open(_SOURCE, encoding='utf-8') as f:
            _cache = json.load(f)
    return _cache


def get_breach_requirements(state_codes):
    """
    Returns a list of breach-notification-requirement dicts for each
    two-letter state code in state_codes that has a stubbed/sourced entry.
    States without an entry are silently omitted — the caller is expected
    to note (per the template README) that coverage is partial until
    Phase 5.
    """
    data = _load()
    return [data[s] for s in state_codes if s in data]
