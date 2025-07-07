import streamlit as st
import pandas as pd
import requests
import urllib.parse
import difflib
import openai

# Data directory
DATA_DIR = "crf_metadata_csvs/"

# Load data
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

# Load full CDISC terminology
cdisc_terms_df = pd.read_csv(DATA_DIR + "cdisc_terminology.csv")

def get_allowed_terms(codelist):
    return cdisc_terms_df[cdisc_terms_df["CODELIST"] == codelist]["VALUE"].dropna().unique().tolist()

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
    st.title("FAIR CRF & Metadata Stewardship Prototype")
    st.markdown("""
    This interactive dashboard simulates the work of a Biomedical Data Steward responsible for end-to-end CRF standards and governance. It demonstrates key responsibilities outlined in industry roles:

    - **Design Indication-Level CRFs**: Create standardized AE, Lab, and Demographics CRFs tailored to oncology or cardiology.  
      _Shows capability in indication-specific CRF library design aligned with CDISC/CDASH._  
      👉 Try it: Go to the **"Indication-Level CRF Library"** tab and explore or generate a new template.

    - **Metadata Repository Management**: View curated field metadata with datatype, term list, definitions, and SME decision rationale.  
      _Supports reuse, traceability, and FAIR-compliant stewardship._  
      👉 Try it: Open the **"Metadata Repository"** tab to inspect and search across domains.

    - **Terminology Compliance Checker**: Identify and suggest fixes for non-compliant values using CDISC-controlled terms.  
      _Enables quality checks and standard adherence across studies._  
      👉 Try it: Use the **"Terminology Compliance"** tab to validate AEDECOD, SEX, and LABTEST values.

    - **LLM Copilot for CRFs**: Ask GPT-4 questions like "Why is AEDECOD important?" or "Suggest fields for a hypertension CRF."  
      _Simulates expert consultation and SME hypercare support._  
      👉 Try it: Ask a question in the **"CRF Copilot (LLM)"** tab and see instant feedback.

    - **Governance Request Tracker**: Submit and manage change requests (add, retire, or modify CRF terms).  
      _Demonstrates oversight of CRF evolution, versioning, and governance coordination._  
      👉 Try it: Submit a test request in the **"Governance Requests"** tab.

    **Use Case Example**: You're designing a new oncology trial and want to ensure the AE CRF complies with CDISC standards, documents metadata for future reuse, and logs a new request to add a custom tumor marker field. This tool walks you through the entire workflow.

    This prototype can be extended to support SME review workflows, CDISC–FHIR mappings, and metadata export to RDF or JSON-LD.
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
    domain = st.selectbox("Select Domain", ["AE", "DM", "LB"])
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
        st.write("Example Oncology AE CRF")
        st.dataframe(crf_ae)
    elif indication == "Cardiology":
        st.write("Example Cardiology Demographics CRF")
        st.dataframe(crf_demo)

# CRF Copilot (LLM)
elif section == "CRF Copilot (LLM)":
    st.title("CRF Copilot – LLM-Powered Assistance")
    user_prompt = st.text_input("Ask the Copilot a question (e.g., Why is AEDECOD used?)")
    if user_prompt:
        with st.spinner("Thinking..."):
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
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
        requestor = st.text_input("Your Name", placeholder="e.g., Dr. Jane Smith")
        domain = st.selectbox(
    "Domain",
    ["AE", "DM", "LB", "VS", "MH", "EX", "Custom"],
    help="Select the clinical data domain: AE=Adverse Events, DM=Demographics, LB=Lab Tests, VS=Vital Signs, MH=Medical History, EX=Exposure."
)
        field = st.text_input("Field Name", placeholder="e.g., TUMOR_MARKER")
        change_type = st.radio("Change Type", ["Add", "Modify", "Retire"])
        reason = st.text_area("Justification for the Change", placeholder="Explain why this change is needed for clinical or regulatory purposes")
        submitted = st.form_submit_button("Submit Request")
        if submitted:
            st.success("Submitted! Governance team will review this request.")
