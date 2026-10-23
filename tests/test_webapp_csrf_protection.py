from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.webapp.csrf_protection import SameOriginCookieMutationMiddleware


def _client():
    app = FastAPI()
    app.add_middleware(SameOriginCookieMutationMiddleware)

    @app.post("/mutate")
    def mutate():
        return {"ok": True}

    @app.get("/read")
    def read():
        return {"ok": True}

    client = TestClient(app, base_url="https://janavani.test")
    client.cookies.set("janavani_identity_assertion", "opaque-test-assertion")
    return client


def test_cookie_authenticated_mutation_accepts_same_origin():
    response = _client().post(
        "/mutate", headers={"Origin": "https://janavani.test"}
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_cookie_authenticated_mutation_rejects_cross_origin():
    response = _client().post(
        "/mutate", headers={"Origin": "https://attacker.test"}
    )
    assert response.status_code == 403
    assert response.headers["cache-control"] == "no-store"


def test_invalid_origin_does_not_fall_back_to_same_origin_referer():
    response = _client().post(
        "/mutate",
        headers={
            "Origin": "null",
            "Referer": "https://janavani.test/form",
        },
    )
    assert response.status_code == 403


def test_same_origin_referer_is_accepted_when_origin_is_absent():
    response = _client().post(
        "/mutate", headers={"Referer": "https://janavani.test/form"}
    )
    assert response.status_code == 200


def test_origin_port_normalizes_default_https_port():
    response = _client().post(
        "/mutate",
        headers={
            "Host": "janavani.test:443",
            "Origin": "https://janavani.test",
        },
    )
    assert response.status_code == 200


def test_read_only_request_is_not_subject_to_mutation_origin_gate():
    response = _client().get("/read", headers={"Origin": "https://attacker.test"})
    assert response.status_code == 200



def test_cookie_authenticated_mutation_rejects_scheme_mismatch():
    response = _client().post(
        "/mutate", headers={"Origin": "http://janavani.test"}
    )
    assert response.status_code == 403
