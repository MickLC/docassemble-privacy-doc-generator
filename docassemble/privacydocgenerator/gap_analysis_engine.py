"""
gap_analysis_engine.py

Produces structured gap analysis findings for each applicable
privacy jurisdiction based on compliance posture answers.

Severity ratings:
  MUST_FIX     - Statutory requirement; non-compliance creates direct legal exposure
  SHOULD_FIX   - Best practice or regulatory expectation; material risk if absent
  CONSIDER     - Recommended enhancement; lower risk if absent

Each finding is a dict:
  {
    'jurisdiction': str,
    'requirement':  str,   # Short name of the requirement
    'authority':    str,   # Statutory citation or regulatory reference
    'current_state': str,  # What the client has (or doesn't have) right now
    'gap':          str,   # Description of the gap
    'severity':     str,   # MUST_FIX | SHOULD_FIX | CONSIDER
  }

No remediation steps are included. The attorney adds those.
"""


# -----------------------------------------------
# Severity constants
# -----------------------------------------------
MUST_FIX = 'Must Fix'
SHOULD_FIX = 'Should Fix'
CONSIDER = 'Consider Fixing'


# -----------------------------------------------
# Helper
# -----------------------------------------------
def _gap(jurisdiction, requirement, authority, current_state, gap, severity):
    return {
        'jurisdiction': jurisdiction,
        'requirement': requirement,
        'authority': authority,
        'current_state': current_state,
        'gap': gap,
        'severity': severity,
    }


def _no_gap():
    """Sentinel — caller should not append this."""
    return None


# -----------------------------------------------
# GDPR Gap Analysis
# -----------------------------------------------
def analyse_gdpr_gaps(matter):
    """
    Evaluates GDPR compliance posture and returns a list
    of gap finding dicts.
    """
    findings = []
    p = matter.gdpr.posture
    g = matter.gdpr
    cs = matter.current_state
    J = 'GDPR'

    # --- Documentation ---

    if not p.lawful_basis_documented:
        findings.append(_gap(
            J,
            'Lawful Basis Documentation',
            'Article 6 GDPR',
            'No documented lawful basis for processing activities.',
            'The client has not documented the lawful basis relied upon for '
            'each category of processing activity. Controllers must be able '
            'to demonstrate compliance with Article 5(2) accountability principle.',
            MUST_FIX
        ))

    if not p.ropa_maintained:
        findings.append(_gap(
            J,
            'Record of Processing Activities (RoPA)',
            'Article 30 GDPR',
            'No RoPA maintained.',
            'The client does not maintain a Record of Processing Activities. '
            'This is a mandatory requirement for most controllers and processors.',
            MUST_FIX
        ))

    if not p.retention_schedule_documented:
        findings.append(_gap(
            J,
            'Data Retention Schedule',
            'Article 5(1)(e) GDPR (storage limitation)',
            'No documented data retention schedule.',
            'The client has no documented schedule defining how long personal '
            'data is retained and the criteria used to determine retention periods.',
            SHOULD_FIX
        ))

    if (g.lawful_bases.get('Legitimate interests (Article 6(1)(f))', False)
            and not p.lia_documented):
        findings.append(_gap(
            J,
            'Legitimate Interests Assessment (LIA)',
            'Article 6(1)(f) GDPR',
            'Legitimate interests relied upon but no LIA documented.',
            'Where legitimate interests is used as a lawful basis, a Legitimate '
            'Interests Assessment should be documented to demonstrate the '
            'balancing test has been performed.',
            CONSIDER
        ))

    # --- Notices and Consent ---

    if not p.privacy_notice_provided:
        findings.append(_gap(
            J,
            'Privacy Notice at Collection',
            'Articles 13 and 14 GDPR',
            'No privacy notice provided to data subjects at point of collection.',
            'The client does not currently provide a compliant privacy notice '
            'at or before the point of data collection as required by Articles 13/14.',
            MUST_FIX
        ))

    if not p.cookie_consent_compliant:
        findings.append(_gap(
            J,
            'Cookie Consent Mechanism',
            'ePrivacy Directive; GDPR Article 6',
            'Cookie consent mechanism absent or non-compliant.',
            'The client does not have a compliant cookie consent mechanism. '
            'Non-essential cookies require prior, freely given, specific, '
            'informed, and unambiguous consent.',
            SHOULD_FIX
        ))

    if (g.lawful_bases.get('Consent (Article 6(1)(a))', False)
            and not p.consent_records_maintained):
        findings.append(_gap(
            J,
            'Consent Records',
            'Article 7(1) GDPR',
            'Consent relied upon but no mechanism to record or evidence consent.',
            'Where consent is the lawful basis, the controller must be able to '
            'demonstrate that the data subject has consented. No consent '
            'recording mechanism is currently in place.',
            MUST_FIX
        ))

    # --- Rights and Contracts ---

    if not p.rights_procedure_documented:
        findings.append(_gap(
            J,
            'Data Subject Rights Procedure',
            'Articles 15–22 GDPR',
            'No documented procedure for handling data subject rights requests.',
            'The client has no documented procedure for receiving, verifying, '
            'and responding to data subject rights requests within the one-month '
            'statutory deadline.',
            MUST_FIX
        ))

    if not p.article28_contracts_in_place:
        findings.append(_gap(
            J,
            'Processor Contracts (Article 28 DPAs)',
            'Article 28 GDPR',
            'Article 28-compliant Data Processing Agreements not in place with all processors.',
            'The client does not have compliant Data Processing Agreements '
            'with all processors. This is a mandatory requirement wherever '
            'a processor handles personal data on the controller\'s behalf.',
            MUST_FIX
        ))

    if g.international_transfers and not p.transfer_mechanism_in_place:
        findings.append(_gap(
            J,
            'International Transfer Mechanism',
            'Articles 44–49 GDPR',
            'Personal data transferred outside UK/EEA without an adequate transfer mechanism.',
            'The client transfers personal data to third countries but does not '
            'have an appropriate transfer mechanism (adequacy decision, SCCs, BCRs, '
            'or IDTA) in place as required by Chapter V GDPR.',
            MUST_FIX
        ))

    # --- Security and Breach ---

    if not p.breach_procedure_documented:
        findings.append(_gap(
            J,
            'Data Breach Response Procedure',
            'Articles 33 and 34 GDPR',
            'No documented breach detection, assessment, and notification procedure.',
            'The client has no documented procedure for detecting, assessing, '
            'and notifying the supervisory authority (within 72 hours) and '
            'affected data subjects of personal data breaches.',
            MUST_FIX
        ))

    if g.requires_dpia and not p.dpia_conducted:
        findings.append(_gap(
            J,
            'Data Protection Impact Assessment (DPIA)',
            'Article 35 GDPR',
            'High-risk processing identified but no DPIA conducted.',
            'The client\'s processing activities indicate that a DPIA is likely '
            'required under Article 35, but none has been conducted. A DPIA is '
            'mandatory before commencing high-risk processing.',
            MUST_FIX
        ))

    if not p.privacy_by_design:
        findings.append(_gap(
            J,
            'Privacy by Design and Default',
            'Article 25 GDPR',
            'Privacy by design principles not embedded in new projects or systems.',
            'The client does not currently implement data protection by design '
            'and by default when developing new products, services, or systems.',
            SHOULD_FIX
        ))

    if not p.staff_training_current:
        findings.append(_gap(
            J,
            'Staff Data Protection Training',
            'Article 5(2) GDPR (accountability); Article 39(1)(b)',
            'Staff have not received data protection training in the last 12 months.',
            'No evidence of current staff data protection training. Regular '
            'training is a key element of the accountability principle and '
            'a DPO obligation where a DPO is appointed.',
            SHOULD_FIX
        ))

    return findings


# -----------------------------------------------
# CCPA/CPRA Gap Analysis
# -----------------------------------------------
def analyse_ccpa_gaps(matter):
    """
    Evaluates CCPA/CPRA compliance posture and returns gap findings.
    """
    findings = []
    p = matter.ccpa.posture
    c = matter.ccpa
    J = 'CCPA/CPRA'

    if not p.notice_at_collection:
        findings.append(_gap(
            J,
            'Notice at Collection',
            'Cal. Civ. Code §1798.100(a)',
            'No privacy notice at collection provided to California consumers.',
            'The client does not provide a notice at or before the point of '
            'collecting personal information disclosing the categories of PI '
            'collected and the purposes for which it is used.',
            MUST_FIX
        ))

    if not p.policy_updated_12mo:
        findings.append(_gap(
            J,
            'Privacy Policy Currency',
            'Cal. Civ. Code §1798.130(a)(5)',
            'Published privacy policy not updated within the last 12 months.',
            'Businesses subject to CCPA must update their privacy policy at '
            'least once every 12 months.',
            MUST_FIX
        ))

    if not p.policy_disclosures_complete:
        findings.append(_gap(
            J,
            'Required Privacy Policy Disclosures',
            'Cal. Civ. Code §1798.130(a)(5)',
            'Privacy policy does not include all required CCPA/CPRA disclosures.',
            'The client\'s current privacy policy is missing one or more of the '
            'disclosures required by CCPA/CPRA, including categories of PI '
            'collected, sources, purposes, third-party disclosures, and '
            'consumer rights.',
            MUST_FIX
        ))

    if c.sells_pi and not p.opt_out_mechanism_in_place:
        findings.append(_gap(
            J,
            '"Do Not Sell or Share" Opt-Out Mechanism',
            'Cal. Civ. Code §1798.120',
            'Client sells/shares PI but no opt-out mechanism is in place.',
            'The client sells or shares personal information but has not '
            'implemented a "Do Not Sell or Share My Personal Information" '
            'link or equivalent mechanism as required.',
            MUST_FIX
        ))

    if not p.gpc_honoured:
        findings.append(_gap(
            J,
            'Global Privacy Control (GPC) Signal',
            'CPPA Regulations §999.315(d)',
            'Global Privacy Control signal not honoured.',
            'The client does not automatically honour the Global Privacy Control '
            'opt-out signal. This is required under CPPA regulations for businesses '
            'subject to CCPA/CPRA.',
            MUST_FIX
        ))

    if c.uses_spi_beyond_primary and not p.spi_limit_mechanism_in_place:
        findings.append(_gap(
            J,
            '"Limit Use of Sensitive Personal Information" Mechanism',
            'Cal. Civ. Code §1798.121',
            'SPI used beyond primary purpose but no limit mechanism in place.',
            'The client uses sensitive personal information beyond what is '
            'necessary for the primary purpose but has not provided a mechanism '
            'for consumers to limit such use as required by §1798.121.',
            MUST_FIX
        ))

    if not p.rights_procedure_45_days:
        findings.append(_gap(
            J,
            'Consumer Rights Request Procedure (45-day)',
            'Cal. Civ. Code §1798.105, §1798.106',
            'No documented procedure to respond to consumer rights requests within 45 days.',
            'The client has no documented procedure for receiving and responding '
            'to consumer rights requests within the 45-day statutory deadline '
            '(extendable by an additional 45 days with notice).',
            MUST_FIX
        ))

    if not p.service_provider_contracts_compliant:
        findings.append(_gap(
            J,
            'Service Provider and Contractor Contracts',
            'Cal. Civ. Code §1798.140(ag)',
            'Service provider/contractor agreements do not include required CPRA provisions.',
            'Contracts with service providers, contractors, and third parties '
            'must include specific provisions required by CPRA. Current contracts '
            'do not meet these requirements.',
            MUST_FIX
        ))

    if not p.staff_trained:
        findings.append(_gap(
            J,
            'Staff Training on Consumer Rights',
            'Cal. Civ. Code §1798.135(a)(3)',
            'Staff who handle consumer rights requests have not been trained.',
            'Businesses must train all individuals responsible for handling '
            'consumer inquiries about CCPA/CPRA privacy practices.',
            SHOULD_FIX
        ))

    if not p.deletion_verification_in_place:
        findings.append(_gap(
            J,
            'Two-Step Verification for Deletion Requests',
            'CPPA Regulations §999.323',
            'No two-step verification process for deletion requests implemented.',
            'A two-step verification process for online deletion requests is '
            'recommended under CPPA regulations to reduce fraudulent requests.',
            SHOULD_FIX
        ))

    return findings


# -----------------------------------------------
# TDPSA Gap Analysis
# -----------------------------------------------
def analyse_tdpsa_gaps(matter):
    """
    Evaluates TDPSA compliance posture and returns gap findings.
    """
    findings = []
    p = matter.tdpsa.posture
    t = matter.tdpsa
    J = 'TDPSA'

    if not p.privacy_notice_provided:
        findings.append(_gap(
            J,
            'Privacy Notice',
            'Tex. Bus. & Com. Code §541.101',
            'No TDPSA-compliant privacy notice provided to Texas consumers.',
            'Controllers must provide consumers with a reasonably accessible, '
            'clear, and meaningful privacy notice covering required disclosures.',
            MUST_FIX
        ))

    if not p.rights_procedure_45_days:
        findings.append(_gap(
            J,
            'Consumer Rights Response Procedure (45-day)',
            'Tex. Bus. & Com. Code §541.052',
            'No documented procedure to respond to consumer requests within 45 days.',
            'Controllers must respond to authenticated consumer rights requests '
            'within 45 days, with a possible 45-day extension on notice.',
            MUST_FIX
        ))

    if not p.appeals_procedure:
        findings.append(_gap(
            J,
            'Consumer Appeals Procedure',
            'Tex. Bus. & Com. Code §541.053',
            'No appeals procedure in place for denied consumer requests.',
            'Controllers must establish an internal appeals process for '
            'consumers to appeal the denial of a rights request.',
            MUST_FIX
        ))

    if t.include_opt_out_section and not p.opt_out_mechanism_in_place:
        findings.append(_gap(
            J,
            'Opt-Out Mechanism for Targeted Advertising / Sale / Profiling',
            'Tex. Bus. & Com. Code §541.051',
            'No opt-out mechanism in place for applicable processing activities.',
            'The client engages in targeted advertising, sale of personal data, '
            'or profiling with significant effects but has not provided a clear '
            'mechanism for consumers to opt out.',
            MUST_FIX
        ))

    if not p.uoom_supported:
        findings.append(_gap(
            J,
            'Universal Opt-Out Mechanism (UOOM)',
            'Tex. Bus. & Com. Code §541.056',
            'Universal Opt-Out Mechanism not supported.',
            'Controllers must honour a universal opt-out mechanism recognised '
            'by the Texas Attorney General. The client does not currently '
            'support any such mechanism.',
            MUST_FIX
        ))

    if matter.footprint.processes_sensitive_data and not p.sensitive_data_consent_obtained:
        findings.append(_gap(
            J,
            'Sensitive Data Opt-In Consent',
            'Tex. Bus. & Com. Code §541.101(b)',
            'Sensitive data processed without opt-in consent mechanism.',
            'Processing of sensitive personal data requires the consumer\'s '
            'prior opt-in consent. No consent mechanism is currently in place.',
            MUST_FIX
        ))

    if not p.dpa_contracts_in_place:
        findings.append(_gap(
            J,
            'Data Processing Agreements with Processors',
            'Tex. Bus. & Com. Code §541.104',
            'Data Processing Agreements with processors not in place.',
            'Controllers must enter into binding contracts with processors '
            'that include required data protection provisions.',
            MUST_FIX
        ))

    if t.include_opt_out_section and not p.dpa_assessments_completed:
        findings.append(_gap(
            J,
            'Data Protection Assessments',
            'Tex. Bus. & Com. Code §541.105',
            'Data Protection Assessments not completed for high-risk processing.',
            'Controllers must conduct and document Data Protection Assessments '
            'before engaging in processing that presents a heightened risk of harm.',
            MUST_FIX
        ))

    return findings


# -----------------------------------------------
# VCDPA Gap Analysis
# -----------------------------------------------
def analyse_vcdpa_gaps(matter):
    """
    Evaluates VCDPA compliance posture and returns gap findings.
    """
    findings = []
    p = matter.vcdpa.posture
    v = matter.vcdpa
    J = 'VCDPA'

    if not p.privacy_notice_provided:
        findings.append(_gap(
            J,
            'Privacy Notice',
            'Va. Code Ann. §59.1-578(A)',
            'No VCDPA-compliant privacy notice provided to Virginia consumers.',
            'Controllers must provide consumers with a reasonably accessible '
            'privacy notice that includes all disclosures required by §59.1-578.',
            MUST_FIX
        ))

    if not p.rights_procedure_45_days:
        findings.append(_gap(
            J,
            'Consumer Rights Response Procedure (45-day)',
            'Va. Code Ann. §59.1-581(A)',
            'No documented procedure to respond to consumer requests within 45 days.',
            'Controllers must respond to authenticated consumer rights requests '
            'within 45 days. An additional 45-day extension is permitted with notice.',
            MUST_FIX
        ))

    if not p.appeals_procedure:
        findings.append(_gap(
            J,
            'Consumer Appeals Procedure',
            'Va. Code Ann. §59.1-581(C)',
            'No appeals procedure in place for denied consumer requests.',
            'Controllers must establish and make available an internal process '
            'for consumers to appeal the denial of any rights request.',
            MUST_FIX
        ))

    if v.include_opt_out_section and not p.opt_out_mechanism_in_place:
        findings.append(_gap(
            J,
            'Opt-Out Mechanism for Targeted Advertising / Sale / Profiling',
            'Va. Code Ann. §59.1-578(A)(5)',
            'No opt-out mechanism in place for applicable processing activities.',
            'The client engages in targeted advertising, sale of personal data, '
            'or profiling with significant effects but has not provided a '
            'mechanism for consumers to opt out.',
            MUST_FIX
        ))

    if v.processes_sensitive_data and not p.sensitive_data_consent_obtained:
        findings.append(_gap(
            J,
            'Sensitive Data Opt-In Consent',
            'Va. Code Ann. §59.1-578(B)',
            'Sensitive data processed without opt-in consent.',
            'Processing of sensitive data requires the consumer\'s prior, '
            'freely given, specific, and unambiguous opt-in consent. '
            'No such mechanism is currently in place.',
            MUST_FIX
        ))

    if not p.dpa_contracts_in_place:
        findings.append(_gap(
            J,
            'Data Processing Agreements with Processors',
            'Va. Code Ann. §59.1-580',
            'Data Processing Agreements with processors not in place.',
            'Controllers must enter into binding contracts with processors '
            'governing the processing of personal data and including all '
            'provisions required by §59.1-580.',
            MUST_FIX
        ))

    if v.include_opt_out_section and not p.pia_assessments_completed:
        findings.append(_gap(
            J,
            'Data Protection Impact Assessments (PIAs)',
            'Va. Code Ann. §59.1-582',
            'Data Protection Impact Assessments not completed for high-risk processing.',
            'Controllers must conduct and document Data Protection Impact '
            'Assessments for processing activities that present a heightened '
            'risk of harm to consumers.',
            MUST_FIX
        ))

    if not p.third_party_contracts_updated:
        findings.append(_gap(
            J,
            'Third-Party Contracts Updated for VCDPA',
            'Va. Code Ann. §59.1-580',
            'Contracts with third parties not reviewed or updated for VCDPA compliance.',
            'Existing contracts with third parties who receive personal data '
            'should be reviewed and updated to include VCDPA-required provisions.',
            SHOULD_FIX
        ))

    return findings


# -----------------------------------------------
# Master gap analysis function (called from YAML)
# -----------------------------------------------
def run_gap_analysis(matter):
    """
    Runs all applicable gap analysis functions for the matter
    and returns a consolidated findings structure:

    {
      'all': [list of all findings],
      'by_jurisdiction': { 'GDPR': [...], 'CCPA/CPRA': [...], ... },
      'by_severity': {
          'Must Fix': [...],
          'Should Fix': [...],
          'Consider Fixing': [...]
      },
      'counts': {
          'total': int,
          'must_fix': int,
          'should_fix': int,
          'consider': int
      }
    }
    """
    confirmed = matter.confirmed_jurisdictions.true_values()
    all_findings = []

    if 'GDPR' in confirmed:
        all_findings.extend(analyse_gdpr_gaps(matter))

    if 'CCPA/CPRA' in confirmed:
        all_findings.extend(analyse_ccpa_gaps(matter))

    if 'TDPSA' in confirmed:
        all_findings.extend(analyse_tdpsa_gaps(matter))

    if 'VCDPA' in confirmed:
        all_findings.extend(analyse_vcdpa_gaps(matter))

    by_jurisdiction = {}
    for f in all_findings:
        j = f['jurisdiction']
        by_jurisdiction.setdefault(j, []).append(f)

    by_severity = {
        MUST_FIX: [f for f in all_findings if f['severity'] == MUST_FIX],
        SHOULD_FIX: [f for f in all_findings if f['severity'] == SHOULD_FIX],
        CONSIDER: [f for f in all_findings if f['severity'] == CONSIDER],
    }

    counts = {
        'total': len(all_findings),
        'must_fix': len(by_severity[MUST_FIX]),
        'should_fix': len(by_severity[SHOULD_FIX]),
        'consider': len(by_severity[CONSIDER]),
    }

    return {
        'all': all_findings,
        'by_jurisdiction': by_jurisdiction,
        'by_severity': by_severity,
        'counts': counts,
    }
