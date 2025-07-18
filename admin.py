import streamlit as st
import pandas as pd
import os
from utils.data_io import CLAIMS_DB, RECEIPT_FOLDER
from utils.pdf_gen import generate_pdf

def admin_view(user):
    st.markdown(f"### Welcome {user['name']} ({user['role']})")
    st.subheader("Submitted Claims")

    if not os.path.exists(CLAIMS_DB):
        st.warning("No claims submitted yet.")
        return

    df = pd.read_excel(CLAIMS_DB)
    if df.empty:
        st.info("No submitted records.")
        return

    for i, row in df.iterrows():
        if row["Status"] not in ["Submitted", "Approved"]:
            continue

        with st.expander(f"Visit #{row['Visit Number']} | {row['Participant ID']} ({row['Visit Date']})"):
            st.markdown(f"**Location:** {row['Visit Location']}")
            st.markdown(f"**Duration:** {row['Visit Duration (hrs)']} hrs")
            st.markdown(f"**Distance:** {row['Distance (km)']} km")

            st.markdown("### Reimbursement:")
            km = st.number_input("KM Amount", value=row['Kilometre Reimbursement'], key=f"km_{i}")
            parking = st.number_input("Parking", value=row['Parking'], key=f"park_{i}")
            meal = st.number_input("Meal", value=row['Meal'], key=f"meal_{i}")
            air = st.number_input("Air Travel", value=row['Air Travel'], key=f"air_{i}")
            accom = st.number_input("Accommodation", value=row['Accommodation'], key=f"accom_{i}")

            # Receipt Viewer
            if isinstance(row.get("Receipt Files"), str) and row["Receipt Files"]:
                for file in row["Receipt Files"].split(","):
                    file = file.strip()
                    if os.path.exists(file):
                        st.markdown(f"[📎 View Receipt]({file})")
                    else:
                        st.warning(f"Missing file: {file}")

            caregiver_value = str(row.get('Caregiver Present')).strip().lower()
            subvisit_value = str(row.get('Sub-Visit Imaging')).strip().lower()

            st.markdown(f"**Caregiver Present:** {'Yes' if caregiver_value in ['true', 'yes'] else 'No'}")
            st.markdown(f"**Sub-Visit Imaging:** {'Yes' if subvisit_value in ['true', 'yes'] else 'No'}")

            if pd.notna(row.get('Notes')) and row['Notes']:
                st.warning(row['Notes'])

            claim_id = f"{row['Participant ID']}_{row['Visit Number']}"
            pdf_filename = f"Claim_{claim_id}.pdf"
            pdf_path = os.path.join("data/pdfs", pdf_filename)

            if row["Status"] == "Approved":
                if os.path.exists(pdf_path):
                    st.download_button(
                        label="📄 Download PDF",
                        data=open(pdf_path, 'rb'),
                        file_name=pdf_filename,
                        key=f"download_{i}"
                    )
                else:
                    # Regenerate missing PDF
                    pdf_path = generate_pdf(row)
                    st.download_button(
                        label="📄 Download PDF (Regenerated)",
                        data=open(pdf_path, 'rb'),
                        file_name=os.path.basename(pdf_path),
                        key=f"redownload_{i}"
                    )
            else:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve", key=f"approve_{i}"):
                        df.at[i, 'Status'] = 'Approved'
                        df.at[i, 'Admin Approved'] = True
                        df.at[i, 'Kilometre Reimbursement'] = km
                        df.at[i, 'Parking'] = parking
                        df.at[i, 'Meal'] = meal
                        df.at[i, 'Air Travel'] = air
                        df.at[i, 'Accommodation'] = accom

                        df.to_excel(CLAIMS_DB, index=False)

                        pdf_path = generate_pdf(df.loc[i])
                        st.success("Approved. PDF generated.")
                        st.download_button(
                            label="📄 Download PDF",
                            data=open(pdf_path, 'rb'),
                            file_name=os.path.basename(pdf_path),
                            key=f"pdf_download_{i}"
                        )

                with col2:
                    if st.button("❌ Reject", key=f"reject_{i}"):
                        df.at[i, 'Status'] = 'Rejected'
                        df.at[i, 'Admin Approved'] = False
                        df.to_excel(CLAIMS_DB, index=False)
                        st.error("Rejected.")
