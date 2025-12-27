import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import logging
import pickle
import os

logger = logging.getLogger(__name__)

class RiskEngine:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.risky_keywords = {
            "High": ["indemnify", "liability", "termination", "arbitration", "liquidated damages", "exclusivity"],
            "Medium": ["confidentiality", "warranty", "jurisdiction", "governing law", "auto-renewal"],
            "Low": ["notice", "severability", "amendment", "waiver"]
        }
        # Initialize with a dummy model or load existing
        self._initialize_model()

    def _initialize_model(self):
        """
        Initializes a basic ML model. In a real scenario, this would load a trained model.
        Here we train on a small dummy dataset to ensure the system is 'working'.
        """
        try:
            # Dummy dataset
            data = [
                ("The Provider shall indemnify the Client against all losses.", "High"),
                ("Limitation of Liability: The Provider's liability shall not exceed $1000.", "High"),
                ("This agreement may be terminated by either party with 30 days notice.", "High"),
                ("Any dispute shall be resolved via arbitration in New York.", "High"),
                ("Confidential Information shall not be disclosed to third parties.", "Medium"),
                ("This agreement is governed by the laws of California.", "Medium"),
                ("All notices must be in writing and sent via certified mail.", "Low"),
                ("This contract is renewable automatically unless cancelled.", "Medium"),
                ("The standard warranty period is 12 months.", "Medium"),
                ("If any provision is found invalid, the rest remains in effect.", "Low")
            ]
            df = pd.DataFrame(data, columns=["text", "risk_level"])
            
            self.pipeline = make_pipeline(
                TfidfVectorizer(stop_words='english'),
                LogisticRegression()
            )
            self.pipeline.fit(df['text'], df['risk_level'])
            logger.info("Risk Model initialized and trained on dummy data.")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            self.pipeline = None

    def analyze_clause_risk(self, clause_text):
        """
        Analyzes a single clause and returns risk level and score.
        Uses Hybrid approach: Keyword match + ML prediction.
        """
        risk_level = "Low"
        explanation = "Standard clause."
        score = 0.0

        # 1. Keyword Heuristic (Override)
        text_lower = clause_text.lower()
        for level, keywords in self.risky_keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    risk_level = level
                    explanation = f"Contains high-risk keyword: '{kw}'"
                    if level == "High": score = 0.9
                    elif level == "Medium": score = 0.6
                    else: score = 0.3
                    break
            if score > 0: break

        # 2. ML Prediction (Refinement)
        if self.pipeline:
            try:
                ml_pred = self.pipeline.predict([clause_text])[0]
                ml_proba = self.pipeline.predict_proba([clause_text]).max()
                
                # If keyword didn't catch it but ML did
                if score == 0:
                    risk_level = ml_pred
                    score = ml_proba
                    explanation = f"ML Model detected pattern similar to {risk_level} risk."
            except Exception as e:
                logger.warning(f"ML prediction failed: {e}")

        return {
            "risk_level": risk_level,
            "risk_score": float(score),
            "explanation": explanation
        }

    def analyze_contract(self, clauses):
        """
        Analyzes list of clauses and aggregates risk.
        """
        results = []
        high_risk_count = 0
        total_score = 0
        
        for clause in clauses:
            if not clause.strip(): continue
            analysis = self.analyze_clause_risk(clause)
            if analysis['risk_level'] == 'High':
                high_risk_count += 1
            if analysis['risk_level'] != 'Low': # Only report relevant risks
                results.append({
                    "clause": clause,
                    "level": analysis['risk_level'],
                    "score": analysis['risk_score'],
                    "explanation": analysis['explanation'],
                    "type": "General Risk" # Placeholder for specific risk type classification
                })
            total_score += analysis['risk_score']

        avg_score = total_score / len(clauses) if clauses else 0
        overall_score = min(100, int(avg_score * 100) + (high_risk_count * 5)) # Simple aggregation logic

        return {
            "risks": results,
            "risk_score": overall_score,
            "summary": f"Found {high_risk_count} high-risk clauses."
        }
