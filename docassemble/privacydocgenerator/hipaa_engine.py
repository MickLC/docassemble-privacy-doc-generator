"""
hipaa_engine.py

HIPAA applicability test. Unlike jurisdiction_engine.py's four detectors
(revenue/consumer-volume thresholds against an operational footprint),
HIPAA status turns on entity type, not scale — so it's a separate module,
separate gate (matters[i].hipaa.status), and deliberately not folded into
confirmed_jurisdictions (see BUILD_PLAN.md Phase 4).

No docassemble.base.util import here on purpose, so this module can be
unit-tested with plain python3.
"""


def detect_hipaa_status(
    is_health_plan,
    is_healthcare_provider_conducting_transactions,
    is_healthcare_clearinghouse,
    handles_phi_for_covered_entity,
):
    """
    Returns 'covered_entity', 'business_associate', or 'none'.

    A health plan, a healthcare provider that conducts HIPAA-covered
    electronic transactions, or a healthcare clearinghouse is a covered
    entity (45 CFR 160.103) regardless of any other answer. Absent that,
    an entity that creates/receives/maintains/transmits PHI on behalf of
    a covered entity is a business associate. Otherwise HIPAA does not
    apply.
    """
    if is_health_plan or is_healthcare_provider_conducting_transactions or is_healthcare_clearinghouse:
        return 'covered_entity'
    if handles_phi_for_covered_entity:
        return 'business_associate'
    return 'none'
