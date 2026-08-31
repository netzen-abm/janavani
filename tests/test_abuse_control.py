import pytest

from src.security.abuse_control import AbuseController, AbuseLimitExceeded, RateLimit


def test_rate_limit_allows_within_budget():
    controller = AbuseController()
    limit = RateLimit(max_requests=2, window_seconds=60)
    controller.check("anon-1", "citizen.rating.submit", limit)
    controller.check("anon-1", "citizen.rating.submit", limit)


def test_rate_limit_denies_after_budget():
    controller = AbuseController()
    limit = RateLimit(max_requests=1, window_seconds=60)
    controller.check("anon-1", "citizen.rating.submit", limit)
    with pytest.raises(AbuseLimitExceeded):
        controller.check("anon-1", "citizen.rating.submit", limit)


def test_rate_limit_isolated_by_capability():
    controller = AbuseController()
    limit = RateLimit(max_requests=1, window_seconds=60)
    controller.check("anon-1", "citizen.rating.submit", limit)
    controller.check("anon-1", "public.search_office", limit)
