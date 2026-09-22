from src.access.capability_session import (
    CapabilitySession,
    CapabilitySessionError,
    CapabilitySessionManager,
    CapabilitySessionState,
)


def _session():
    return CapabilitySession(
        session_id="session-1",
        principal_id="principal-1",
        purpose="evidence_capture",
        resource="camera",
    )


def test_sensitive_capability_session_follows_terminal_lifecycle():
    manager = CapabilitySessionManager()
    session = manager.present_purpose(_session())
    session = manager.grant(session)
    session = manager.activate(session)
    session = manager.purpose_complete(session)
    session = manager.release(session)

    assert session.state is CapabilitySessionState.RELEASED


def test_released_session_cannot_be_reactivated():
    manager = CapabilitySessionManager()
    session = manager.present_purpose(_session())
    session = manager.grant(session)
    session = manager.release(session)

    try:
        manager.activate(session)
    except CapabilitySessionError:
        pass
    else:
        raise AssertionError("released sessions must be terminal")


def test_denied_and_unavailable_sessions_are_terminal():
    manager = CapabilitySessionManager()
    presented = manager.present_purpose(_session())

    denied = manager.transition(presented, CapabilitySessionState.DENIED)
    unavailable = manager.transition(presented, CapabilitySessionState.UNAVAILABLE)

    assert denied.state is CapabilitySessionState.DENIED
    assert unavailable.state is CapabilitySessionState.UNAVAILABLE


def test_invalid_transition_is_rejected():
    manager = CapabilitySessionManager()

    try:
        manager.activate(_session())
    except CapabilitySessionError:
        pass
    else:
        raise AssertionError("activation before purpose/grant must be rejected")
