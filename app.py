import streamlit as st
import pandas as pd
import requests
import urllib.parse
import difflib
import openai

# Data directory
DATA_DIR = "crf_metadata_csvs/"

# Load data
try:
    crf_ae = pd.read_csv(DATA_DIR + "crf_ae_sample.csv")
    crf_demo = pd.read_csv(DATA_DIR + "crf_demographics_sample.csv")
    crf_lab = pd.read_csv(DATA_DIR + "crf_lab_sample.csv")

    metadata_ae = pd.read_csv(DATA_DIR + "metadata_repository_sample.csv")
    metadata_demo = pd.read_csv(DATA_DIR + "metadata_demographics_sample.csv")
    metadata_lab = pd.read_csv(DATA_DIR + "metadata_lab_sample.csv")

    filled_ae = pd.read_csv(DATA_DIR + "filled_crf_ae_sample.csv")
    filled_demo = pd.read_csv(DATA_DIR + "filled_crf_demographics_sample.csv")
    filled_lab = pd.read_csv(DATA_DIR + "filled_crf_lab_sample.csv")

    noncompliant = pd.read_csv(DATA_DIR + "filled_crf_noncompliant_sample.csv")

    cdisc_terms_df = pd.read_csv(DATA_DIR + "cdisc_terminology.csv")
except FileNotFoundError as e:
    st.error(f"Required file not found: {e.filename}. Please verify that all data files are in the correct location.")
    st.stop()

# Footer
st.markdown("---")
st.caption("Dashboard created by Shima Dastgheib | [LinkedIn](https://www.linkedin.com/in/shima-dastgheib) | [GitHub](https://github.com/BinaryStars/crf-metadata-dashboard)")

# Load partial CDISC terminology
cdisc_terms_df = pd.read_csv(DATA_DIR + "cdisc_terminology.csv")

def get_allowed_terms(codelist):
    if cdisc_terms_df.empty:
        st.warning("CDISC terminology file is empty. Please verify the file contents.")
        return []
    terms = cdisc_terms_df[cdisc_terms_df["CODELIST"] == codelist]["VALUE"].dropna().unique().tolist()
    if not terms:
        st.warning(f"No controlled terms found for CODELIST='{codelist}'.")
    return terms

def show_noncompliant(df, column, allowed_values):
    df_copy = df.copy()
    noncompliant_values = []
    for val in df_copy[column]:
        if pd.isna(val):
            continue
        if val not in allowed_values:
            noncompliant_values.append(val)
    df_copy['NONCOMPLIANT'] = df_copy[column].apply(lambda x: x if x not in allowed_values else '')
    st.dataframe(df_copy.style.applymap(lambda x: 'background-color: red' if x in noncompliant_values else ''))
    if noncompliant_values:
        st.warning(f"Found non-compliant values: {set(noncompliant_values)}")
    else:
        st.success("All values are compliant.")

# Sidebar navigation
st.sidebar.title("CRF Metadata Dashboard")
section = st.sidebar.radio("Select Section", ["Overview", "CRF Structures", "Filled CRFs", "Metadata Repository", "Terminology Compliance", "Indication-Level CRF Library", "CRF Copilot (LLM)", "Governance Requests"])

# Overview
if section == "Overview":
    st.title("FAIR Data Stewardship Prototype")
    st.markdown("""
This dashboard demonstrates key CRF data stewardship responsibilities:

- **Design CRF Templates** for domains like AE, Demographics, and Lab Tests
- **Check Terminology Compliance** using CDISC-controlled terms
- **Curate Metadata** with SME decisions and implementation rules
- **Use LLM Copilot** for expert support on CRF standards
- **Submit Governance Requests** for new fields or standards updates

Navigate tabs to explore each function.
""")


# CRF Structures
elif section == "CRF Structures":
    st.title("CRF Templates by Domain")
    st.subheader("Adverse Events CRF")
    st.dataframe(crf_ae)
    st.subheader("Demographics CRF")
    st.dataframe(crf_demo)
    st.subheader("Lab CRF")
    st.dataframe(crf_lab)

# Filled CRFs
elif section == "Filled CRFs":
    st.title("Sample Completed CRFs")
    st.subheader("Adverse Events")
    st.dataframe(filled_ae)
    st.subheader("Demographics")
    st.dataframe(filled_demo)
    st.subheader("Lab Tests")
    st.dataframe(filled_lab)

# Metadata Repository
elif section == "Metadata Repository":
    st.title("CRF Metadata Repository")
    domain = st.selectbox(
    "Domain",
    ["AE", "DM", "LB", "VS", "MH", "EX", "Custom"],
    index=0,
    help="Select the clinical data domain: AE=Adverse Events, DM=Demographics, LB=Lab Tests, VS=Vital Signs, MH=Medical History, EX=Exposure."
)
    if domain == "AE":
        st.dataframe(metadata_ae)
    elif domain == "DM":
        st.dataframe(metadata_demo)
    elif domain == "LB":
        st.dataframe(metadata_lab)

# Terminology Compliance
elif section == "Terminology Compliance":
    st.title("Terminology Compliance Checker")
    st.subheader("Check AEDECOD (Adverse Events)")
    unmatched_ae = noncompliant["AEDECOD"].dropna()
    show_noncompliant(noncompliant, "AEDECOD", get_allowed_terms("AEDECOD"))

    st.subheader("Check SEX (Demographics)")
    show_noncompliant(noncompliant, "SEX", get_allowed_terms("SEX"))

    st.subheader("Check LABTEST (Lab Tests)")
    show_noncompliant(noncompliant, "LABTEST", get_allowed_terms("LABTEST"))

# Indication-Level CRF Library
elif section == "Indication-Level CRF Library":
    st.title("Indication-Level CRF Library")

    indication = st.selectbox("Select Indication", ["Oncology", "Cardiology"])

    if indication == "Oncology":
        st.subheader("Oncology-specific AE CRF")
        st.markdown("Includes AE severity and treatment-related fields used in oncology trials.")
        oncology_ae = crf_ae.copy()
        if "AESEV" not in oncology_ae.columns:
            oncology_ae["AESEV"] = "MILD"  # Example default
        st.dataframe(oncology_ae)

    elif indication == "Cardiology":
        st.subheader("Cardiology-specific Vital Signs CRF")
        st.markdown("Captures blood pressure, heart rate, and related vitals relevant to cardiology.")
        cardiology_vs = pd.DataFrame({
            "VSDTC": ["2025-07-01"],
            "VSORRES": [120],
            "VSTEST": ["Systolic Blood Pressure"],
            "VSUNIT": ["mmHg"]
        })
        st.dataframe(cardiology_vs)


# CRF Copilot (LLM)
elif section == "CRF Copilot (LLM)":
    st.title("CRF Copilot – LLM-Powered Assistance")
    user_prompt = st.text_input("Ask the Copilot a question (e.g., What metadata should I define for AESEV in an oncology CRF?)")
    if user_prompt:
        with st.spinner("Thinking..."):
            try:
                api_key = st.secrets["OPENAI_API_KEY"]
            except KeyError:
                st.error("OpenAI API key not found. Please add OPENAI_API_KEY to your Streamlit secrets.")
                st.stop()
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a biomedical metadata steward helping design compliant CRFs based on CDISC and FHIR."},
                    {"role": "user", "content": user_prompt}
                ]
            )
            st.markdown("**Response:**")
            st.write(response.choices[0].message.content)

# Governance Requests
elif section == "Governance Requests":
    st.title("CRF Standards Governance Tracker")
    st.markdown("Submit a change request for a CRF standard or term. Track and review governance decisions.")
    with st.form("governance_form"):
        requestor = st.text_input("Your Name", placeholder="e.g., Clinical Data Steward")
        domain = st.selectbox(
    "Domain",
    ["AE", "DM", "LB", "VS", "MH", "EX", "Custom"],
    help="Select the clinical data domain: AE=Adverse Events, DM=Demographics, LB=Lab Tests, VS=Vital Signs, MH=Medical History, EX=Exposure."
)
        field = st.text_input("Field Name", placeholder="e.g., AESEV")
        change_type = st.radio("Change Type", ["Add", "Modify", "Retire"])
        reason = st.text_area("Justification for the Change", placeholder="e.g., AESEV is needed to capture severity in AE records for oncology patients.")
        submitted = st.form_submit_button("Submit Request")
        if submitted:
            st.success("Submitted! Governance team will review this request.")
