
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="GiM - Clarity in the Chaos", layout="wide")

st.title("👩‍🍳 GiM - Shift Assistant")
st.subheader("Clarity in the Chaos")

# Load shift log CSV
@st.cache_data
def load_data():
    return pd.read_csv("shift_logs.csv")

df = load_data()

# Extract unique roles
roles = df['role'].dropna().unique().tolist()
selected_role = st.selectbox("Select your role", roles)

# Optional access overview
with st.expander("🔐 Trusted Access Overview"):
    now = pd.Timestamp.now()
    trusted = df[df['temporary_trusted_until'].notna()]
    trusted['temporary_trusted_until'] = pd.to_datetime(trusted['temporary_trusted_until'], errors='coerce')
    active_trusted = trusted[trusted['temporary_trusted_until'] > now]
    if not active_trusted.empty:
        st.markdown("These staff members currently have elevated access:")
        st.dataframe(active_trusted[['staff', 'role', 'temporary_trusted_until']])
    else:
        st.info("No active trusted access currently granted.")

# Show the user their shift digest
if st.button("Show My Briefing"):
    st.markdown(f"### Shift Digest for **{selected_role}**")
    role_data = df[df['role'] == selected_role]

    # Show 3 most recent entries
    latest = role_data.sort_values(by='date', ascending=False).head(3)
    for _, row in latest.iterrows():
        st.write(f"🕒 **{row['date']}** – {row['shift']}")
        st.write(f"👤 **{row['staff']}**")
        st.write(f"📝 {row['notes']}")
        st.markdown("---")

    # Complaint detection
    complaints = role_data[role_data['notes'].str.contains("complain|issue|problem|broken|noise|angry|slow", case=False, na=False)]
    if not complaints.empty:
        st.warning("⚠️ Guest or Ops issues flagged in your recent shifts:")
        for _, row in complaints.iterrows():
            st.write(f"- {row['date']} – {row['notes']}")
    else:
        st.success("✅ No major complaints or issues logged for your role recently.")

    # Loop Agent stub (surface unresolved issues)
    st.markdown("### 📋 Loop Agent Summary")
    recurring = df['notes'].value_counts().reset_index()
    recurring.columns = ['issue', 'count']
    recurring = recurring[recurring['count'] > 1]
    if not recurring.empty:
        st.info("Recurring issues detected:")
        st.dataframe(recurring)
    else:
        st.success("No unresolved repeated issues across logs.")

st.caption("GiM v1.0 – Built with Streamlit")
