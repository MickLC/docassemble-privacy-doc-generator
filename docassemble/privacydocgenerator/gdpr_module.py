"""
gdpr_module.py
Helper functions for the Privacy Policy Generator interview.
"""

from docassemble.base.util import DAObject, log


def format_data_types(data_types_collected):
    """
    Returns a formatted list of collected data types
    from the checkboxes DAObject.
    """
    return [key for key, value in data_types_collected.items() if value]


def format_purposes(processing_purposes):
    """
    Returns a formatted list of processing purposes
    from the checkboxes DAObject.
    """
    return [key for key, value in processing_purposes.items() if value]


def format_lawful_bases(lawful_bases):
    """
    Returns a formatted list of lawful bases
    from the checkboxes DAObject.
    """
    return [key for key, value in lawful_bases.items() if value]


def requires_dpia(data_types_collected, processing_purposes):
    """
    Determines whether a Data Protection Impact Assessment (DPIA)
    is likely required based on data types and purposes.
    Returns True if high-risk processing is detected.
    """
    high_risk_data = [
        'Health or medical data',
        "Children's data (under 16)",
        'Financial information',
        'Location data',
    ]
    high_risk_purposes = [
        'Analytics and service improvement',
        'Fraud prevention and security',
    ]

    for item in high_risk_data:
        if data_types_collected.get(item):
            return True
    for purpose in high_risk_purposes:
        if processing_purposes.get(purpose):
            return True
    return False
