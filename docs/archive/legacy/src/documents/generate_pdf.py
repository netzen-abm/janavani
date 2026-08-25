# Archived legacy implementation preserved before consolidation.
# Source: src/documents/generate_pdf.py

from weasyprint import HTML
import pandas as pd


def generate_pdf_from_complaint(complaint: dict) -> str:
    """
    New: Generates PDF from structured complaint
    """

    df = pd.read_csv("database/offices.csv")
    office = df[df['id'] == int(complaint["office_id"])].iloc[0]

    complaint_id = complaint["complaint_id"]
    today = complaint["date"]
    user_name = complaint["user"]["name"]
    user_address = complaint["user"]["address"]
    issue_text = complaint["issue"]
    law_data = complaint["law"]

    html_content = f"""
    <html>
    <head><style>
        body {{ font-family: Arial; margin: 40px; }}
        h2 {{ text-align: center; }}
        .header {{ margin-bottom: 30px; }}
    </style></head>
    <body>
        <h2>FORMAL COMPLAINT</h2>
        <p><b>Complaint ID:</b> {complaint_id}<br><b>Date:</b> {today}</p>
        <div class="header">
            <p><b>To:</b><br>
            The {office['officer_role']}<br>
            {office['name']}<br>
            {office['address']}</p>
        </div>
        <div class="header">
            <p><b>From:</b><br>
            {user_name}<br>
            {user_address}</p>
        </div>
        <p><b>Subject:</b> Complaint regarding deficiency in service at {office['name']}</p>
        <p>Respected Sir/Madam,</p>
        <p>I visited {office['name']} on {today} regarding the following issue:</p>
        <p><i>"{issue_text}"</i></p>
        <p><b>Legal Ground:</b><br>
        As per <b>{law_data['law']}</b>, <b>{law_data['section']}</b><br>
        {law_data['explanation']}</p>
        <p>I therefore request you to take immediate action and resolve this matter within 7 days.</p>
        <p>Thank you.</p>
        <br><br>
        <p>Sincerely,<br>{user_name}</p>
        <hr>
        <p><b>CC:</b> 1. District Collector, Ernakulam<br>
        2. Head of Department, {office['type']}</p>
    </body>
    </html>
    """

    filename = f"complaint_{complaint_id}.pdf"
    HTML(string=html_content).write_pdf(filename)
    return f"PDF Generated: {filename}. Print and send to {office['name']}"

from src.documents.complaint_builder import build_complaint


def generate_complaint_pdf(user_name, user_address, office_id, issue_text):
    """OLD interface preserved"""
    complaint = build_complaint(
        user_name=user_name,
        user_address=user_address,
        office_id=office_id,
        issue_text=issue_text
    )
    return
