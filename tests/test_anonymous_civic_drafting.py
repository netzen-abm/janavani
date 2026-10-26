from src.capabilities.anonymous_civic_drafting import (
    build_anonymous_drafts,
    recommend_document_types,
)
from src.documents.anonymous_draft_renderer import render_anonymous_draft


def test_information_only_narrative_recommends_rti():
    types, reason = recommend_document_types(
        "I need copies of the work order and action taken report for the road repair."
    )
    assert types == ("rti",)
    assert "records" in reason


def test_remedy_only_narrative_recommends_complaint():
    types, _reason = recommend_document_types(
        "The streetlight has not worked for two weeks and needs repair."
    )
    assert types == ("complaint",)


def test_incident_and_records_narrative_recommends_both_documents():
    narrative = (
        "The road is broken and unsafe. Please repair it and provide copies "
        "of the tender and work order."
    )
    types, _reason = recommend_document_types(narrative)
    drafts = build_anonymous_drafts(narrative)
    assert types == ("complaint", "rti")
    assert tuple(draft.document_type for draft in drafts) == types
    assert all(narrative in draft.body for draft in drafts)
    assert all("DRAFT ONLY" in draft.body for draft in drafts)


def test_user_can_override_recommendation_and_request_both():
    narrative = "A broken streetlight is dangerous."
    assert tuple(x.document_type for x in build_anonymous_drafts(narrative, "rti")) == ("rti",)
    assert tuple(x.document_type for x in build_anonymous_drafts(narrative, "both")) == ("complaint", "rti")


def test_anonymous_draft_rejects_empty_tiny_and_oversized_narratives():
    for value in ("", "hi", "x " * 2501):
        try:
            build_anonymous_drafts(value)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid narrative should be rejected")


def test_pdf_and_docx_rendering_is_in_memory_and_downloadable():
    draft = build_anonymous_drafts("The streetlight is broken and needs repair.")[0]
    pdf, pdf_type, pdf_ext = render_anonymous_draft(draft, "pdf")
    docx, docx_type, docx_ext = render_anonymous_draft(draft, "docx")
    assert pdf.startswith(b"%PDF-")
    assert pdf_type == "application/pdf"
    assert pdf_ext == "pdf"
    assert docx.startswith(b"PK")
    assert "wordprocessingml" in docx_type
    assert docx_ext == "docx"
