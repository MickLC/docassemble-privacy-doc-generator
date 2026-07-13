"""
state_privacy_acts.py

Shared question/logic support for the "standard model" tier of state
comprehensive privacy acts identified in BUILD_PLAN_PHASE6.md Phase 3 step 4:
states whose rights/obligations track VCDPA's model closely enough to share
one generic-object question set (`data/questions/includes/state_privacy/`)
instead of a dedicated file per state. Genuinely divergent states (Maryland,
Minnesota, Connecticut, Iowa, Utah) get their own dedicated question/logic
files instead — see the build plan's per-state classification table for why.

Every citation and threshold note below is grounded in the actual statute
text on file under
`.claude/skills/Privacy/context/text/NAmerica/United States/States/<ST>/`
(Phase 3 step 4 extraction), not general legal knowledge. None of these
detectors or citations are attorney-verified; treat outputs as a first pass
for attorney review.

`jurisdiction_name` keys below must match the `name` field returned by the
corresponding `detect_*` function in `jurisdiction_engine.py` exactly, since
that's the string stored in `matters[i].confirmed_jurisdictions`.
"""

from docassemble.base.util import DAObject


STATE_PRIVACY_CONFIG = {
    'Indiana Consumer Data Protection Act': dict(
        code='IN',
        citations=dict(
            rights='IC 24-15-3-1(b)',
            deadline='IC 24-15-3-1(c)(1)',
            appeal='IC 24-15-3-1(d)',
            notice='IC 24-15-4-4',
            sensitive_data='IC 24-15-4-1(5)',
            dpa='IC 24-15-6-1(b)',
            contracts='IC 24-15-5',
        ),
        requires_uoom=False,
        uoom_citation=None,
        notes=[
            '30-day AG cure right is permanent, with no sunset (IC 24-15-10-3).',
        ],
    ),
    'Kentucky Consumer Data Protection Act': dict(
        code='KY',
        citations=dict(
            rights='KRS 367.3615(2)',
            deadline='KRS 367.3615(3)(a)',
            appeal='KRS 367.3615(4)',
            notice='KRS 367.3617(4)',
            sensitive_data='KRS 367.3617(1)(e)',
            dpa='KRS 367.3621(1)',
            contracts='KRS 367.3619',
        ),
        requires_uoom=False,
        uoom_citation=None,
        notes=[
            '30-day AG cure right is permanent (KRS 367.3627(2)).',
            'The DPA duty applies only to processing activities created or '
            'generated on or after 2026-06-01 (KRS 367.3621(8)).',
            'Consumers get two free responses per year, not one '
            '(KRS 367.3615(3)(c)).',
        ],
    ),
    'Colorado Privacy Act': dict(
        code='CO',
        citations=dict(
            rights='C.R.S. § 6-1-1306(1)(b)-(e)',
            deadline='C.R.S. § 6-1-1306(2)(a)',
            appeal='C.R.S. § 6-1-1306(3)',
            notice='C.R.S. § 6-1-1306(1)(a)(IV)',
            sensitive_data='C.R.S. § 6-1-1308(7)',
            dpa='C.R.S. § 6-1-1309',
            contracts='C.R.S. § 6-1-1305',
        ),
        requires_uoom=True,
        uoom_citation='C.R.S. § 6-1-1306(1)(a)(IV)(B)',
        notes=[
            'A separate minors-specific DPA and processing restrictions '
            'apply if the client knowingly offers services to minors '
            '(C.R.S. §§ 6-1-1305.5, 1308.5, 1309.5, eff. 2025-10-01) — '
            "verify manually if the client's user base includes minors.",
            'Biometric identifiers trigger a standalone written retention/'
            'security policy and breach protocol requirement '
            '(C.R.S. § 6-1-1314, eff. 2025-07-01) — verify manually if the '
            'client collects biometric data.',
            'General cure period sunset 2025-01-01, but preserved through '
            '2026-12-31 specifically for the new minors provisions '
            '(§ 6-1-1311(1)(d)).',
        ],
    ),
    'Delaware Personal Data Privacy Act': dict(
        code='DE',
        citations=dict(
            rights='6 Del. C. § 12D-104(a)(1)-(4),(6)',
            deadline='6 Del. C. § 12D-104(c)(1)',
            appeal='6 Del. C. § 12D-104(d)',
            notice='6 Del. C. § 12D-106(e)',
            sensitive_data='6 Del. C. § 12D-106(a)(4)',
            dpa='6 Del. C. § 12D-108(a)',
            contracts='6 Del. C. § 12D-107',
        ),
        requires_uoom=True,
        uoom_citation='6 Del. C. § 12D-106(e)(1)(a)(2), eff. 2026-01-01',
        notes=[
            'The Data Protection Assessment duty (§ 12D-108(a)) only '
            'attaches once the controller processes 100,000+ consumers/'
            "year — a higher bar than the Act's general 35,000/10,000 "
            'applicability threshold. A client covered by DE consumer-'
            'rights obligations may still owe no DPA duty — verify '
            'consumer volume against this specific threshold.',
            'Consumers have a standalone right to a list of third-party '
            'categories data was disclosed to (§ 12D-104(a)(5)), beyond '
            'what is in the privacy notice.',
            'Cure period was a fixed one-year window (2025-01-01 to '
            '2025-12-31); now AG-discretionary (§ 12D-111(c)).',
        ],
    ),
    'Montana Consumer Data Privacy Act': dict(
        code='MT',
        citations=dict(
            rights='Mont. Code Ann. § 30-14-2808(1)(a)-(e)',
            deadline='Mont. Code Ann. § 30-14-2808(4)(a)',
            appeal='Mont. Code Ann. § 30-14-2808(5)',
            notice='Mont. Code Ann. § 30-14-2809(3)(b)',
            sensitive_data='Mont. Code Ann. § 30-14-2812(2)(b)',
            dpa='Mont. Code Ann. § 30-14-2814(1)',
            contracts='Mont. Code Ann. § 30-14-2813',
        ),
        requires_uoom=True,
        uoom_citation='Mont. Code Ann. § 30-14-2809(3)(b), eff. 2025-01-01',
        notes=[
            "2025 amendment (SB297) added a standalone minors' duty-of-"
            "care regime (§ 30-14-2811) and separate minors' DPA "
            '(§ 30-14-2819) triggered whenever a controller offers a '
            'service to a known/willfully-disregarded minor — verify '
            "manually if the client's user base includes minors.",
            'The cure-period cross-reference (§ 30-14-2820(2) → '
            '§ 30-14-2817(3)) appears stale post-2025-amendment — '
            '§ 30-14-2817(3) as currently written covers civil '
            'investigative demands, not a cure mechanism. Flag for '
            'attorney confirmation rather than assuming a cure period '
            'exists.',
        ],
    ),
    'Nebraska Data Privacy Act': dict(
        code='NE',
        citations=dict(
            rights='Neb. Rev. Stat. § 87-1107(2)',
            deadline='Neb. Rev. Stat. § 87-1108(2)',
            appeal='Neb. Rev. Stat. § 87-1109',
            notice='Neb. Rev. Stat. § 87-1111',
            sensitive_data='Neb. Rev. Stat. § 87-1112(2)(d)',
            dpa='Neb. Rev. Stat. § 87-1116(1)',
            contracts='Neb. Rev. Stat. § 87-1115',
        ),
        requires_uoom=False,
        uoom_citation=None,
        notes=[
            'No numeric consumer-count/revenue threshold — applies to any '
            'non-SBA-small-business entity doing business in or targeting '
            'Nebraska (already reflected in detect_ne()).',
            'A standalone duty to obtain consent before selling sensitive '
            'data applies even to entities otherwise exempt as an SBA '
            'small business (§ 87-1118) — verify separately from the '
            'general applicability screen.',
            '30-day AG cure right is mandatory and permanent, with no '
            'sunset (§ 87-1122).',
            'The DPA trigger list includes an open-ended "heightened risk '
            'of harm" catch-all (§ 87-1116(1)(e)) beyond the standard '
            'four categories.',
        ],
    ),
    'New Hampshire Expectation of Privacy Act': dict(
        code='NH',
        citations=dict(
            rights='RSA 507-H:4(I)',
            deadline='RSA 507-H:4(III)(a)',
            appeal='RSA 507-H:4(IV)',
            notice='RSA 507-H:6(V)(a)(1)(B)',
            sensitive_data='RSA 507-H:6(I)(d)',
            dpa='RSA 507-H:8(I)',
            contracts='RSA 507-H:7',
        ),
        requires_uoom=True,
        uoom_citation='RSA 507-H:6(V)(a)(1)(B), eff. 2025-01-01',
        notes=[
            'AG cure period was mandatory through 2025-12-31; from '
            '2026-01-01 onward it is discretionary, weighed against '
            'statutory factors (§ 507-H:11(II)-(III)) — already in the '
            "discretionary era as of today. Don't assume a guaranteed "
            'cure right.',
            "Where NH's Act conflicts with another NH consumer-data "
            'statute, the more-protective standard governs, and opt-in '
            'is deemed per se more protective than opt-out (§ 507-H:12) — '
            'relevant if the client is also subject to other NH data '
            'statutes.',
        ],
    ),
    'New Jersey Data Privacy Act': dict(
        code='NJ',
        citations=dict(
            rights='N.J.S.A. 56:8-166.10',
            deadline='N.J.S.A. 56:8-166.7(a)',
            appeal='N.J.S.A. 56:8-166.7(f)',
            notice='N.J.S.A. 56:8-166.11(b)-(c)',
            sensitive_data='N.J.S.A. 56:8-166.12(a)(4)',
            dpa='N.J.S.A. 56:8-166.12(a)(9)',
            contracts='N.J.S.A. 56:8-166.16',
        ),
        requires_uoom=True,
        uoom_citation='N.J.S.A. 56:8-166.11(b), subject to Division of '
                       'Consumer Affairs rulemaking',
        notes=[
            'Sensitive-data definition is broader than the standard '
            'model — separately includes financial account/credential '
            'data and transgender or non-binary status (§ 56:8-166.5).',
            'Appeal decision deadline is 45 days, not the 60 days used in '
            'most other states in this batch (§ 56:8-166.7(f)).',
            'Teen-consent age band for targeted ads/sale/profiling runs '
            '13 to under 17, wider than most peer states\' 13-to-under-16 '
            '(§ 56:8-166.12(a)(7)).',
            'Universal opt-out mechanism requirement is subject to '
            'further NJ Division of Consumer Affairs rulemaking on '
            'technical specifications (§§ 56:8-166.11(c), 166.18) — '
            'confirm current regulatory status before relying on a fixed '
            'technical spec.',
            'Mandatory cure period sunsets 18 months after the Act\'s '
            'effective date (§ 56:8-166.17(b)), after which cure becomes '
            'discretionary.',
        ],
    ),
    'Oregon Consumer Privacy Act': dict(
        code='OR',
        citations=dict(
            rights='ORS 646A.574(1)',
            deadline='ORS 646A.576(5)(a)',
            appeal='ORS 646A.576(6)',
            notice='ORS 646A.578(5)(c)',
            sensitive_data='ORS 646A.578(2)(b)',
            dpa='ORS 646A.586(1)(b)',
            contracts='ORS 646A.581',
        ),
        requires_uoom=True,
        uoom_citation='ORS 646A.578(5)(c)',
        notes=[
            'Additional restriction: a controller may not process for '
            'targeted advertising/significant-effect profiling, or sell '
            'data, of a consumer it knows or willfully disregards is '
            'under 16, without consent (§ 646A.578(2)(c)-(d)) — a '
            'stricter age band than the standard under-13/COPPA '
            "framework. Verify manually if the client's user base may "
            'include 13-15 year-olds.',
            'Sensitive-data definition is broader than the standard '
            'model — separately includes transgender/nonbinary status '
            'and victim-of-crime status (§ 646A.570(18)(a)(A)).',
        ],
    ),
    'Rhode Island Data Transparency and Privacy Protection Act': dict(
        code='RI',
        citations=dict(
            rights='R.I. Gen. Laws § 6-48.1-5(e)',
            deadline='R.I. Gen. Laws § 6-48.1-6(b)(1)',
            appeal='R.I. Gen. Laws § 6-48.1-6(b)(6)',
            notice='R.I. Gen. Laws § 6-48.1-5(f)',
            sensitive_data='R.I. Gen. Laws § 6-48.1-4(c)',
            dpa='R.I. Gen. Laws § 6-48.1-7(e)',
            contracts='R.I. Gen. Laws § 6-48.1-7',
        ),
        requires_uoom=False,
        uoom_citation=None,
        notes=[
            'Applies to for-profit entities only (§§ 6-48.1-4(a), 5(a), '
            '6(a), 7(a)) — already reflected in detect_ri(), but verify '
            'entity type before relying on RI obligations for a '
            'nonprofit client.',
            'Appeal decision deadline is 60 days, not 45.',
            'The profiling opt-out right is scoped to profiling in '
            'furtherance of solely automated decisions '
            '(§ 6-48.1-5(e)(4)) — narrower than the standard '
            '"significant decisions" framing.',
            'A separate mandatory fine of $100-$500 per disclosure '
            'applies to intentional disclosure to a shell/circumvention '
            'entity (§ 6-48.1-8(a)), layered on top of general '
            'enforcement — worth noting in risk discussions.',
        ],
    ),
    'Tennessee Information Protection Act': dict(
        code='TN',
        citations=dict(
            rights='Tenn. Code Ann. § 47-18-3203(a)(2)',
            deadline='Tenn. Code Ann. § 47-18-3203(b)(1)',
            appeal='Tenn. Code Ann. § 47-18-3203(c)',
            notice='Tenn. Code Ann. § 47-18-3204(e)',
            sensitive_data='Tenn. Code Ann. § 47-18-3204(a)(6)',
            dpa='Tenn. Code Ann. § 47-18-3206(a)',
            contracts='Tenn. Code Ann. § 47-18-3205',
        ),
        requires_uoom=False,
        uoom_citation=None,
        notes=[
            'Applicability requires a conjunctive $25M+ annual revenue '
            'floor on top of the consumer-volume test (already reflected '
            'in detect_tn()).',
            'Mandatory 60-day AG cure period is a standing precondition '
            'to all enforcement (§ 47-18-3212(b)), not a sunsetting one.',
            'Maintaining a NIST Privacy Framework-conformant written '
            'privacy program is an affirmative defense against '
            'enforcement (§ 47-18-3213) — worth flagging to clients as a '
            'voluntary compliance opportunity.',
            'Appeal decision deadline is 60 days, not 45; consumers get '
            'two free responses per year, not one (§ 47-18-3203(b)(3)).',
            'The DPA trigger list includes an open-ended "heightened '
            'risk of harm" catch-all (§ 47-18-3206(a)(5)) beyond the '
            'standard four categories.',
        ],
    ),
}


class StatePrivacyAct(DAObject):
    """
    One instance per applicable "standard model" state privacy act (see
    STATE_PRIVACY_CONFIG above). `jurisdiction_name` and `matter` must be set
    right after creation, before any question/logic block reads this
    instance — see the per-matter init loop in main.yml.
    """

    @property
    def full_name(self):
        return self.jurisdiction_name

    @property
    def code(self):
        return STATE_PRIVACY_CONFIG[self.jurisdiction_name]['code']

    @property
    def requires_uoom(self):
        return STATE_PRIVACY_CONFIG[self.jurisdiction_name]['requires_uoom']

    @property
    def uoom_citation(self):
        return STATE_PRIVACY_CONFIG[self.jurisdiction_name]['uoom_citation']

    @property
    def notes(self):
        return STATE_PRIVACY_CONFIG[self.jurisdiction_name]['notes']

    def citation(self, key):
        return STATE_PRIVACY_CONFIG[self.jurisdiction_name]['citations'][key]


def applicable_state_privacy_acts(matter):
    """
    Names of "standard model" state privacy acts (per STATE_PRIVACY_CONFIG)
    that are in matter.confirmed_jurisdictions. Iterates STATE_PRIVACY_CONFIG
    rather than confirmed_jurisdictions.true_values() so the display order is
    stable regardless of checkbox-widget ordering.
    """
    confirmed = set(matter.confirmed_jurisdictions.true_values())
    return [name for name in STATE_PRIVACY_CONFIG if name in confirmed]
