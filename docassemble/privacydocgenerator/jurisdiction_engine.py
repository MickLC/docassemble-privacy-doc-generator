"""
jurisdiction_engine.py

Core logic for auto-detecting applicable privacy laws based on
a client organisation's operational footprint.

Supported jurisdictions:
  - GDPR (EU & UK)
  - CCPA/CPRA (California)
  - TDPSA (Texas)
  - VCDPA (Virginia)
  - Colorado Privacy Act (CO)
  - Connecticut Data Privacy Act (CT)
  - Delaware Personal Data Privacy Act (DE)
  - Iowa Consumer Data Protection Act (IA)
  - Indiana Consumer Data Protection Act (IN)
  - Kentucky Consumer Data Protection Act (KY)
  - Maryland Online Data Privacy Act (MD)
  - Minnesota Consumer Data Privacy Act (MN)
  - Montana Consumer Data Privacy Act (MT)
  - Nebraska Data Privacy Act (NE)
  - New Hampshire Expectation of Privacy Act (NH)
  - New Jersey Data Privacy Act (NJ)
  - Oregon Consumer Privacy Act (OR)
  - Rhode Island Data Transparency and Privacy Protection Act (RI)
  - Tennessee Information Protection Act (TN)
  - Utah Consumer Privacy Act (UT)

Threshold and effective-date constants below are grounded in the actual
statute text queried from the Privacy skill's corpus
(`Projects/Privacy/privacy.sqlite`, or the same text as flat files under
`Projects/Privacy/corpus/us/states/<ST>/`; see that project's SKILL.md and
BUILD_PLAN_PHASE6.md Phase 3) — not general legal knowledge. None of these
detectors are attorney-verified; treat outputs as a first pass for
attorney review, not final applicability determinations.

Each detect_* function returns a dict:
  {'name': str, 'applies': bool, 'reason': str,
   'effective_date': 'YYYY-MM-DD', 'in_effect': bool}

`in_effect` is computed against the current date at call time, so a
detector for an enacted-but-not-yet-effective law will correctly flip to
True once its effective date passes without any code changes.
"""

from datetime import date

from docassemble.base.util import log


# -----------------------------------------------
# Effective dates (grounded in statute text — see module docstring)
# -----------------------------------------------
EFFECTIVE_DATES = {
    'GDPR': date(2018, 5, 25),        # GDPR Art. 99
    'CCPA/CPRA': date(2023, 1, 1),    # CPRA amendments operative (Prop 24 Sec. 31)
    'TDPSA': date(2024, 7, 1),        # Tex. Bus. & Com. Code ch. 541
    'VCDPA': date(2023, 1, 1),        # Va. Code § 59.1-575 et seq.
    'Colorado Privacy Act': date(2023, 7, 1),
    'Connecticut Data Privacy Act': date(2023, 7, 1),
    'Delaware Personal Data Privacy Act': date(2025, 1, 1),
    'Iowa Consumer Data Protection Act': date(2025, 1, 1),
    'Indiana Consumer Data Protection Act': date(2026, 1, 1),
    'Kentucky Consumer Data Protection Act': date(2026, 1, 1),
    'Maryland Online Data Privacy Act': date(2025, 10, 1),
    'Minnesota Consumer Data Privacy Act': date(2025, 7, 31),
    'Montana Consumer Data Privacy Act': date(2023, 10, 1),
    'Nebraska Data Privacy Act': date(2025, 1, 1),
    'New Hampshire Expectation of Privacy Act': date(2025, 1, 1),
    'New Jersey Data Privacy Act': date(2025, 1, 15),
    'Oregon Consumer Privacy Act': date(2024, 7, 1),
    'Rhode Island Data Transparency and Privacy Protection Act': date(2026, 1, 1),
    'Tennessee Information Protection Act': date(2025, 7, 1),
    'Utah Consumer Privacy Act': date(2023, 12, 31),
}


def _finalize(name, applies, reason):
    """Attach effective_date/in_effect to a detector result."""
    effective_date = EFFECTIVE_DATES[name]
    return {
        'name': name,
        'applies': applies,
        'reason': reason,
        'effective_date': effective_date.isoformat(),
        'in_effect': effective_date <= date.today(),
    }


# -----------------------------------------------
# Threshold constants
# -----------------------------------------------
CCPA_REVENUE_THRESHOLD = 25_000_000        # $25M annual gross revenue
CCPA_CONSUMER_THRESHOLD = 100_000          # 100,000 consumers/households
CCPA_REVENUE_SHARE_THRESHOLD = 0.50        # 50% of revenue from PI sale

TDPSA_CONSUMER_THRESHOLD = 100_000         # 100,000 Texas consumers

VCDPA_CONSUMER_THRESHOLD = 100_000         # 100,000 Virginia consumers
VCDPA_REVENUE_SHARE_THRESHOLD = 25_000     # 25,000 consumers + 50% revenue

TN_UT_REVENUE_FLOOR = 25_000_000           # TN/UT conjunctive $25M revenue gate


# -----------------------------------------------
# Individual jurisdiction detectors
# -----------------------------------------------

def detect_gdpr(operating_regions, consumer_regions):
    """
    GDPR applies if the organisation:
    - Has an establishment in the EU or UK, OR
    - Offers goods/services to EU/UK residents, OR
    - Monitors the behaviour of EU/UK residents
    """
    eu_uk = {'European Union (EU)', 'United Kingdom (UK)'}

    has_establishment = bool(eu_uk & set(operating_regions.true_values()))
    targets_eu_uk = bool(eu_uk & set(consumer_regions.true_values()))

    if has_establishment:
        reason = (
            'Client has an establishment in '
            + ', '.join(eu_uk & set(operating_regions.true_values()))
            + '.'
        )
        return _finalize('GDPR', True, reason)

    if targets_eu_uk:
        reason = (
            'Client processes personal data of residents in '
            + ', '.join(eu_uk & set(consumer_regions.true_values()))
            + '.'
        )
        return _finalize('GDPR', True, reason)

    return _finalize(
        'GDPR', False,
        'No EU/UK establishment or consumer base detected.'
    )


def detect_ccpa_cpra(operating_regions, consumer_regions,
                     annual_revenue, consumer_volume,
                     sells_data):
    """
    CCPA/CPRA applies to for-profit businesses doing business in California
    that meet at least one of three thresholds.
    """
    operates_in_ca = 'California (US)' in operating_regions.true_values()
    consumers_in_ca = 'California (US)' in consumer_regions.true_values()

    if not (operates_in_ca or consumers_in_ca):
        return _finalize(
            'CCPA/CPRA', False,
            'No California operations or consumer base detected.'
        )

    reasons = []

    if annual_revenue and annual_revenue >= CCPA_REVENUE_THRESHOLD:
        reasons.append(
            f'Annual revenue (${annual_revenue:,.0f}) meets or exceeds '
            f'${CCPA_REVENUE_THRESHOLD:,.0f} threshold.'
        )

    if consumer_volume and consumer_volume >= CCPA_CONSUMER_THRESHOLD:
        reasons.append(
            f'Consumer volume ({consumer_volume:,}) meets or exceeds '
            f'{CCPA_CONSUMER_THRESHOLD:,} threshold.'
        )

    if sells_data:
        reasons.append(
            'Client derives revenue from selling personal information.'
        )

    if reasons:
        return _finalize('CCPA/CPRA', True, ' '.join(reasons))

    return _finalize(
        'CCPA/CPRA', False,
        'Client operates in California but does not appear to meet '
        'revenue or volume thresholds. Verify manually.'
    )


def detect_tdpsa(operating_regions, consumer_regions,
                 consumer_volume, is_sba_small_business):
    """
    TDPSA applies to entities doing business in Texas or targeting Texas
    residents, processing 100,000+ consumers, excluding SBA small businesses.
    """
    operates_in_tx = 'Texas (US)' in operating_regions.true_values()
    consumers_in_tx = 'Texas (US)' in consumer_regions.true_values()

    if not (operates_in_tx or consumers_in_tx):
        return _finalize(
            'TDPSA', False,
            'No Texas operations or consumer base detected.'
        )

    if is_sba_small_business:
        return _finalize(
            'TDPSA', False,
            'Client qualifies as SBA small business and is '
            'exempt from TDPSA. Verify classification.'
        )

    if consumer_volume and consumer_volume >= TDPSA_CONSUMER_THRESHOLD:
        return _finalize(
            'TDPSA', True,
            f'Client processes data of {consumer_volume:,} consumers '
            f'(threshold: {TDPSA_CONSUMER_THRESHOLD:,}) and '
            f'operates in or targets Texas.'
        )

    return _finalize(
        'TDPSA', False,
        'Client operates in Texas but consumer volume does not '
        'appear to meet the 100,000 threshold. Verify manually.'
    )


def detect_vcdpa(operating_regions, consumer_regions,
                 consumer_volume, sells_data):
    """
    VCDPA applies if the entity controls/processes data of:
    - 100,000+ Virginia consumers, OR
    - 25,000+ Virginia consumers AND derives 50%+ revenue from PI sale
    """
    operates_in_va = 'Virginia (US)' in operating_regions.true_values()
    consumers_in_va = 'Virginia (US)' in consumer_regions.true_values()

    if not (operates_in_va or consumers_in_va):
        return _finalize(
            'VCDPA', False,
            'No Virginia operations or consumer base detected.'
        )

    if consumer_volume and consumer_volume >= VCDPA_CONSUMER_THRESHOLD:
        return _finalize(
            'VCDPA', True,
            f'Client processes data of {consumer_volume:,} consumers '
            f'(threshold: {VCDPA_CONSUMER_THRESHOLD:,}) and '
            f'operates in or targets Virginia.'
        )

    if consumer_volume and consumer_volume >= VCDPA_REVENUE_SHARE_THRESHOLD and sells_data:
        return _finalize(
            'VCDPA', True,
            f'Client processes data of {consumer_volume:,} Virginia consumers '
            f'and derives revenue from sale of personal data.'
        )

    return _finalize(
        'VCDPA', False,
        'Client operates in Virginia but does not appear to meet '
        'consumer volume thresholds. Verify manually.'
    )


def _standard_two_prong_detector(name, state_label, statute_note,
                                 operating_regions, consumer_regions,
                                 consumer_volume, sells_data,
                                 upper_threshold, lower_threshold):
    """
    Shared logic for the common "X,000+ consumers OR Y,000+ consumers AND
    sells/shares personal data" applicability pattern used by most of the
    Tier-1 states' comprehensive privacy acts. `sells_data` approximates
    each state's revenue-share-from-sale prong the same way the existing
    VCDPA detector does — the interview doesn't collect an exact revenue
    percentage, only a sells-data yes/no.
    """
    operates = state_label in operating_regions.true_values()
    has_consumers = state_label in consumer_regions.true_values()

    if not (operates or has_consumers):
        return _finalize(
            name, False,
            f'No {state_label} operations or consumer base detected.'
        )

    if consumer_volume and consumer_volume >= upper_threshold:
        return _finalize(
            name, True,
            f'Client processes data of {consumer_volume:,} consumers '
            f'(threshold: {upper_threshold:,}) and operates in or '
            f'targets {state_label}. {statute_note}'
        )

    if consumer_volume and consumer_volume >= lower_threshold and sells_data:
        return _finalize(
            name, True,
            f'Client processes data of {consumer_volume:,} {state_label} '
            f'consumers (threshold: {lower_threshold:,}) and derives '
            f'revenue from sale of personal data. {statute_note}'
        )

    return _finalize(
        name, False,
        f'Client operates in {state_label} but does not appear to meet '
        f'consumer volume thresholds. Verify manually. {statute_note}'
    )


def detect_co(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    Colorado Privacy Act, Colo. Rev. Stat. § 6-1-1301 et seq.
    Applies to 100,000+ CO consumers/year, OR 25,000+ consumers where the
    controller derives revenue or a discount from the sale of personal
    data (§ 6-1-1304(1)) — no revenue-percentage figure, unlike VCDPA.
    No general nonprofit or small-business exemption. A third trigger
    (any amount of biometric data, eff. 2025-07-01) is not modeled here —
    the interview has no granular biometric-only data field — flag for
    attorney awareness on biometric-heavy clients.
    """
    return _standard_two_prong_detector(
        'Colorado Privacy Act', 'Colorado (US)',
        'No general nonprofit or small-business exemption under CPA.',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=100_000, lower_threshold=25_000,
    )


def detect_ct(operating_regions, consumer_regions, consumer_volume,
             sells_data, processes_sensitive_data):
    """
    Connecticut Data Privacy Act, Conn. Gen. Stat. § 42-515 et seq.
    Original (2023-07-01) thresholds were 100,000+/25,000+ consumers.
    As amended by P.A. 25-113 (eff. 2026-07-01, already in force), the
    threshold test changed to: 35,000+ consumers, OR processing any
    amount of sensitive data, OR offering personal data for sale — no
    revenue-percentage figure remains. Uses the amended (current) test.
    """
    operates = 'Connecticut (US)' in operating_regions.true_values()
    has_consumers = 'Connecticut (US)' in consumer_regions.true_values()

    if not (operates or has_consumers):
        return _finalize(
            'Connecticut Data Privacy Act', False,
            'No Connecticut operations or consumer base detected.'
        )

    if consumer_volume and consumer_volume >= 35_000:
        return _finalize(
            'Connecticut Data Privacy Act', True,
            f'Client processes data of {consumer_volume:,} consumers '
            f'(threshold: 35,000) and operates in or targets Connecticut.'
        )

    if processes_sensitive_data:
        return _finalize(
            'Connecticut Data Privacy Act', True,
            'Client processes sensitive data of Connecticut residents, '
            'which independently triggers CTDPA applicability under the '
            'P.A. 25-113 amendment (no consumer-count floor for this prong).'
        )

    if sells_data:
        return _finalize(
            'Connecticut Data Privacy Act', True,
            'Client offers Connecticut residents\' personal data for sale, '
            'which independently triggers CTDPA applicability under the '
            'P.A. 25-113 amendment (no consumer-count floor for this prong).'
        )

    return _finalize(
        'Connecticut Data Privacy Act', False,
        'Client operates in Connecticut but does not appear to meet the '
        '35,000-consumer threshold or trigger the sensitive-data/sale '
        'prongs. Verify manually.'
    )


def detect_de(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    Delaware Personal Data Privacy Act, Del. Code tit. 6, § 12D-101 et seq.
    Applies to 35,000+ DE consumers, OR 10,000+ consumers AND >20% gross
    revenue from sale of personal data (§ 12D-103(a)).
    """
    return _standard_two_prong_detector(
        'Delaware Personal Data Privacy Act', 'Delaware (US)',
        '',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=35_000, lower_threshold=10_000,
    )


def detect_ia(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    Iowa Consumer Data Protection Act, Iowa Code ch. 715D.
    Applies to 100,000+ IA consumers, OR 25,000+ consumers AND >50% gross
    revenue from sale of personal data (§ 715D.2(1)) — matches VCDPA's
    structure exactly.
    """
    return _standard_two_prong_detector(
        'Iowa Consumer Data Protection Act', 'Iowa (US)',
        '',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=100_000, lower_threshold=25_000,
    )


def detect_in(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    Indiana Consumer Data Protection Act, Ind. Code § 24-15-1-1 et seq.
    Applies to 100,000+ IN consumers, OR 25,000+ consumers AND >50% gross
    revenue from sale of personal data.
    """
    return _standard_two_prong_detector(
        'Indiana Consumer Data Protection Act', 'Indiana (US)',
        '',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=100_000, lower_threshold=25_000,
    )


def detect_ky(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    Kentucky Consumer Data Protection Act, KRS 367.3611-367.3629.
    Applies to 100,000+ KY consumers, OR 25,000+ consumers AND >50% gross
    revenue from sale of personal data (KRS 367.3613(1)).
    """
    return _standard_two_prong_detector(
        'Kentucky Consumer Data Protection Act', 'Kentucky (US)',
        '',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=100_000, lower_threshold=25_000,
    )


def detect_md(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    Maryland Online Data Privacy Act, Md. Code Com. Law § 14-4701 et seq.
    Applies to 35,000+ MD consumers, OR 10,000+ consumers AND >20% gross
    revenue from sale of personal data (§ 14-4702) — notably lower
    thresholds than the 100,000/50% pattern, and no blanket nonprofit or
    higher-ed exemption unlike most Tier-1 states.
    """
    return _standard_two_prong_detector(
        'Maryland Online Data Privacy Act', 'Maryland (US)',
        'No general nonprofit or higher-education exemption under MODPA.',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=35_000, lower_threshold=10_000,
    )


def detect_mn(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    Minnesota Consumer Data Privacy Act, Minn. Stat. §§ 325M.10-325M.21.
    Applies to 100,000+ MN consumers, OR 25,000+ consumers AND >25% gross
    revenue from sale of personal data (§ 325M.12, subd. 1(a)) — 25%
    threshold, not the more common 50%. Postsecondary institutions have a
    delayed compliance date (2029-07-31) not modeled here.
    """
    return _standard_two_prong_detector(
        'Minnesota Consumer Data Privacy Act', 'Minnesota (US)',
        '',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=100_000, lower_threshold=25_000,
    )


def detect_mt(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    Montana Consumer Data Privacy Act, Mont. Code Ann. § 30-14-2801 et seq.
    As amended by 2025 Mont. Laws ch. 567 (eff. 2025-10-01, already in
    force): 25,000+ MT consumers, OR 15,000+ consumers AND >25% gross
    revenue from sale of personal data — lowered from the original 2023
    thresholds of 50,000/25,000+50%. Uses the amended (current) test.
    """
    return _standard_two_prong_detector(
        'Montana Consumer Data Privacy Act', 'Montana (US)',
        '',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=25_000, lower_threshold=15_000,
    )


def detect_ne(operating_regions, consumer_regions, sells_data,
             is_sba_small_business):
    """
    Nebraska Data Privacy Act, Neb. Rev. Stat. §§ 87-1101 to 87-1130.
    No numeric consumer-count or revenue threshold at all (§ 87-1103(1)) —
    applies to any entity doing business in or targeting Nebraska that
    processes or sells personal data and is NOT an SBA small business.
    Structurally different from every other detector in this module.
    """
    operates = 'Nebraska (US)' in operating_regions.true_values()
    has_consumers = 'Nebraska (US)' in consumer_regions.true_values()

    if not (operates or has_consumers):
        return _finalize(
            'Nebraska Data Privacy Act', False,
            'No Nebraska operations or consumer base detected.'
        )

    if is_sba_small_business:
        return _finalize(
            'Nebraska Data Privacy Act', False,
            'Client qualifies as an SBA small business and is exempt from '
            'the Nebraska Data Privacy Act, which has no numeric consumer '
            'threshold otherwise. Verify classification.'
        )

    return _finalize(
        'Nebraska Data Privacy Act', True,
        'Client operates in or targets Nebraska, processes or sells '
        'personal data, and does not qualify as an SBA small business. '
        'The NDPA has no numeric consumer-count threshold.'
    )


def detect_nh(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    New Hampshire Expectation of Privacy Act, RSA ch. 507-H.
    Applies to 35,000+ NH consumers, OR 10,000+ consumers AND >25% gross
    revenue from sale of personal data (§ 507-H:2(I)).
    """
    return _standard_two_prong_detector(
        'New Hampshire Expectation of Privacy Act', 'New Hampshire (US)',
        '',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=35_000, lower_threshold=10_000,
    )


def detect_nj(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    New Jersey Data Privacy Act, P.L. 2023, c.266.
    Applies to 100,000+ NJ consumers, OR 25,000+ consumers where the
    controller derives revenue or a discount from the sale of personal
    data (C.56:8-166.5) — no revenue-percentage figure, unlike VCDPA. No
    general nonprofit or higher-education exemption.
    """
    return _standard_two_prong_detector(
        'New Jersey Data Privacy Act', 'New Jersey (US)',
        'No general nonprofit or higher-education exemption under NJDPA.',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=100_000, lower_threshold=25_000,
    )


def detect_or(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    Oregon Consumer Privacy Act, Or. Rev. Stat. §§ 646A.570-646A.589.
    Applies to 100,000+ OR consumers, OR 25,000+ consumers AND >=25% gross
    revenue from sale of personal data (§ 646A.572(1)(a)). No general
    nonprofit exemption, unlike most Tier-1 states.
    """
    return _standard_two_prong_detector(
        'Oregon Consumer Privacy Act', 'Oregon (US)',
        'No general nonprofit exemption under OCPA.',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=100_000, lower_threshold=25_000,
    )


def detect_ri(operating_regions, consumer_regions, consumer_volume, sells_data):
    """
    Rhode Island Data Transparency and Privacy Protection Act,
    R.I. Gen. Laws §§ 6-48.1-1 to -10.
    Applies to for-profit entities only: 35,000+ RI customers, OR 10,000+
    customers AND >20% gross revenue from sale of personal data. The
    for-profit-entity limitation is not modeled here (no entity-type
    field in the interview) — flag for attorney verification on any
    nonprofit client.
    """
    return _standard_two_prong_detector(
        'Rhode Island Data Transparency and Privacy Protection Act',
        'Rhode Island (US)',
        'Applies to for-profit entities only — verify entity type.',
        operating_regions, consumer_regions, consumer_volume, sells_data,
        upper_threshold=35_000, lower_threshold=10_000,
    )


def detect_tn(operating_regions, consumer_regions, annual_revenue,
             consumer_volume, sells_data):
    """
    Tennessee Information Protection Act, Tenn. Code Ann. § 47-18-3201
    et seq. Unlike the standard pattern, TIPA requires a conjunctive
    $25M+ annual revenue floor (§ 47-18-3202) on top of EITHER
    (25,000+ consumers AND >50% revenue from sale) OR 175,000+ consumers
    alone. Has a nonprofit and higher-ed exemption (§ 47-18-3210(a)).
    """
    operates = 'Tennessee (US)' in operating_regions.true_values()
    has_consumers = 'Tennessee (US)' in consumer_regions.true_values()

    if not (operates or has_consumers):
        return _finalize(
            'Tennessee Information Protection Act', False,
            'No Tennessee operations or consumer base detected.'
        )

    if not (annual_revenue and annual_revenue >= TN_UT_REVENUE_FLOOR):
        return _finalize(
            'Tennessee Information Protection Act', False,
            f'Client operates in Tennessee but annual revenue does not '
            f'appear to meet the ${TN_UT_REVENUE_FLOOR:,.0f} threshold '
            f'TIPA requires regardless of consumer volume. Verify manually.'
        )

    if consumer_volume and consumer_volume >= 175_000:
        return _finalize(
            'Tennessee Information Protection Act', True,
            f'Client meets the ${TN_UT_REVENUE_FLOOR:,.0f}+ revenue floor '
            f'and processes data of {consumer_volume:,} consumers '
            f'(threshold: 175,000).'
        )

    if consumer_volume and consumer_volume >= 25_000 and sells_data:
        return _finalize(
            'Tennessee Information Protection Act', True,
            f'Client meets the ${TN_UT_REVENUE_FLOOR:,.0f}+ revenue floor, '
            f'processes data of {consumer_volume:,} consumers '
            f'(threshold: 25,000), and derives revenue from sale of '
            f'personal data.'
        )

    return _finalize(
        'Tennessee Information Protection Act', False,
        'Client meets the revenue floor but does not appear to meet '
        'either consumer-volume prong. Verify manually.'
    )


def detect_ut(operating_regions, consumer_regions, annual_revenue,
             consumer_volume, sells_data):
    """
    Utah Consumer Privacy Act, Utah Code §§ 13-61-101 to -404. Like TIPA,
    requires a conjunctive $25M+ annual revenue floor (§ 13-61-102(1)(b))
    on top of EITHER 100,000+ consumers OR (25,000+ consumers AND >50%
    revenue from sale).
    """
    operates = 'Utah (US)' in operating_regions.true_values()
    has_consumers = 'Utah (US)' in consumer_regions.true_values()

    if not (operates or has_consumers):
        return _finalize(
            'Utah Consumer Privacy Act', False,
            'No Utah operations or consumer base detected.'
        )

    if not (annual_revenue and annual_revenue >= TN_UT_REVENUE_FLOOR):
        return _finalize(
            'Utah Consumer Privacy Act', False,
            f'Client operates in Utah but annual revenue does not appear '
            f'to meet the ${TN_UT_REVENUE_FLOOR:,.0f} threshold UCPA '
            f'requires regardless of consumer volume. Verify manually.'
        )

    if consumer_volume and consumer_volume >= 100_000:
        return _finalize(
            'Utah Consumer Privacy Act', True,
            f'Client meets the ${TN_UT_REVENUE_FLOOR:,.0f}+ revenue floor '
            f'and processes data of {consumer_volume:,} consumers '
            f'(threshold: 100,000).'
        )

    if consumer_volume and consumer_volume >= 25_000 and sells_data:
        return _finalize(
            'Utah Consumer Privacy Act', True,
            f'Client meets the ${TN_UT_REVENUE_FLOOR:,.0f}+ revenue floor, '
            f'processes data of {consumer_volume:,} consumers '
            f'(threshold: 25,000), and derives revenue from sale of '
            f'personal data.'
        )

    return _finalize(
        'Utah Consumer Privacy Act', False,
        'Client meets the revenue floor but does not appear to meet '
        'either consumer-volume prong. Verify manually.'
    )


# -----------------------------------------------
# Master detection function (called from YAML)
# -----------------------------------------------

def detect_applicable_jurisdictions(
    operating_regions,
    consumer_regions,
    annual_revenue,
    consumer_volume,
    sells_data,
    is_sba_small_business,
    processes_sensitive_data=False
):
    """
    Runs all jurisdiction detectors and returns a list of
    applicable jurisdiction dicts for display in the interview.

    Returns all results, both applicable and non-applicable, so the
    interview can display confirmed applicability, notable non-detections,
    and (via `in_effect`) upcoming obligations for enacted-but-not-yet-
    effective laws.
    """
    results = [
        detect_gdpr(operating_regions, consumer_regions),
        detect_ccpa_cpra(
            operating_regions, consumer_regions,
            annual_revenue, consumer_volume, sells_data
        ),
        detect_tdpsa(
            operating_regions, consumer_regions,
            consumer_volume, is_sba_small_business
        ),
        detect_vcdpa(
            operating_regions, consumer_regions,
            consumer_volume, sells_data
        ),
        detect_co(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_ct(
            operating_regions, consumer_regions, consumer_volume,
            sells_data, processes_sensitive_data
        ),
        detect_de(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_ia(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_in(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_ky(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_md(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_mn(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_mt(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_ne(
            operating_regions, consumer_regions, sells_data,
            is_sba_small_business
        ),
        detect_nh(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_nj(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_or(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_ri(operating_regions, consumer_regions, consumer_volume, sells_data),
        detect_tn(
            operating_regions, consumer_regions, annual_revenue,
            consumer_volume, sells_data
        ),
        detect_ut(
            operating_regions, consumer_regions, annual_revenue,
            consumer_volume, sells_data
        ),
    ]

    return results


# -----------------------------------------------
# DPIA / PIA risk flag (universal helper)
# -----------------------------------------------

def requires_dpia(data_types_collected, data_purposes):
    """
    Flags whether a DPIA/PIA is likely required based on
    high-risk data types or processing purposes.
    """
    high_risk_data = [
        'Health or medical data',
        'Biometric data',
        'Precise geolocation data',
        'Data relating to children (under 13 / under 16)',
        'Racial or ethnic origin',
        'Criminal conviction data',
        'Genetic data',
    ]
    high_risk_purposes = [
        'Targeted or behavioural advertising',
        'Profiling with significant effects',
        'Sharing or selling to third parties',
    ]

    for item in high_risk_data:
        if data_types_collected.get(item):
            return True
    for purpose in high_risk_purposes:
        if data_purposes.get(purpose):
            return True
    return False
