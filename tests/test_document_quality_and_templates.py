from capabilities.document_quality import DocumentQualityCapability
from capabilities.document_templates import get_template


def test_quality_requires_verified_authority_address_subject_and_issue():
    result = DocumentQualityCapability().check({"authority": {"name": "PWD"}, "issue": "Road broken"})
    codes = {issue.code for issue in result.issues}
    assert not result.ok
    assert "missing_to_address" in codes
    assert "missing_subject" in codes


def test_quality_accepts_minimum_complaint_data():
    result = DocumentQualityCapability().check({
        "authority": {"name": "PWD", "address": "Office address"},
        "subject": "Broken road",
        "issue": "Road has been damaged for two weeks.",
        "user": {"name": "Citizen"},
    })
    assert result.ok


def test_template_is_versioned_and_channel_neutral():
    template = get_template("complaint")
    assert template.template_id == "JNV-COMPLAINT"
    assert template.version == "1.0"
    assert "authority" in template.required_fields
