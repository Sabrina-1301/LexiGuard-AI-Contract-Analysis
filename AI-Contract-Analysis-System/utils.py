import hashlib
import logging
import os
from fpdf import FPDF
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def compute_file_hash(file_bytes):
    """
    Computes SHA256 hash of file content for duplicate detection.
    """
    return hashlib.sha256(file_bytes).hexdigest()

def generate_pdf_report(analysis_result, output_path):
    """
    Generates a PDF report from the analysis result.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Contract Risk Analysis Report", ln=True, align='C')
    pdf.ln(10)
    
    # Metadata
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(200, 10, txt=f"Overall Risk Score: {analysis_result.get('risk_score', 'N/A')}", ln=True)
    pdf.ln(10)
    
    # Risks
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Identified Risks", ln=True)
    pdf.set_font("Arial", size=12)
    
    risks = analysis_result.get('risks', [])
    if not risks:
        pdf.cell(200, 10, txt="No significant risks detected.", ln=True)
    else:
        for risk in risks:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=f"- {risk['type']} ({risk['level']})", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 5, txt=f"  Clause: {risk['clause'][:100]}...")
            pdf.multi_cell(0, 5, txt=f"  Explanation: {risk['explanation']}")
            pdf.ln(5)
            
    try:
        pdf.output(output_path)
        return output_path
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        return None

def log_audit_event(db, user, action, details):
    """
    Logs an audit event to Firestore (or mock).
    """
    try:
        db.collection('audit_logs').add({
            'user': user,
            'action': action,
            'details': details,
            'timestamp': datetime.now()
        })
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")
