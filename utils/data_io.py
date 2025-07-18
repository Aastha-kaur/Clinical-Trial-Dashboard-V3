import pandas as pd
import os
from datetime import datetime

VISIT_TRACKING = "data/participant_visit_tracking.xlsx"
CLAIMS_DB = "data/claims_db.xlsx"
STUDY_CAPS = "data/studies_caps.xlsx"
RECEIPT_FOLDER = "data/receipts"

#os.makedirs(RECEIPT_FOLDER, exist_ok=True)
os.makedirs("data/receipts", exist_ok=True)
os.makedirs("data/pdfs",     exist_ok=True)

# Load study caps (as a dictionary of dictionaries)
def load_study_caps():
    if not os.path.exists(STUDY_CAPS):
        return {}

    df = pd.read_excel(STUDY_CAPS, sheet_name=None)
    caps_dict = {}
    for study, sheet in df.items():
        caps_dict[study] = {row[0]: row[1] for row in sheet.values}
        if 'total' not in caps_dict[study]:
            caps_dict[study]['total'] = sum(caps_dict[study].values())
    return caps_dict
from urllib.parse import quote_plus

def get_google_maps_url(origin, destination):
    """
    Returns a Google Maps directions URL from origin to destination.
    """
    return f"https://www.google.com/maps/dir/?api=1&origin={quote_plus(origin)}&destination={quote_plus(destination)}"

# List participants for a given study
def get_study_participants(study_name):
    if not os.path.exists(VISIT_TRACKING):
        return []
    xls = pd.ExcelFile(VISIT_TRACKING)
    return [sheet for sheet in xls.sheet_names if study_name.lower() in sheet.lower()]

# Load visit records for a participant
def get_participant_visits(participant_id):
    if not os.path.exists(VISIT_TRACKING):
        return pd.DataFrame()
    return pd.read_excel(VISIT_TRACKING, sheet_name=participant_id)

# Save a visit claim to the main claims database
def save_visit_data(participant_id, visit_number, visit_date, location, distance,
                    km_amount, parking, meal, caregiver, subvisit,
                    air, accom, receipts, approved, status, notes,
                    submitted_by, maps_url, visit_duration):

    # Handle caregiver/subvisit duplication logic here for total claimed
    total = km_amount + parking + meal
    if caregiver:
        total *= 2
    if subvisit:
        total += (air + accom) * (2 if caregiver else 1)

    claim = {
        "Participant ID": participant_id,
        "Visit Number": visit_number,
        "Visit Date": visit_date,
        "Visit Location": location,
        "Visit Duration (hrs)": visit_duration,
        "Distance (km)": distance,
        "Kilometre Reimbursement": km_amount,
        "Parking": parking,
        "Meal": meal,
        "Caregiver Present": caregiver,
        "Sub-Visit Imaging?": subvisit,  # ✅ matches admin.py
        "Air Travel": air,
        "Accommodation": accom,
        "Total Claimed (est.)": total,
        "Submitted By": submitted_by,
        "Status": str(status or "Submitted"),                     # ✅ critical for admin view
        "Admin Approved": approved,
        "Notes": notes or "",
        "Google Maps Link": maps_url,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save receipts
    receipt_links = []
    if receipts:
        for file in receipts:
            filename = f"{participant_id}_{visit_number}_{file.name}"
            path = os.path.join(RECEIPT_FOLDER, filename)
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            receipt_links.append(path)
    claim["Receipt Files"] = ", ".join(receipt_links) if receipt_links else ""

    # Append to claims DB
    if os.path.exists(CLAIMS_DB):
        db = pd.read_excel(CLAIMS_DB)
        db = pd.concat([db, pd.DataFrame([claim])], ignore_index=True)
    else:
        db = pd.DataFrame([claim])

    db.to_excel(CLAIMS_DB, index=False)
