from dataclasses import dataclass

from src.storage.relationship_repository import CanonicalRelationshipRepository


@dataclass
class Response:
    data: list[dict]


class Query:
    def __init__(self, table: str, payload: dict) -> None:
        self.table = table
        self.payload = payload
        self.executed = False

    def insert(self, payload: dict):
        self.payload = payload
        return self

    def execute(self):
        self.executed = True
        return Response([self.payload])


class Rpc:
    def __init__(self, function_name: str, params: dict) -> None:
        self.function_name = function_name
        self.params = params
        self.executed = False

    def execute(self):
        self.executed = True
        return Response([])


class Client:
    def __init__(self) -> None:
        self.queries: list[Query] = []
        self.rpcs: list[Rpc] = []

    def table(self, name: str) -> Query:
        query = Query(name, {})
        self.queries.append(query)
        return query

    def rpc(self, function_name: str, params: dict) -> Rpc:
        rpc = Rpc(function_name, params)
        self.rpcs.append(rpc)
        return rpc


def test_case_relationship_links_use_atomic_database_functions() -> None:
    client = Client()
    repository = CanonicalRelationshipRepository(client)

    repository.link_evidence("CASE-1", "E-1")
    repository.link_authority("CASE-1", "AUTH-1")
    repository.link_consent("CASE-1", "CON-1")
    repository.link_document("CASE-1", "DOC-1")
    repository.link_submission("CASE-1", "SUB-1")

    assert [(rpc.function_name, rpc.params) for rpc in client.rpcs] == [
        ("link_case_evidence_atomic", {"p_case_id": "CASE-1", "p_evidence_id": "E-1", "p_actor": None}),
        ("link_case_authority_atomic", {"p_case_id": "CASE-1", "p_authority_id": "AUTH-1", "p_actor": None}),
        ("link_case_consent_atomic", {"p_case_id": "CASE-1", "p_consent_id": "CON-1", "p_actor": None}),
        ("link_case_document_atomic", {"p_case_id": "CASE-1", "p_document_id": "DOC-1", "p_actor": None}),
        ("link_case_submission_atomic", {"p_case_id": "CASE-1", "p_submission_id": "SUB-1", "p_actor": None}),
    ]
    assert all(rpc.executed for rpc in client.rpcs)


def test_case_events_use_atomic_rpc_and_delivery_events_are_append_only() -> None:
    client = Client()
    repository = CanonicalRelationshipRepository(client)

    repository.append_case_event("CASE-1", "submission.approved", actor="api", event_data={"submission_id": "SUB-1"})
    repository.append_delivery_event("SUB-1", "received", adapter_id="internet", reference="receipt-1")

    assert client.rpcs[0].function_name == "append_case_event_atomic"
    assert client.rpcs[0].params["p_event_type"] == "submission.approved"
    assert client.queries[0].table == "delivery_events"
    assert client.queries[0].payload["reference"] == "receipt-1"
    assert client.queries[0].executed
