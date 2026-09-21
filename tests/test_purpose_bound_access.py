from src.capabilities.purpose_bound_access import (
    PermissionLifecycleState, PurposeBoundPermissionLifecycle, PurposeBoundPermissionRequest,
)
from src.capabilities.safety_privacy import AccessPurpose, SensitiveResource
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal

def _identity(pid="citizen:permission"):
    return IdentityContext(principal=Principal(principal_id=pid, identity_mode=IdentityMode.AUTHENTICATED, interface="test"))

def test_sensitive_resource_requires_purpose_and_releases_after_use():
    lifecycle=PurposeBoundPermissionLifecycle(); identity=_identity()
    session=lifecycle.present(PurposeBoundPermissionRequest(identity,AccessPurpose.EVIDENCE_CAPTURE,SensitiveResource.CAMERA,"Capture one incident image"))
    assert session.state is PermissionLifecycleState.PURPOSE_PRESENTED
    lifecycle.grant(session.session_id); lifecycle.activate(session.session_id,identity=identity)
    lifecycle.purpose_complete(session.session_id,identity=identity)
    released=lifecycle.release(session.session_id,identity=identity)
    assert released.state is PermissionLifecycleState.RELEASED

def test_released_permission_cannot_be_reactivated():
    lifecycle=PurposeBoundPermissionLifecycle(); identity=_identity()
    s=lifecycle.present(PurposeBoundPermissionRequest(identity,AccessPurpose.EVIDENCE_CAPTURE,SensitiveResource.MICROPHONE,"Record one statement"))
    lifecycle.grant(s.session_id); lifecycle.activate(s.session_id,identity=identity)
    lifecycle.purpose_complete(s.session_id,identity=identity); lifecycle.release(s.session_id,identity=identity)
    try: lifecycle.activate(s.session_id,identity=identity)
    except ValueError: pass
    else: raise AssertionError("released permission must require a new purpose-bound session")

def test_permission_session_is_identity_bound():
    lifecycle=PurposeBoundPermissionLifecycle(); owner=_identity("citizen:a"); other=_identity("citizen:b")
    s=lifecycle.present(PurposeBoundPermissionRequest(owner,AccessPurpose.SOS,SensitiveResource.LOCATION,"Provide current location for SOS"))
    lifecycle.grant(s.session_id)
    try: lifecycle.activate(s.session_id,identity=other)
    except PermissionError: pass
    else: raise AssertionError("another identity must not activate the permission session")


class Adapter:
    def __init__(self): self.released=[]
    def release(self, *, session_id, resource): self.released.append((session_id, resource))

class Minimizer:
    def __init__(self): self.minimized=[]
    def minimize(self, *, session_id, resource, purpose): self.minimized.append((session_id, resource, purpose))


def test_completion_minimizes_data_and_release_stops_resource():
    identity=_identity(); adapter=Adapter(); minimizer=Minimizer()
    lifecycle=PurposeBoundPermissionLifecycle(resource_adapter=adapter, data_minimizer=minimizer)
    s=lifecycle.present(PurposeBoundPermissionRequest(identity,AccessPurpose.EVIDENCE_CAPTURE,SensitiveResource.CAMERA,"Capture one image"))
    lifecycle.grant(s.session_id); lifecycle.activate(s.session_id,identity=identity)
    lifecycle.purpose_complete(s.session_id,identity=identity)
    lifecycle.release(s.session_id,identity=identity)
    assert len(minimizer.minimized)==1
    assert len(adapter.released)==1
