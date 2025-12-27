from flask import Flask, request, jsonify
from nlp_processor import NLPProcessor
from risk_engine import RiskEngine
from firebase_config import db
from datetime import datetime
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
nlp = NLPProcessor()
risk_engine = RiskEngine()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "LexiGuard API"})

@app.route('/analyze', methods=['POST'])
def analyze_contract():
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400

        raw_text = data['text']
        filename = data.get('filename', 'api_upload.txt')

        # Clean and Segment
        clean_text = nlp.clean_text(raw_text)
        clauses = nlp.segment_clauses(clean_text)

        # Analyze Risk
        analysis_result = risk_engine.analyze_contract(clauses)

        # Store Results
        contract_data = {
            "filename": filename,
            "timestamp": datetime.now(),
            "risk_score": analysis_result['risk_score'],
            "risks": analysis_result['risks'],
            "summary": analysis_result['summary'],
            "source": "api"
        }
        
        _, doc_ref = db.collection('contracts').add(contract_data)
        
        return jsonify({
            "success": True,
            "risk_score": analysis_result['risk_score'],
            "summary": analysis_result['summary'],
            "details": analysis_result['risks'],
            "id": doc_ref.id
        })

    except Exception as e:
        logger.error(f"API Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
