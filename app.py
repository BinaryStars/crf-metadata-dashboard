import streamlit as st
import pandas as pd
import requests
import urllib.parse
import difflib

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

# Sidebar navigation
st.sidebar.title("CRF Metadata Dashboard")
section = st.sidebar.radio("Select Section", ["Overview", "CRF Structures", "Filled CRFs", "Metadata Repository", "Terminology Compliance", "Indication-Level CRF Library", "CRF Copilot (LLM)", "Governance Requests"])

# Overview
if section == "Overview":
    st.title("FAIR CRF & Metadata Stewardship Prototype")
    st.markdown("""
    This interactive dashboard simulates the work of a Biomedical Data Steward responsible for end-to-end CRF standards and governance. It demonstrates key responsibilities outlined in industry roles:

    - 📋 **Design Indication-Level CRFs**: Create standardized AE, Lab, and Demographics CRFs tailored to oncology or cardiology.  
      _Shows capability in indication-specific CRF library design aligned with CDISC/CDASH._  
      👉 Try it: Go to the **"Indication-Level CRF Library"** tab and explore or generate a new template.

    - 📚 **Metadata Repository Management**: View curated field metadata with datatype, term list, definitions, and SME decision rationale.  
      _Supports reuse, traceability, and FAIR-compliant stewardship._  
      👉 Try it: Open the **"Metadata Repository"** tab to inspect and search across domains.

    - ✅ **Terminology Compliance Checker**: Identify and suggest fixes for non-compliant values using CDISC-controlled terms.  
      _Enables quality checks and standard adherence across studies._  
      👉 Try it: Use the **"Terminology Compliance"** tab to validate AEDECOD, SEX, and LABTEST values.

    - 🤖 **LLM Copilot for CRFs**: Ask GPT-4 questions like "Why is AEDECOD important?" or "Suggest fields for a hypertension CRF."  
      _Simulates expert consultation and SME hypercare support._  
      👉 Try it: Ask a question in the **"CRF Copilot (LLM)"** tab and see instant feedback.

    - 🔧 **Governance Request Tracker**: Submit and manage change requests (add, retire, or modify CRF terms).  
      _Demonstrates oversight of CRF evolution, versioning, and governance coordination._  
      👉 Try it: Submit a test request in the **"Governance Requests"** tab.

    🧪 **Use Case Example**: You're designing a new oncology trial and want to ensure the AE CRF complies with CDISC standards, documents metadata for future reuse, and logs a new request to add a custom tumor marker field. This tool walks you through the entire workflow.

    This prototype can be extended to support SME review workflows, CDISC–FHIR mappings, and metadata export to RDF or JSON-LD.
    """)

            for val in df_copy[column]:
                val_lower = val.lower()
                matches = difflib.get_close_matches(val_lower, allowed_terms_lower, n=1, cutoff=0.3)
                if matches:
                    suggestions.append(allowed_term_map[matches[0]])
                else:
                    suggestions.append("(no suggestion)")

            df_copy["Suggested Correction"] = suggestions
            styled = df_copy.style.applymap(lambda v: highlight_noncompliant(v, allowed_terms), subset=[column])
            st.dataframe(styled)

    st.subheader("Check AEDECOD (Adverse Events)")
    unmatched_ae = noncompliant[~noncompliant["AEDECOD"].isin(get_allowed_terms("AEDECOD"))]
    if unmatched_ae.empty:
        st.success("All AEDECOD entries are compliant.")
    else:
        st.warning("Non-compliant AEDECOD terms with suggestions:")
        show_noncompliant(unmatched_ae, "AEDECOD", get_allowed_terms("AEDECOD"))

    st.subheader("Check SEX (Demographics)")
    unmatched_sex = noncompliant[~noncompliant["SEX"].isin(get_allowed_terms("SEX"))]
    if unmatched_sex.empty:
        st.success("All SEX entries are compliant.")
    else:
        st.warning("Non-compliant SEX entries with suggestions:")
        show_noncompliant(unmatched_sex, "SEX", get_allowed_terms("SEX"))

    st.subheader("Check LABTEST (Lab Data)")
    unmatched_labtest = noncompliant[~noncompliant["LABTEST"].isin(get_allowed_terms("LABTEST"))]
    if unmatched_labtest.empty:
        st.success("All LABTEST entries are compliant.")
    else:
        st.warning("Non-compliant LABTEST entries with suggestions:")
        show_noncompliant(unmatched_labtest, "LABTEST", get_allowed_terms("LABTEST"))
