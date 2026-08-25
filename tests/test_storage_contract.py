from src.platform.storage import StorageResult
from src.storage.supabase_adapter import SupabaseStorageAdapter


class FakeResponse:
    def __init__(self, data=None):
        self.data = data or []


class FakeQuery:
    def __init__(self, rows=None):
        self.rows = rows or []

    def select(self, _columns):
        return self

    def eq(self, _column, _value):
        return self

    def limit(self, _count):
        return self

    def upsert(self, _payload):
        return self

    def delete(self):
        return self

    def execute(self):
        return FakeResponse(self.rows)


class FakeClient:
    def __init__(self):
        self.rows = {"items": [{"id": "1", "value": "old"}]}

    def table(self, collection):
        return FakeQuery(self.rows.get(collection, []))


def test_storage_result_contract_is_provider_neutral() -> None:
    result = StorageResult(ok=True, value={"id": "1"})
    assert result.ok is True
    assert result.value["id"] == "1"


def test_supabase_adapter_implements_storage_operations() -> None:
    adapter = SupabaseStorageAdapter(FakeClient())

    get_result = adapter.get("items", "1")
    put_result = adapter.put("items", "2", {"value": "new"})
    delete_result = adapter.delete("items", "1")

    assert get_result.ok
    assert put_result.ok
    assert delete_result.ok
