# FAIR CRF & Metadata Stewardship Prototype

This Streamlit dashboard demonstrates a prototype system for managing **Case Report Forms (CRFs)** and **clinical metadata** aligned with **FAIR principles**, **CDISC standards**, and **data governance responsibilities**—designed as a mini-project for the *Biomedical Data Stewardship Manager* role at Amgen.

## 🔍 Features

* **CRF Design Templates**: View standard CRFs for Adverse Events (AE), Demographics (DM), and Lab Tests (LB).
* **Metadata Repository**: Curated metadata per domain, including field names, definitions, and controlled terms.
* **Terminology Compliance Checker**: Automatically highlights non-compliant entries using CDISC-controlled terminologies.
* **Indication-Level CRF Library**: Switch between oncology and cardiology-specific CRFs.
* **LLM-Powered Copilot**: An OpenAI-based assistant for answering CRF metadata questions.
* **Governance Request Tracker**: Submit and log requests for metadata changes, with justification and field-level detail.

## 📁 Project Structure

```
crf_metadata_dashboard/
├── app.py                    # Streamlit app
├── crf_metadata_csvs/        # Sample CRF data and metadata
│   ├── crf_ae_sample.csv
│   ├── metadata_repository_sample.csv
│   ├── filled_crf_noncompliant_sample.csv
│   └── cdisc_terminology.csv
└── README.md
```

## 🚀 How to Run

Install dependencies and run the app:

```bash
pip install streamlit pandas openai
streamlit run app.py
```

Set your OpenAI API key in `.streamlit/secrets.toml`:

```toml
[general]
OPENAI_API_KEY = "your_openai_api_key"
```

## 🌐 Live Demo

Hosted on Streamlit Cloud:
👉 [Try the dashboard](https://crf-metadata-dashboard-7nr7eakvhrc2qe8xuvesgb.streamlit.app)

## 👩‍💼 Author

Shima Dastgheib
[LinkedIn](https://www.linkedin.com/in/shima-dastgheib) | [GitHub](https://github.com/BinaryStars)
