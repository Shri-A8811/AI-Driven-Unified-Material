# National Material Master Harmonization Platform
### One Nation – One Material Code

An AI-driven standardization and harmonization framework for Central Public Sector Enterprises (CPSEs) in India (spanning Oil & Gas, Power, Steel, Mining, and Heavy Engineering sectors).

---

## Overview

CPSEs procure and maintain hundreds of thousands of similar or functionally equivalent materials under divergent legacy codes, inconsistent naming schemes, disparate units of measurement (UoM), and isolated enterprise systems.

This platform solves this challenge by implementing an intelligent **National Unified Material Master Framework** capable of:
1. **Multi-CPSE Ingestion & Normalization**: Resolving legacy shorthand, abbreviations, and UoMs.
2. **AI-Powered Deduplication & Matching**: Semantic similarity, vector-cosine matching, and physical constraint verification.
3. **Common National Material Code (CNMC) Generation**: Deterministic, collision-resistant codification based on standardized technical attributes.
4. **Canonical 8-Tuple AI Pipeline**:
   $$\text{CPSE Code} \longrightarrow \text{Standard Description} \longrightarrow \text{Standard Specs} \longrightarrow \text{Classification} \longrightarrow \text{Similar/Equivalent Materials} \longrightarrow \text{Confidence Score} \longrightarrow \text{Common Code (CNMC)} \longrightarrow \text{Approval Status}$$
5. **Human-in-the-Loop Resolution Workbench**: Side-by-side spec comparison and multi-role sign-off (Approver, Technical Reviewer, Data Steward, Admin).
6. **ERP & Governance**: Simulated SAP RFC/BAPI connectors (`BAPI_MATERIAL_GET_DETAIL`, `BAPI_MATERIAL_SAVEDATA` updating `MARA-ZZ_CNMC`), real-time pre-procurement duplication alerts, and a tamper-evident SHA-256 block ledger.

---

## Architecture

```
cpse-material-harmonizer/
├── src/
│   ├── models/
│   │   └── material.py            # Pydantic schemas (Raw, Normalized, TechnicalAttributes, CoreAIOutputTuple)
│   ├── data/
│   │   └── sample_cpse_catalogs.py # Multi-CPSE industrial datasets (IOCL, NTPC, SAIL, BHEL, GAIL)
│   ├── engine/
│   │   ├── preprocessor.py        # Abbreviation expansion & UoM normalization
│   │   ├── attribute_extractor.py # Regex & rule-based physical attribute extractor
│   │   ├── matcher.py             # Vector-cosine, lexical, & constraint matching
│   │   ├── clusterer.py           # Duplicate item clusterer & collaborative savings calculator
│   │   ├── code_generator.py      # Deterministic Common National Material Code (CNMC) generator
│   │   ├── mapping_registry.py    # Bidirectional CPSE <-> CNMC mapping & CSV export
│   │   ├── pipeline_output.py     # Canonical 8-tuple transformation engine
│   │   └── ingestion.py           # Ingestion coordinator
│   ├── taxonomy/
│   │   └── unspcs_rules.py        # 4-tier UNSPSC taxonomy classifier
│   ├── connectors/
│   │   └── sap_mock_connector.py  # SAP BAPI integration & pre-procurement interception
│   ├── governance/
│   │   └── audit_ledger.py        # Cryptographically chained SHA-256 audit ledger
│   └── web/
│       ├── app.py                 # FastAPI REST API backend
│       └── static/
│           ├── index.html         # Executive command portal
│           ├── style.css          # Dual-theme (Light/Dark) design system
│           └── app.js             # Interactive client application
├── tests/                         # Automated test suite (24 passing tests)
├── requirements.txt
└── README.md
```

---

## Quickstart

### 1. Prerequisites
- Python 3.10+
- `pip`

### 2. Installation
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd cpse-material-harmonizer
pip install -r requirements.txt
```

### 3. Run the Development Server
```bash
python -m uvicorn src.web.app:app --host 127.0.0.1 --port 8000 --reload
```
Navigate to **`http://127.0.0.1:8000`** in your browser.

---

## Running Automated Tests

Run the full pytest suite with verbose output:
```bash
python -m pytest tests/ -v
```

All 24 test suites validate:
- Multi-CPSE ingestion and normalization
- Exact and near-duplicate cluster detection
- Rejection of incompatible engineering specifications
- Deterministic CNMC code generation
- REST API analytics, approval workflows, and CSV export
- Tamper-evident cryptographic ledger verification
- SAP RFC/BAPI pre-procurement duplicate alert interception
- Canonical 8-tuple pipeline output integrity

---

## Key Features

- **Dual-Theme Adaptive UI**: Seamless Light and Dark modes with native browser `color-scheme` synchronization.
- **Side-by-Side Spec Comparison**: View raw legacy descriptions alongside normalized physical parameters.
- **Pre-Procurement Duplication Interception**: Alerts CPSE procurement officers before purchase orders are raised for items that already exist across sister CPSEs.
- **Cryptographic Audit Trail**: Every approval, rejection, and mapping reversal is permanently recorded in a SHA-256 chained ledger.
