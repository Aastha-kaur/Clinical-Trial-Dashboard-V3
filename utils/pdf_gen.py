import os
from fpdf import FPDF
from datetime import datetime

PDF_FOLDER = "data/pdfs"
os.makedirs(PDF_FOLDER, exist_ok=True)

def generate_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_title("Claim Approval Summary")
    pdf.cell(200, 10, txt="Reimbursement Approval Summary", ln=True, align='C')
    pdf.ln(10)

    fields = [
        ("Participant ID", row["Participant ID"]),
        ("Visit Number", row["Visit Number"]),
        ("Visit Date", row["Visit Date"]),
        ("Visit Location", row["Visit Location"]),
        ("Approved Date", datetime.now().strftime('%Y-%m-%d')),
        ("Parking", f"${row['Parking']}"),
        ("Meal", f"${row['Meal']}"),
        ("KM Amount", f"${row['Kilometre Reimbursement']}"),
        ("Distance", f"{row['Distance (km)']} km"),
        ("Visit Duration", f"{row['Visit Duration (hrs)']} hrs"),
        ("Air Travel", f"${row['Air Travel']}"),
        ("Accommodation", f"${row['Accommodation']}"),
        ("Caregiver Present", "Yes" if row['Caregiver Present'] else "No"),
        ("Sub Visit Imaging", "Yes" if row['Sub-Visit Imaging'] else "No"),
        ("Total Claimed", f"${row['Total Claimed (est.)']}"),
        ("Notes", row['Notes'] or "None")
    ]

    for label, value in fields:
        pdf.cell(200, 10, txt=f"{label}: {value}", ln=True)

    filename = f"{PDF_FOLDER}/Claim_{row['Participant ID']}_{row['Visit Number']}.pdf"
    pdf.output(filename)
    return filename
