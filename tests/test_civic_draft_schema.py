import json

import pytest

from src.services.civic_draft_schema import InvalidAIDraftOutput, normalize_provider_draft


def _payload(content):
    return {"choices": [{"message": {"content": content}}]}


def test_schema_extracts_only_bounded_editable_fields():
    raw = json.dumps({
        "subject": "Road maintenance",
        "proposal_or_notice": "Please inspect.",
        "part_i_interrogatories": ["Which office is responsible?"],
        "requested_conditions": ["Please respond in writing."],
        "remedies_reserved": ["Lawful remedies are reserved."],
        "legal_framework": ["Invented statute"],
        "deadline_date": "Tomorrow",
        "authority_id": "unverified-office",
    })
    result = normalize_provider_draft(_payload(raw), fallback_subject="Fallback")

    assert result == {
        "subject": "Road maintenance",
        "proposal_or_notice": "Please inspect.",
        "part_i_interrogatories": ["Which office is responsible?"],
        "requested_conditions": ["Please respond in writing."],
        "remedies_reserved": ["Lawful remedies are reserved."],
    }
    assert "legal_framework" not in result
    assert "deadline_date" not in result
    assert "authority_id" not in result


@pytest.mark.parametrize("payload", [
    {},
    {"choices": []},
    {"choices": [{"message": {"content": "not-json"}}]},
    {"choices": [{"message": {"content": "[]"}}]},
])
def test_malformed_provider_output_fails_closed(payload):
    with pytest.raises(InvalidAIDraftOutput):
        normalize_provider_draft(payload, fallback_subject="Road issue")


def test_model_output_length_and_list_bounds_are_enforced():
    too_long = '{"subject":"' + ("x" * 201) + '","proposal_or_notice":"request"}'
    with pytest.raises(InvalidAIDraftOutput):
        normalize_provider_draft(_payload(too_long), fallback_subject="Fallback")

    too_many = {
        "subject": "Road",
        "proposal_or_notice": "Please inspect.",
        "part_i_interrogatories": ["Question"] * 13,
    }
    with pytest.raises(InvalidAIDraftOutput):
        normalize_provider_draft(_payload(json.dumps(too_many)), fallback_subject="Fallback")


def test_fenced_json_response_is_normalized():
    fence = chr(96) * 3
    response = f'{fence}json\n{{"subject":"Road","proposal_or_notice":"Please inspect."}}\n{fence}'
    result = normalize_provider_draft(
        _payload(response), fallback_subject="Fallback"
    )
    assert result["subject"] == "Road"
