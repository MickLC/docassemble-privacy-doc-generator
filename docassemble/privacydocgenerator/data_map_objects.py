from docassemble.base.core import DAObject


class SystemOrVendor(DAObject):
    """A vendor, system, or storage location that can receive personal data.
    Shared by the upfront Vendor & System Inventory (matters[i].systems) and
    by systems added inline while describing a processing activity
    (matters[i].processing_activities[j].new_systems[k]), so one
    `generic object: SystemOrVendor` question block gathers either.
    """
    pass
