"""
content_library.py

Loads the drafted clause-content reference libraries from data/sources/
and exposes them as plain functions, so jurisdiction logic.yml files and
document templates can pull real clause text instead of just booleans.

No docassemble.base.util import here on purpose, so this module can be
unit-tested with plain python3 (see the four *_clauses.json files it reads).
"""

import json
import os

_SOURCES_DIR = os.path.join(os.path.dirname(__file__), 'data', 'sources')

_cache = {}


def _load(filename):
    if filename not in _cache:
        with open(os.path.join(_SOURCES_DIR, filename), encoding='utf-8') as f:
            _cache[filename] = json.load(f)
    return _cache[filename]


def gdpr_data_subject_rights():
    return _load('gdpr_clauses.json')['data_subject_rights']


def gdpr_transfer_mechanisms():
    return _load('gdpr_clauses.json')['international_transfer_mechanisms']


def ccpa_consumer_rights():
    return _load('ccpa_cpra_clauses.json')['consumer_rights']


def ccpa_sensitive_pi_categories():
    return _load('ccpa_cpra_clauses.json')['sensitive_pi_categories']


def tdpsa_consumer_rights():
    return _load('tdpsa_clauses.json')['consumer_rights']


def tdpsa_sensitive_data_categories():
    return _load('tdpsa_clauses.json')['sensitive_data_categories']


def vcdpa_consumer_rights():
    return _load('vcdpa_clauses.json')['consumer_rights']


def vcdpa_sensitive_data_categories():
    return _load('vcdpa_clauses.json')['sensitive_data_categories']


def state_privacy_consumer_rights(code):
    return _load('state_privacy_clauses.json')[code]['consumer_rights']


def state_privacy_sensitive_data_categories(code):
    return _load('state_privacy_clauses.json')[code]['sensitive_data_categories']
