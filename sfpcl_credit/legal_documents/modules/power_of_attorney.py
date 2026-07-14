"""Compatibility import for callers retained before the security owner transfer.

Power of Attorney policy belongs to ``security_instruments``. New code must import the
security owner directly; this module contains no policy.
"""

from sfpcl_credit.security_instruments.modules.power_of_attorney import *  # noqa: F403
