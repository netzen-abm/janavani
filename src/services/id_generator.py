import uuid
from datetime import datetime


def generate_complaint_id():

    date_part = datetime.now().strftime("%Y%m%d")

    unique_part = str(uuid.uuid4())[:6].upper()

    return f"JAN-{date_part}-{unique_part}"