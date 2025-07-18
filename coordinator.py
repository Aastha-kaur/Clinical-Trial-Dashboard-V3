import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.data_io import (
    get_study_participants,
    get_participant_visits,
    save_visit_data,
    load_study_caps,
    get_google_maps_url
)


def coordinator_view(user):
    st.markdown(f"### Welcome {user['name']} ({user['role']})")
    st.write("📅 Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    caps = load_study_caps()

    study = st.selectbox("Select Study", caps.keys())
    if not study:
        st.info("Please select a study to continue.")
        return

    study_cap = caps[study]
    st.write("🧾 **Study Cap Rules**:")
    for k, v in study_cap.items():
        st.write(f"- {k}: ${v}")

    participants = get_study_participants(study)
    if not participants:
        st.warning("No participants found for this study.")
        return

    participant = st.selectbox("Select Participant", participants)
    if not participant:
        return

    visit_df = get_participant_visits(participant)
    visit_number = st.selectbox("Select Visit", visit_df['Visit number'].tolist())

    if visit_number:
        visit_info = visit_df[visit_df['Visit number'] == visit_number].iloc[0]
        with st.form(f"visit_form_{visit_number}"):
            st.subheader(f"Visit #{visit_number} for {participant}")
            date = st.date_input("Visit Date", visit_info['visit date'])
            location = st.text_input("Visit Location", visit_info['visit location'])
            address = st.text_input("Participant Address", visit_info.get('address', 'Enter address'))
            duration = st.number_input("Visit Duration (hours)", min_value=0.0, step=0.5)

            # Distance and Google Maps
            #distance_km = calculate_distance(address, location)
            #maps_url = get_google_maps_url(address, location)
            #st.write(f"Distance: **{distance_km:.2f} km** [📍 Maps Link]({maps_url})")
            from utils.data_io import get_google_maps_url

            maps_url = get_google_maps_url(address, location)
            st.markdown(f"📍 [Open Google Maps for Distance Check]({maps_url})")

            # Let coordinator manually enter the distance
            distance_km = st.number_input("Distance (km)", min_value=0.0, step=0.1)
            km_reimb = round(distance_km * 0.44, 2)


            # Editable fields
            #km_reimb = round(distance_km * 0.44, 2)
            km_reimb = st.number_input("Kilometre Reimbursement (AUD)", value=km_reimb)
            parking = st.number_input("Parking Allowance", value=visit_info.get('parking allowance', 0.0))
            meal = st.number_input("Meal Allowance", value=visit_info.get('meal allowance', 0.0))

            # Upload receipts
            uploaded_files = st.file_uploader("Upload Receipts", accept_multiple_files=True)

            # Caregiver checkbox
            caregiver = st.checkbox("Caregiver/Support Person Present")

            # Sub-visit (air travel + accommodation)
            subvisit = st.checkbox("Did this visit involve air travel for imaging/scanning in Melbourne/Sydney?")
            air_amount, accom_amount = 0.0, 0.0
            if subvisit:
                air_amount = st.number_input("Air Travel Allowance", min_value=0.0)
                accom_amount = st.number_input("Accommodation Allowance", min_value=0.0)

            # Submit Claim
            submit = st.form_submit_button("Submit Claim for Approval")
            if submit:
                total_claim = km_reimb + parking + meal
                notes = ""
                if caregiver:
                    total_claim *= 2
                if subvisit:
                    extra = air_amount + accom_amount
                    total_claim += (extra * (2 if caregiver else 1))

                if total_claim > study_cap['total']:
                    notes = f"⚠ Claimed amount ${total_claim:.2f} exceeds cap of ${study_cap['total']}. Cap applied. Remaining to be approved by sponsor: ${total_claim - study_cap['total']:.2f}."
                    total_claim = study_cap['total']

                # Save claim
                save_visit_data(
                    participant_id=participant,
                    visit_number=visit_number,
                    visit_date=str(date),
                    location=location,
                    distance=distance_km,
                    km_amount=km_reimb,
                    parking=parking,
                    meal=meal,
                    caregiver=caregiver,
                    subvisit=subvisit,
                    air=air_amount,
                    accom=accom_amount,
                    receipts=uploaded_files,
                    approved=False,
                    status='Submitted',
                    notes=notes,
                    submitted_by=user['email'],
                    maps_url=maps_url,
                    visit_duration=duration
                )

                st.success("✅ Claim submitted successfully!")
                if notes:
                    st.warning(notes)
