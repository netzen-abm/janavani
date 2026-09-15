"""Retired legacy rating service.

The historical implementation is preserved under archive/legacy/feedback/.
The canonical replacement is src/capabilities/accountability_feedback.py.
"""


def save_rating(*args, **kwargs):
    """Fail closed so legacy callers cannot bypass the canonical capability."""
    raise RuntimeError(
        "Legacy rating service is retired; use AccountabilityFeedbackCapability."
    )
