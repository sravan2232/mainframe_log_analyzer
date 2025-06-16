import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mainframe Log Analyzer", layout="centered")
st.title("🧠 Mainframe Log Analyzer")
st.write("Upload a mainframe SYSOUT or ABEND log to get categorized error analysis and suggested fixes.")

# Upload
uploaded_file = st.file_uploader("📤 Upload your .txt log file", type=["txt"])

# Rules
rules = {
    "S0C7": ("COBOL", "Data exception — check numeric fields or uninitialized variables."),
    "S0C4": ("COBOL", "Protection exception — check array bounds, null pointer."),
    "SQLCODE = -911": ("DB2", "Deadlock or timeout — check concurrent access."),
    "IGD17272I": ("SMS/Storage", "Dataset not found — check DISP or deletion."),
    "IGD104I": ("SMS/Storage", "Unallocated DDNAME — ensure it exists in JCL."),
    "IEC141I": ("JCL", "Open error — check file DISP or unit."),
    "IEB3270E": ("JCL", "PDS member missing — verify member name or allocation.")
}

category_map = {
    "JCL": ["IEC141I", "IEB3270E"],
    "COBOL": ["S0C7", "S0C4"],
    "DB2": ["SQLCODE = -911"],
    "SMS/Storage": ["IGD17272I", "IGD104I"]
}

selected_category = st.sidebar.multiselect("📂 Filter by Category", list(category_map.keys()))

def category_filter(line):
    if not selected_category:
        return True
    return any(code in line for cat in selected_category for code in category_map[cat])

# Analyze
results = []
if uploaded_file:
    st.subheader("🔍 Analysis Results")
    lines = uploaded_file.read().decode("utf-8").splitlines()
    for line in lines:
        if not category_filter(line):
            continue
        matched = False
        for pattern, (category, fix) in rules.items():
            if pattern in line:
                results.append({"Log": line, "Category": category, "Fix": fix})
                matched = True
                break
        if not matched:
            results.append({"Log": line, "Category": "Unknown", "Fix": "No known fix. Manual check required."})

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)

        # CSV download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv, file_name="log_analysis.csv", mime="text/csv")

        # Visualization
        st.subheader("📊 Error Category Distribution")
        fig, ax = plt.subplots()
        df['Category'].value_counts().plot(kind='bar', ax=ax, color='skyblue')
        ax.set_ylabel("Count")
        ax.set_xlabel("Category")
        ax.set_title("Error Categories Found")
        st.pyplot(fig)