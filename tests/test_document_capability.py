from documents.document_engine import DocumentEngine


def test_document_engine_generates_pdf_and_docx():
    engine = DocumentEngine()

    pdf = engine.generate(
        "complaint",
        format_type="pdf",
        user_name="Test Citizen",
        user_address="Test Address",
        office_id="1",
        issue_text="Road maintenance issue",
        office={"name": "Test Office", "email": "office@example.gov.in"},
        subject="Road maintenance",
        cc=[{"name": "District Authority", "email": "authority@example.gov.in"}],
    )
    assert pdf.media_type == "application/pdf"
    assert pdf.extension == ".pdf"
    assert pdf.content.startswith(b"%PDF")

    docx = engine.generate(
        "complaint",
        format_type="docx",
        user_name="Test Citizen",
        user_address="Test Address",
        office_id="1",
        issue_text="Road maintenance issue",
    )
    assert docx.extension == ".docx"
    assert docx.content.startswith(b"PK")


def test_composition_preserves_editable_address_fields():
    payload = DocumentEngine().compose(
        "complaint",
        user_name="Citizen",
        user_address="Citizen Address",
        office_id="1",
        issue_text="Service issue",
        office={"name": "Office", "email": "office@example.gov.in"},
        cc=[{"name": "Authority", "email": "authority@example.gov.in"}],
    )
    assert payload["to"]["email"] == "office@example.gov.in"
    assert payload["cc"][0]["email"] == "authority@example.gov.in"
