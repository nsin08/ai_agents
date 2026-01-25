from src.agent_labs.context import ContextManifest


def test_context_manifest_to_dict_contains_budget_and_items():
    manifest = ContextManifest(request_id="req-1", max_tokens=1000, reserved_response_tokens=200)
    manifest.add_item(kind="evidence", tokens=50, reason="retrieval_top_k", metadata={"doc_id": "d1"})
    payload = manifest.to_dict()

    assert payload["request_id"] == "req-1"
    assert payload["budget"]["max_tokens"] == 1000
    assert payload["budget"]["reserved_response_tokens"] == 200
    assert payload["items"][0]["metadata"]["doc_id"] == "d1"

