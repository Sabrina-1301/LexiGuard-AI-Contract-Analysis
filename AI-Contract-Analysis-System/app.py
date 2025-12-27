import streamlit as st
import os
from datetime import datetime
import tempfile
from contract_parser import ContractParser
from nlp_processor import NLPProcessor
from risk_engine import RiskEngine
from firebase_config import db
from utils import generate_pdf_report, log_audit_event, compute_file_hash

# Initialize components
@st.cache_resource
def get_components():
    return {
        "parser": ContractParser(),
        "nlp": NLPProcessor(),
        "risk_engine": RiskEngine()
    }

components = get_components()

def main():
    st.set_page_config(page_title="LexiGuard AI Contract Analysis", layout="wide")
    st.title("LexiGuard AI - Contract Risk Analysis System")

    # Sidebar for Navigation
    menu = ["Analysis", "History", "Admin"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Analysis":
        show_analysis_page()
    elif choice == "History":
        show_history_page()
    elif choice == "Admin":
        show_admin_page()

def show_analysis_page():
    st.header("Upload Contract for Analysis")
    uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])

    if uploaded_file is not None:
        if st.button("Analyze Contract"):
            with st.spinner("Processing document..."):
                try:
                    # 1. Parse File
                    raw_text = components["parser"].parse_uploaded_file(uploaded_file)
                    
                    # 2. Check for Duplicates
                    file_hash = compute_file_hash(uploaded_file.getvalue())
                    existing_docs = db.collection('contracts').where('hash', '==', file_hash).stream()
                    duplicate = None
                    for doc in existing_docs:
                        duplicate = doc.to_dict()
                        break
                    
                    if duplicate:
                        st.warning(f"Duplicate contract detected! Analyzed on {duplicate['timestamp']}")
                        st.write("Fetching previous results...")
                        display_results(duplicate)
                        return

                    # 3. Clean and Segment
                    clean_text = components["nlp"].clean_text(raw_text)
                    clauses = components["nlp"].segment_clauses(clean_text)
                    
                    # 4. Analyze Risk
                    analysis_result = components["risk_engine"].analyze_contract(clauses)
                    
                    # 5. Store Results
                    contract_data = {
                        "filename": uploaded_file.name,
                        "hash": file_hash,
                        "timestamp": datetime.now(),
                        "risk_score": analysis_result['risk_score'],
                        "risks": analysis_result['risks'],
                        "summary": analysis_result['summary'],
                        "full_text_snippet": clean_text[:500]
                    }
                    
                    _, doc_ref = db.collection('contracts').add(contract_data)
                    log_audit_event(db, "user", "analyze_contract", f"Analyzed {uploaded_file.name}")
                    
                    # 6. Display Results
                    st.success("Analysis Complete!")
                    display_results(contract_data)

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    log_audit_event(db, "system", "error", str(e))

def display_results(data):
    st.subheader(f"Risk Score: {data['risk_score']}/100")
    
    # Visual gauge (simulated with progress bar)
    st.progress(min(data['risk_score'], 100))
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("Summary")
        st.write(data['summary'])
    
    with col2:
        st.write("File Details")
        st.write(f"Filename: {data.get('filename', 'Unknown')}")
        st.write(f"Date: {data.get('timestamp', 'Unknown')}")

    st.subheader("Detailed Risk Analysis")
    risks = data.get('risks', [])
    
    if not risks:
        st.success("No high risks detected.")
    else:
        for risk in risks:
            with st.expander(f"{risk['level']} Risk: {risk['type']}"):
                st.write(f"**Clause:** {risk['clause']}")
                st.write(f"**Explanation:** {risk['explanation']}")
                st.write(f"**Score:** {risk['score']:.2f}")

    # Export Report
    if st.button("Download PDF Report"):
        report_path = f"reports/report_{data['hash']}.pdf"
        # Ensure reports dir exists
        if not os.path.exists("reports"):
            os.makedirs("reports")
            
        generated_path = generate_pdf_report(data, report_path)
        if generated_path:
            with open(generated_path, "rb") as f:
                st.download_button(
                    label="Download PDF",
                    data=f,
                    file_name="risk_report.pdf",
                    mime="application/pdf"
                )

def show_history_page():
    st.header("Contract History")
    docs = db.collection('contracts').stream()
    
    data = []
    for doc in docs:
        d = doc.to_dict()
        data.append({
            "Filename": d.get('filename'),
            "Date": d.get('timestamp'),
            "Risk Score": d.get('risk_score')
        })
    
    if data:
        st.dataframe(data)
    else:
        st.info("No contracts found in history.")

def show_admin_page():
    st.header("Admin Dashboard")
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "admin123": # Simple auth for demo
        st.success("Access Granted")
        
        st.subheader("Audit Logs")
        logs = db.collection('audit_logs').stream()
        log_data = []
        for log in logs:
            l = log.to_dict()
            log_data.append(l)
        
        if log_data:
            st.dataframe(log_data)
        else:
            st.info("No audit logs available.")
            
        st.subheader("Manage Risk Keywords")
        st.write("Feature coming soon: Add/Remove keywords from Firestore.")
    elif password:
        st.error("Invalid Password")

if __name__ == "__main__":
    main()
