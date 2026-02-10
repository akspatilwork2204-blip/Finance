import pandas as pd
import streamlit as st

EXCEL_PATH = "Finance.xlsx"

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():

    # ================= CONTRIBUTION SHEET =================
    raw_contribution = pd.read_excel(
        EXCEL_PATH,
        sheet_name="Contribution",
        header=None
    )

    # Data starts from row 3, column E
    contribution_df = raw_contribution.iloc[2:, 4:8]
    contribution_df.columns = [
        "Name",
        "Initial Contribution",
        "Monthly Contribution",
        "Total Contribution"
    ]

    # Drop empty name rows
    contribution_df = contribution_df.dropna(subset=["Name"])

    # Remove embedded header row
    contribution_df = contribution_df[
        contribution_df["Name"].astype(str).str.strip().str.lower() != "name"
    ]

    # Convert numeric columns safely
    numeric_cols = [
        "Initial Contribution",
        "Monthly Contribution",
        "Total Contribution"
    ]

    for col in numeric_cols:
        contribution_df[col] = pd.to_numeric(
            contribution_df[col], errors="coerce"
        )

    # Remove garbage rows (blank / zero rows before actual data)
    contribution_df = contribution_df.dropna(
        subset=["Initial Contribution"]
    )

    # ================= LOAN SHEET =================
    raw_loan = pd.read_excel(
        EXCEL_PATH,
        sheet_name="LoanTakenAndEMIDetails",
        header=None
    )

    # Data starts from row 6, column D
    loan_df = raw_loan.iloc[5:, 3:]
    loan_df = loan_df.dropna(how="all")

    # Rename columns dynamically
    base_cols = ["Name", "Interest", "Amount", "Duration"]
    month_cols = [
        f"Month_{i}"
        for i in range(1, loan_df.shape[1] - 3)
    ]

    loan_df.columns = base_cols + month_cols

    # Clean loan rows
    loan_df = loan_df.dropna(subset=["Name", "Amount", "Duration"])

    return contribution_df, loan_df


# ---------------- MAIN APP ----------------
contribution_df, loan_df = load_data()

st.title("📊 Finance Dashboard")

# ================= CONTRIBUTION SUMMARY =================
st.header("💼 Contribution Summary")

contribution_summary = (
    contribution_df
    .groupby("Name", as_index=False)
    .agg({
        "Initial Contribution": "sum",
        "Monthly Contribution": "sum",
        "Total Contribution": "sum"
    })
)

st.dataframe(contribution_summary, use_container_width=True)

# ================= LOAN DETAILS =================
st.header("💰 Loan Taken & EMI Details")

loan_rows = []

for _, row in loan_df.iterrows():
    duration = int(row["Duration"])

    record = {
        "Name": row["Name"],
        "Amount Taken": row["Amount"],
        "Duration": duration
    }

    for i in range(1, duration + 1):
        col = f"Month_{i}"
        record[col] = row[col] if col in loan_df.columns else None

    loan_rows.append(record)

loan_display_df = pd.DataFrame(loan_rows)

st.dataframe(loan_display_df, use_container_width=True)
