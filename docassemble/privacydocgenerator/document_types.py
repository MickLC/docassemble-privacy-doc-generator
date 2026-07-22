"""
document_types.py

Registry of generated document types. Each entry describes what a document
is, which template it uses, which attachment variable holds the assembled
file, and when it applies to a given matter.

Adding a new document type later = one template file, one entry here, one
`attachment:` block with a matching `variable name:`, and one line in the
`if document_applies(...)` chain in documents/document_list.yml.

No docassemble.base.util import here on purpose, so DOCUMENT_TYPES and
document_applies() can be unit-tested with plain python3 against a fixture
object standing in for `matters[i]`.

Registered incrementally as the underlying data exists (see the project's
phased build plan): 'privacy_statement' and 'gap_analysis_memo' went live in
Phase 1; 'internal_privacy_policy' and 'ropa' in Phase 2; 'dpia_report' and
'lia_report' in Phase 3; 'hipaa_npp' in Phase 4.
"""

# Each 'applies' value must be a named module-level function, not a lambda:
# `modules:` blocks import this module's globals into the interview
# namespace, and docassemble pickles that namespace between requests. Pickle
# can only serialize a function by looking it up by name in its module, and
# an anonymous lambda has no such name, so a lambda here breaks session save.


def _applies_privacy_statement(m):
    # Every matter gets a website Privacy Statement, same as the internal
    # policy and ROPA below -- there's no real "no privacy law applies to
    # our website at all" case, and privacy_statement.docx wraps each
    # jurisdiction's section individually so a matter with zero confirmed
    # jurisdictions still renders a valid baseline statement (org info,
    # generic intro, no jurisdiction-specific sections). Previously gated
    # on confirmed_jurisdictions being non-empty, which silently dropped
    # the document for matters under every threshold.
    return True


def _applies_gap_analysis_memo(m):
    return m.gap_analysis['counts']['total'] > 0


def _applies_internal_privacy_policy(m):
    return True


def _applies_ropa(m):
    # RoPA is generated for every matter as a recordkeeping best practice,
    # not only where GDPR Art. 30 makes it a legal requirement.
    return True


def _applies_dpia_report(m):
    return any(a.is_high_risk for a in m.processing_activities)


def _applies_lia_report(m):
    return (
        'GDPR' in m.confirmed_jurisdictions.true_values()
        and any(a.relies_on_legitimate_interest for a in m.processing_activities)
    )


def _applies_hipaa_npp(m):
    # Business-associate-only clients don't issue an NPP — only a covered
    # entity does.
    return m.hipaa.status == 'covered_entity'


DOCUMENT_TYPES = [
    {
        'key': 'privacy_statement',
        'label': 'Privacy Statement',
        'family': 'collateral',
        'template': 'privacy_statement.docx',
        'attachment_var': 'privacy_statement_doc',
        'applies': _applies_privacy_statement,
    },
    {
        'key': 'gap_analysis_memo',
        'label': 'Gap Analysis Memo',
        'family': 'internal',
        'template': 'gap_analysis_memo.docx',
        'attachment_var': 'gap_analysis_memo_doc',
        'applies': _applies_gap_analysis_memo,
    },
    {
        'key': 'internal_privacy_policy',
        'label': 'Internal Privacy Policy',
        'family': 'internal',
        'template': 'internal_privacy_policy.docx',
        'attachment_var': 'internal_privacy_policy_doc',
        'applies': _applies_internal_privacy_policy,
    },
    {
        'key': 'ropa',
        'label': 'Record of Processing Activities (ROPA)',
        'family': 'internal',
        'template': 'ropa.docx',
        'attachment_var': 'ropa_doc',
        'applies': _applies_ropa,
    },
    {
        'key': 'dpia_report',
        'label': 'DPIA Report',
        'family': 'internal',
        'template': 'dpia_report.docx',
        'attachment_var': 'dpia_report_doc',
        'applies': _applies_dpia_report,
    },
    {
        'key': 'lia_report',
        'label': 'LIA Report',
        'family': 'internal',
        'template': 'lia_report.docx',
        'attachment_var': 'lia_report_doc',
        'applies': _applies_lia_report,
    },
    {
        'key': 'hipaa_npp',
        'label': 'HIPAA Notice of Privacy Practices',
        'family': 'collateral',
        'template': 'hipaa_npp.docx',
        'attachment_var': 'hipaa_npp_doc',
        'applies': _applies_hipaa_npp,
    },
]


def document_applies(key, matter):
    for dt in DOCUMENT_TYPES:
        if dt['key'] == key:
            return dt['applies'](matter)
    raise KeyError('Unknown document type: {}'.format(key))
