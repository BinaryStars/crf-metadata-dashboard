import streamlit as st
import pandas as pd
import requests
import urllib.parse

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

# Mock SDTM/CDISC terminology
controlled_terms = {
    "AEDECOD": ["HEADACHE", "NAUSEA", "FATIGUE"],
    "SEX": ["MALE", "FEMALE"],
    "LABTEST": ["HEMOGLOBIN", "GLUCOSE", "WBC"]
}

# Sidebar navigation
st.sidebar.title("CRF Metadata Dashboard")
section = st.sidebar.radio("Select Section", ["Overview", "CRF Structures", "Filled CRFs", "Metadata Repository", "ClinicalTrials.gov Explorer", "Terminology Compliance"])

# Overview
if section == "Overview":
    st.title("FAIR CRF & Metadata Stewardship Prototype")
    st.markdown("""
    This dashboard simulates a clinical metadata governance framework:
    - Standardized CRFs for Adverse Events, Demographics, and Lab Results
    - Metadata repositories with terminology, data types, and change tracking
    - Filled CRFs simulating study data
    - Integration with ClinicalTrials.gov for external metadata alignment
    - SDTM/CDISC terminology validation to support data governance
    """)

# CRF Structures
elif section == "CRF Structures":
    st.title("CRF Templates")
    tab1, tab2, tab3 = st.tabs(["Adverse Events", "Demographics", "Laboratory"])
    with tab1:
        st.subheader("Adverse Events CRF")
        st.dataframe(crf_ae)
    with tab2:
        st.subheader("Demographics CRF")
        st.dataframe(crf_demo)
    with tab3:
        st.subheader("Laboratory CRF")
        st.dataframe(crf_lab)

# Filled CRFs
elif section == "Filled CRFs":
    st.title("Filled CRF Data")
    tab1, tab2, tab3 = st.tabs(["Adverse Events", "Demographics", "Laboratory"])
    with tab1:
        st.subheader("Adverse Events Records")
        st.dataframe(filled_ae)
    with tab2:
        st.subheader("Demographics Records")
        st.dataframe(filled_demo)
    with tab3:
        st.subheader("Laboratory Records")
        st.dataframe(filled_lab)

# Metadata
elif section == "Metadata Repository":
    st.title("Metadata Repositories")
    tab1, tab2, tab3 = st.tabs(["Adverse Events", "Demographics", "Laboratory"])
    with tab1:
        st.subheader("AE Metadata")
        st.dataframe(metadata_ae)
    with tab2:
        st.subheader("Demographics Metadata")
        st.dataframe(metadata_demo)
    with tab3:
        st.subheader("Lab Metadata")
        st.dataframe(metadata_lab)

# ClinicalTrials.gov Integration
elif section == "ClinicalTrials.gov Explorer":
    st.title("ClinicalTrials.gov Metadata Explorer")
    st.markdown("Search trials to cross-reference CRF content with real-world study metadata.")

    query = st.text_input("Search ClinicalTrials.gov (e.g., diabetes, COVID-19, oncology):")
    if query:
        search_url = f"https://clinicaltrials.gov/search?cond={urllib.parse.quote(query)}"
        st.markdown(f"[Click here to view ClinicalTrials.gov results for '{query}']({search_url})")
        st.markdown("(This opens the official site in a new tab.)")

# Terminology Compliance
elif section == "Terminology Compliance":
    st.title("Terminology Compliance Check")
    st.markdown("This tool checks whether filled CRF terms align with SDTM/CDISC controlled terminology.")

    def check_terms(df, column, allowed_terms):
        if column in df.columns:
            return df[~df[column].isin(allowed_terms)]
        return pd.DataFrame()

    st.subheader("Check AEDECOD (Adverse Events)")
    unmatched_ae = check_terms(filled_ae, "AEDECOD", controlled_terms["AEDECOD"])
    if unmatched_ae.empty:
        st.success("All AEDECOD entries are compliant.")
    else:
        st.warning("Non-compliant AEDECOD terms:")
        st.dataframe(unmatched_ae[["SUBJID", "AEDECOD"]])

    st.subheader("Check SEX (Demographics)")
    unmatched_sex = check_terms(filled_demo, "SEX", controlled_terms["SEX"])
    if unmatched_sex.empty:
        st.success("All SEX entries are compliant.")
    else:
        st.warning("Non-compliant SEX entries:")
        st.dataframe(unmatched_sex[["SUBJID", "SEX"]])

    st.subheader("Check LABTEST (Lab Data)")
    unmatched_labtest = check_terms(filled_lab, "LABTEST", controlled_terms["LABTEST"])
    if unmatched_labtest.empty:
        st.success("All LABTEST entries are compliant.")
    else:
        st.warning("Non-compliant LABTEST entries:")
        st.dataframe(unmatched_labtest[["SUBJID", "LABTEST"]])
