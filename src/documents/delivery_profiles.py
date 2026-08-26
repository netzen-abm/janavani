"""Supported delivery profiles for document workflows."""

from enum import StrEnum


class DeliveryProfile(StrEnum):
    EMAIL = "EMAIL"
    REGISTERED_POST = "REGISTERED_POST"
    SPEED_POST = "SPEED_POST"
    HAND_DELIVERY = "HAND_DELIVERY"
    ONLINE_PORTAL = "ONLINE_PORTAL"
    COURIER = "COURIER"


__all__ = ["DeliveryProfile"]
