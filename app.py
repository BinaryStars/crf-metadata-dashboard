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
    tab1, tab2, tab3, tab4 = st.tabs(["Adverse Events", "Demographics", "Laboratory", "Non-Compliant Example"])
    with tab1:
        st.subheader("Adverse Events Records")
        st.dataframe(filled_ae)
    with tab2:
        st.subheader("Demographics Records")
        st.dataframe(filled_demo)
    with tab3:
        st.subheader("Laboratory Records")
        st.dataframe(filled_lab)
    with tab4:
        st.subheader("Non-Compliant Sample Records")
        st.dataframe(noncompliant)

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

    def highlight_noncompliant(val, allowed):
        return f"color: red; font-weight: bold" if val not in allowed else ""

    def show_noncompliant(df, column, allowed_terms):
        if column in df.columns:
            df_copy = df[["SUBJID", column]].copy()
            suggestions = []

            allowed_terms_lower = [term.lower() for term in allowed_terms]
            allowed_term_map = dict(zip(allowed_terms_lower, allowed_terms))

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
        show_noncompliant(unmatched_ae, "AEDECOD", controlled_terms["AEDECOD"])

    st.subheader("Check SEX (Demographics)")
    unmatched_sex = noncompliant[~noncompliant["SEX"].isin(get_allowed_terms("SEX"))]
    if unmatched_sex.empty:
        st.success("All SEX entries are compliant.")
    else:
        st.warning("Non-compliant SEX entries with suggestions:")
        show_noncompliant(unmatched_sex, "SEX", controlled_terms["SEX"])

    st.subheader("Check LABTEST (Lab Data)")
    unmatched_labtest = noncompliant[~noncompliant["LABTEST"].isin(get_allowed_terms("LABTEST"))]
    if unmatched_labtest.empty:
        st.success("All LABTEST entries are compliant.")
    else:
        st.warning("Non-compliant LABTEST entries with suggestions:")
        show_noncompliant(unmatched_labtest, "LABTEST", controlled_terms["LABTEST"])
