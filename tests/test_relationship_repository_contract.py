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


class Client:
    def __init__(self) -> None:
        self.queries: list[Query] = []

    def table(self, name: str) -> Query:
        query = Query(name, {})
        self.queries.append(query)
        return query


def test_case_relationship_links_use_canonical_join_tables() -> None:
    client = Client()
    repository = CanonicalRelationshipRepository(client)

    repository.link_evidence("CASE-1", "E-1")
    repository.link_authority("CASE-1", "AUTH-1")
    repository.link_consent("CASE-1", "CON-1")
    repository.link_document("CASE-1", "DOC-1")
    repository.link_submission("CASE-1", "SUB-1")

    assert [(q.table, q.payload) for q in client.queries] == [
        ("case_evidence_refs", {"case_id": "CASE-1", "evidence_id": "E-1"}),
        ("case_authority_refs", {"case_id": "CASE-1", "authority_id": "AUTH-1"}),
        ("case_consent_refs", {"case_id": "CASE-1", "consent_id": "CON-1"}),
        ("case_document_refs", {"case_id": "CASE-1", "document_id": "DOC-1"}),
        ("case_submission_refs", {"case_id": "CASE-1", "submission_id": "SUB-1"}),
    ]
    assert all(query.executed for query in client.queries)


def test_event_methods_are_append_only_inserts() -> None:
    client = Client()
    repository = CanonicalRelationshipRepository(client)

    repository.append_case_event(
        "CASE-1", "submission.approved", actor="api", event_data={"submission_id": "SUB-1"}
    )
    repository.append_delivery_event(
        "SUB-1", "received", adapter_id="internet", reference="receipt-1"
    )

    assert client.queries[0].table == "case_events"
    assert client.queries[0].payload["event_type"] == "submission.approved"
    assert client.queries[1].table == "delivery_events"
    assert client.queries[1].payload["reference"] == "receipt-1"
    assert all(query.executed for query in client.queries)
