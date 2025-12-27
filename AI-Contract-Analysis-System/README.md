# AI Contract Analysis & Risk Detection System

LexiGuard is a production-ready, AI-powered system for analyzing legal contracts, detecting risks, and generating compliance reports.

## Features

- **Document Processing**: Support for PDF and DOCX files.
- **AI Risk Detection**: Hybrid approach using Keyword Matching and Logistic Regression (TF-IDF).
- **Clause Analysis**: NLP-based segmentation of contract clauses.
- **Risk Scoring**: Automated scoring (0-100) based on risk severity.
- **Duplicate Detection**: Prevents re-analysis of the same document using SHA256 hashing.
- **Audit Logging**: Tracks all user actions and system errors.
- **Report Generation**: Export analysis results to PDF.
- **Admin Dashboard**: View audit logs and manage system settings.

## Tech Stack

- **Language**: Python 3.10+
- **UI**: Streamlit
- **NLP**: spaCy, scikit-learn
- **Parsing**: pdfplumber, python-docx
- **Database**: Firebase Firestore (with local Mock fallback)

## Project Structure

```
AI-Contract-Analysis-System/
│
├── contracts/          # Directory for storing uploaded contracts (optional)
├── models/             # ML models storage
├── reports/            # Generated PDF reports
│
├── app.py              # Streamlit UI Entry Point
├── contract_parser.py  # Document parsing logic
├── risk_engine.py      # AI Risk Analysis Engine
├── nlp_processor.py    # NLP Utilities (spaCy)
├── firebase_config.py  # Firebase Configuration
├── utils.py            # Helper functions (PDF gen, Logging)
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

## Setup & Installation

### 1. Prerequisites
- Python 3.10 or higher
- pip

### 2. Installation

1. Clone the repository or navigate to the project directory:
   ```bash
   cd AI-Contract-Analysis-System
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

### 3. Firebase Configuration (Optional)
To use real Firebase Firestore:
1. Generate a Service Account Key from Firebase Console -> Project Settings -> Service Accounts.
2. Save the JSON file as `serviceAccountKey.json` in the project root.
3. If not provided, the system defaults to **Mock Mode** (in-memory storage) for local testing.

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

- **Analysis Tab**: Upload a contract (PDF/DOCX) to analyze risks.
- **History Tab**: View previously analyzed contracts.
- **Admin Tab**: Login (Password: `admin123`) to view audit logs.

## API (Optional)

A Flask backend can be added to expose `risk_engine.py` as a REST API. Currently, the Streamlit app interacts directly with the Python modules for a seamless local experience.

## Contributing

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request
