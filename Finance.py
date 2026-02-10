import streamlit as st
import pandas as pd

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Finance Tracker", layout="wide")
st.title("💰 Finance Contribution & Loan Tracker")

# 🔹 Default local file path
DEFAULT_PATH = "/Users/saaaga/Downloads/codeBase/Finance.xlsx"


# =====================================================
# MODE SELECTION
# =====================================================
mode = st.radio(
    "Select Data Source:",
    ["Use Local File", "Upload Excel File"]
)

if mode == "Use Local File":
    file_source = DEFAULT_PATH
    st.info(f"Using local file: {DEFAULT_PATH}")
else:
    uploaded_file = st.file_uploader(
        "Upload Finance Excel file",
        type=["xlsx"]
    )
    if uploaded_file is None:
        st.stop()
    file_source = uploaded_file


# =====================================================
# LOAD CONTRIBUTION SHEET
# =====================================================
@st.cache_data
def load_contribution(file):
    raw = pd.read_excel(
        file,
        sheet_name="Contribution",
        header=None,
        engine="openpyxl"
    )

    df = raw.iloc[:, 4:].copy()

    # Detect header row automatically
    header_row_idx = df[df.iloc[:, 0].notna()].index[0]
    headers = df.loc[header_row_idx].tolist()

    df = df.loc[header_row_idx + 1:].copy()
    df.columns = headers

    df = df.dropna(subset=[headers[0]])
    df = df[df[headers[0]].astype(str).str.strip() != ""]

  df = df.rename(columns={headers[0]: "Name"})

    return df.reset_index(drop=True)


# =====================================================
# LOAD LOAN SHEET
# =====================================================
@st.cache_data
def load_loans(file):
    raw = pd.read_excel(
        file,
        sheet_name="LoanTakenAndEMIDetails",
        header=None,
        engine="openpyxl"
    )

    header_row = raw.iloc[5, 3:].tolist()
    df = raw.iloc[6:, 3:].copy()
    df.columns = header_row

    # Force fixed columns by position
    rename_map = {
        df.columns[0]: "Name",
        df.columns[1]: "AmountTaken",
        df.columns[2]: "Duration",
        df.columns[3]: "MonthlyPrincipal",
    }

    df = df.rename(columns=rename_map)

 df = df.dropna(subset=["Name"])
    df = df[df["Name"].astype(str).str.strip() != ""]
    df = df[df["Name"] != "Name"]

    return df.reset_index(drop=True)


# =====================================================
# LOAD DATA
# =====================================================
try:
    contribution_df = load_contribution(file_source)
    loan_df = load_loans(file_source)
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()


# =====================================================
# DISPLAY CONTRIBUTION
# =====================================================
st.subheader("📊 Contribution Summary")
st.dataframe(contribution_df, use_container_width=True)


# =====================================================
# DISPLAY LOAN DETAILS
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

    for i in range(1, duration + 1):
        col = f"Month_{i}"
        if col in loan_df.columns:
            row_data[col] = row[col]
 loan_rows.append(row_data)

final_loan_df = pd.DataFrame(loan_rows)

st.dataframe(final_loan_df, use_container_width=True)

st.success("✅ Data loaded successfully")



    df = df.rename(columns={headers[0]: "Name"})
