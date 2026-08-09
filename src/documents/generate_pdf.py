# src/tools/generate_pdf.py
# Makes legal complaint PDF with law citation

from weasyprint import HTML
import datetime
import pandas as pd
from legal_brain import get_legal_advice

def generate_complaint_pdf(user_name, user_address, office_id, issue_text):
    """
    Generates PDF complaint letter
    """
    # 1. Find office details from CSV
    df = pd.read_csv("database/offices.csv")
    office = df[df['id'] == int(office_id)].iloc[0]

    # 2. Get law from Legal Brain
    law_data = get_legal_advice(issue_text)

    # 3. Create HTML for PDF
    today = datetime.date.today().strftime("%d-%m-%Y")
    complaint_id = f"JV{datetime.datetime.now().strftime('%Y%m%d%H%M')}"

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

    # 4. Generate PDF
    filename = f"complaint_{complaint_id}.pdf"
    HTML(string=html_content).write_pdf(filename)

    return f"PDF Generated: {filename}. Print and send to {office['name']}"
