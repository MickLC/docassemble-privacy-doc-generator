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

DOCUMENT_TYPES = [
    {
        'key': 'privacy_statement',
        'label': 'Privacy Statement',
        'family': 'collateral',
        'template': 'privacy_statement.docx',
        'attachment_var': 'privacy_statement_doc',
        'applies': lambda m: bool(m.confirmed_jurisdictions.true_values()),
    },
    {
        'key': 'gap_analysis_memo',
        'label': 'Gap Analysis Memo',
        'family': 'internal',
        'template': 'gap_analysis_memo.docx',
        'attachment_var': 'gap_analysis_memo_doc',
        'applies': lambda m: m.gap_analysis['counts']['total'] > 0,
    },
    {
        'key': 'internal_privacy_policy',
        'label': 'Internal Privacy Policy',
        'family': 'internal',
        'template': 'internal_privacy_policy.docx',
        'attachment_var': 'internal_privacy_policy_doc',
        'applies': lambda m: True,
    },
    {
        'key': 'ropa',
        'label': 'Record of Processing Activities (ROPA)',
        'family': 'internal',
        'template': 'ropa.docx',
        'attachment_var': 'ropa_doc',
        # Over-inclusive on purpose: generate whenever GDPR applies rather
        # than trying to detect the <250-employee Art. 30(5) exemption —
        # attorney judges that, same posture as the gap analysis engine.
        'applies': lambda m: 'GDPR' in m.confirmed_jurisdictions.true_values(),
    },
    {
        'key': 'dpia_report',
        'label': 'DPIA Report',
        'family': 'internal',
        'template': 'dpia_report.docx',
        'attachment_var': 'dpia_report_doc',
        'applies': lambda m: any(a.is_high_risk for a in m.processing_activities),
    },
    {
        'key': 'lia_report',
        'label': 'LIA Report',
        'family': 'internal',
        'template': 'lia_report.docx',
        'attachment_var': 'lia_report_doc',
        'applies': lambda m: (
            'GDPR' in m.confirmed_jurisdictions.true_values()
            and any(a.relies_on_legitimate_interest for a in m.processing_activities)
        ),
    },
    {
        'key': 'hipaa_npp',
        'label': 'HIPAA Notice of Privacy Practices',
        'family': 'collateral',
        'template': 'hipaa_npp.docx',
        'attachment_var': 'hipaa_npp_doc',
        # Business-associate-only clients don't issue an NPP — only a
        # covered entity does.
        'applies': lambda m: m.hipaa.status == 'covered_entity',
    },
]


def document_applies(key, matter):
    for dt in DOCUMENT_TYPES:
        if dt['key'] == key:
            return dt['applies'](matter)
    raise KeyError('Unknown document type: {}'.format(key))
