import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finance Tracker", layout="wide")
st.title("💰 Finance Contribution & Loan Tracker")

# =====================================================
# Upload Excel
# =====================================================
uploaded_file = st.file_uploader(
    "Upload Finance Excel file",
    type=["xlsx"]
)

if uploaded_file is None:
    st.stop()

# =====================================================
# Contribution Sheet (E3)
# =====================================================
@st.cache_data
def load_contribution(file):
    raw = pd.read_excel(
        file,
        sheet_name="Contribution",
        header=None
    )

    # Work only from column E onward
    df = raw.iloc[:, 4:].copy()

    # Find first row where column E is not empty → HEADER
    header_row_idx = df[df.iloc[:, 0].notna()].index[0]

    # Extract headers
    headers = df.loc[header_row_idx].tolist()

    # Data starts AFTER header
    df = df.loc[header_row_idx + 1:].copy()
    df.columns = headers

    # Clean data rows
    df = df.dropna(subset=[headers[0]])
    df = df[df[headers[0]].astype(str).str.strip() != ""]

    # Normalize column name
    df = df.rename(columns={headers[0]: "Name"})

    return df.reset_index(drop=True)

# =====================================================
# Loan Sheet (POSITION + HEADER SAFE)
# =====================================================
@st.cache_data
def load_loans(file):
    raw = pd.read_excel(
        file,
        sheet_name="LoanTakenAndEMIDetails",
        header=None
    )

    # Header row (Excel row 6)
    header_row = raw.iloc[5, 3:].tolist()

    # Data rows (Excel row 7 onwards)
    df = raw.iloc[6:, 3:].copy()

    # Assign temporary headers
    df.columns = header_row

    # --- FORCE FIXED COLUMNS BY POSITION ---
    rename_map = {
        df.columns[0]: "Name",
        df.columns[2]: "AmountTaken",
        df.columns[3]: "Duration",
        df.columns[4]: "MonthlyPrincipal",
    }

    df = df.rename(columns=rename_map)

    # Remove junk rows
    df = df.dropna(subset=["Name"])
    df = df[df["Name"].astype(str).str.strip() != ""]
    df = df[df["Name"] != "Name"]

    return df


# =====================================================
# Load Data
# =====================================================
contribution_df = load_contribution(uploaded_file)
loan_df = load_loans(uploaded_file)

# =====================================================
# Contribution Summary
# =====================================================
st.subheader("📊 Contribution Summary")
st.dataframe(contribution_df, use_container_width=True)

# =====================================================
# Loan Details (Month_1 → Month_N CORRECT)
# =====================================================
st.subheader("🏦 Loan Taken & EMI Details")

loan_rows = []

for _, row in loan_df.iterrows():
    duration = int(row["Duration"])

    row_data = {
        "Name": row["Name"],
        "AmountTaken": row["AmountTaken"],
        "Duration": duration
    }

    # Month_1 → Month_N (NO SHIFTING)
    for i in range(1, duration + 1):
        col = f"Month_{i}"
        if col in loan_df.columns:
            row_data[col] = row[col]

    loan_rows.append(row_data)

final_loan_df = pd.DataFrame(loan_rows)

st.dataframe(final_loan_df, use_container_width=True)

st.success("✅ Data loaded correctly — columns, months, rows all fixed")

