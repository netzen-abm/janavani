"""Supported delivery methods for civic documents.

Values are stable machine-readable identifiers; user-facing labels belong in
presentation/translation layers.
"""

EMAIL = "email"
REGISTERED_POST = "registered_post"
SPEED_POST = "speed_post"
HAND_DELIVERY = "hand_delivery"
ONLINE_PORTAL = "online_portal"
COURIER = "courier"

DELIVERY_PROFILES = (
    EMAIL,
    REGISTERED_POST,
    SPEED_POST,
    HAND_DELIVERY,
    ONLINE_PORTAL,
    COURIER,
)
