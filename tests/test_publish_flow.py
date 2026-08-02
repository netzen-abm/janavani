import json


def test_publish_rating_flow(monkeypatch):
    # Arrange: fake helpers
    fake_cid = "QmFakeCid12345"

    def fake_add_bytes(data):
        # ensure we got bytes
        assert isinstance(data, (bytes, bytearray))
        return fake_cid

    def fake_publish_nostr_event(content):
        assert isinstance(content, dict)
        return "fake-nostr-id"

    def fake_anchor_to_chain(cid):
        assert cid == fake_cid
        return "0xdeadbeef"

    monkeypatch.setattr("services.storage_ipfs.add_bytes_to_ipfs", fake_add_bytes)
    monkeypatch.setattr("services.nostr_client.publish_nostr_event", fake_publish_nostr_event)
    monkeypatch.setattr("services.blockchain.anchor_to_chain", fake_anchor_to_chain)

    # Act: call the function directly to avoid running the ASGI server
    from api.agent_api import publish_rating
    from api.agent_api import RatingPayload

    payload = RatingPayload(user="alice", rating=5, text="Good service")

    result = None
    import asyncio

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(publish_rating(payload))

    # Assert
    assert result["cid"] == fake_cid
    assert result["nostr_event_id"] == "fake-nostr-id"
    assert result["tx_hash"] == "0xdeadbeef"
