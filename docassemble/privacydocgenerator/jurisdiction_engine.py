"""
jurisdiction_engine.py

Core logic for auto-detecting applicable privacy laws based on
a client organisation's operational footprint.

Supported jurisdictions:
  - GDPR (EU & UK)
  - CCPA/CPRA (California)
  - TDPSA (Texas)
  - VCDPA (Virginia)

Each detect_* function returns a dict:
  {'name': str, 'applies': bool, 'reason': str}
"""

from docassemble.base.util import log


# -----------------------------------------------
# Threshold constants
# -----------------------------------------------
CCPA_REVENUE_THRESHOLD = 25_000_000        # $25M annual gross revenue
CCPA_CONSUMER_THRESHOLD = 100_000          # 100,000 consumers/households
CCPA_REVENUE_SHARE_THRESHOLD = 0.50        # 50% of revenue from PI sale

TDPSA_CONSUMER_THRESHOLD = 100_000         # 100,000 Texas consumers

VCDPA_CONSUMER_THRESHOLD = 100_000         # 100,000 Virginia consumers
VCDPA_REVENUE_SHARE_THRESHOLD = 25_000     # 25,000 consumers + 50% revenue


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
        return {'name': 'GDPR', 'applies': True, 'reason': reason}

    if targets_eu_uk:
        reason = (
            'Client processes personal data of residents in '
            + ', '.join(eu_uk & set(consumer_regions.true_values()))
            + '.'
        )
        return {'name': 'GDPR', 'applies': True, 'reason': reason}

    return {
        'name': 'GDPR',
        'applies': False,
        'reason': 'No EU/UK establishment or consumer base detected.'
    }


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
        return {
            'name': 'CCPA/CPRA',
            'applies': False,
            'reason': 'No California operations or consumer base detected.'
        }

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
        return {
            'name': 'CCPA/CPRA',
            'applies': True,
            'reason': ' '.join(reasons)
        }

    return {
        'name': 'CCPA/CPRA',
        'applies': False,
        'reason': (
            'Client operates in California but does not appear to meet '
            'revenue or volume thresholds. Verify manually.'
        )
    }


def detect_tdpsa(operating_regions, consumer_regions,
                 consumer_volume, is_sba_small_business):
    """
    TDPSA applies to entities doing business in Texas or targeting Texas
    residents, processing 100,000+ consumers, excluding SBA small businesses.
    """
    operates_in_tx = 'Texas (US)' in operating_regions.true_values()
    consumers_in_tx = 'Texas (US)' in consumer_regions.true_values()

    if not (operates_in_tx or consumers_in_tx):
        return {
            'name': 'TDPSA',
            'applies': False,
            'reason': 'No Texas operations or consumer base detected.'
        }

    if is_sba_small_business:
        return {
            'name': 'TDPSA',
            'applies': False,
            'reason': (
                'Client qualifies as SBA small business and is '
                'exempt from TDPSA. Verify classification.'
            )
        }

    if consumer_volume and consumer_volume >= TDPSA_CONSUMER_THRESHOLD:
        return {
            'name': 'TDPSA',
            'applies': True,
            'reason': (
                f'Client processes data of {consumer_volume:,} consumers '
                f'(threshold: {TDPSA_CONSUMER_THRESHOLD:,}) and '
                f'operates in or targets Texas.'
            )
        }

    return {
        'name': 'TDPSA',
        'applies': False,
        'reason': (
            'Client operates in Texas but consumer volume does not '
            'appear to meet the 100,000 threshold. Verify manually.'
        )
    }


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
        return {
            'name': 'VCDPA',
            'applies': False,
            'reason': 'No Virginia operations or consumer base detected.'
        }

    if consumer_volume and consumer_volume >= VCDPA_CONSUMER_THRESHOLD:
        return {
            'name': 'VCDPA',
            'applies': True,
            'reason': (
                f'Client processes data of {consumer_volume:,} consumers '
                f'(threshold: {VCDPA_CONSUMER_THRESHOLD:,}) and '
                f'operates in or targets Virginia.'
            )
        }

    if consumer_volume and consumer_volume >= VCDPA_REVENUE_SHARE_THRESHOLD and sells_data:
        return {
            'name': 'VCDPA',
            'applies': True,
            'reason': (
                f'Client processes data of {consumer_volume:,} Virginia consumers '
                f'and derives revenue from sale of personal data.'
            )
        }

    return {
        'name': 'VCDPA',
        'applies': False,
        'reason': (
            'Client operates in Virginia but does not appear to meet '
            'consumer volume thresholds. Verify manually.'
        )
    }


# -----------------------------------------------
# Master detection function (called from YAML)
# -----------------------------------------------

def detect_applicable_jurisdictions(
    operating_regions,
    consumer_regions,
    annual_revenue,
    consumer_volume,
    sells_data,
    is_sba_small_business
):
    """
    Runs all jurisdiction detectors and returns a list of
    applicable jurisdiction dicts for display in the interview.

    Returns only jurisdictions where applies=True.
    Also returns close calls (applies=False) for attorney awareness.
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
    ]

    # Return all results so the interview can display both
    # confirmed applicability and notable non-detections
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
