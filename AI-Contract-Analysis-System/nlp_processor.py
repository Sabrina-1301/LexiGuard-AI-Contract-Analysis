import spacy
import re
import logging

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self, model_name="en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            logger.warning(f"spaCy model '{model_name}' not found. Attempting to download...")
            from spacy.cli import download
            download(model_name)
            self.nlp = spacy.load(model_name)
        
    def clean_text(self, text):
        """
        Cleans extracted text by removing excessive whitespace and artifacts.
        """
        # Remove multiple newlines and extra spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that are likely artifacts (keep basic punctuation)
        # text = re.sub(r'[^\w\s.,;:!?()"\'-]', '', text) 
        return text.strip()

    def segment_clauses(self, text):
        """
        Segments text into clauses or sentences.
        For legal docs, often numbered lists or paragraphs are clauses.
        Here we use spaCy sentence segmentation as a baseline.
        """
        doc = self.nlp(text)
        clauses = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
        return clauses

    def extract_entities(self, text):
        """
        Extracts named entities (ORG, DATE, MONEY, GPE, etc.)
        """
        doc = self.nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

if __name__ == "__main__":
    # Test
    processor = NLPProcessor()
    sample = "This Agreement is made on 2023-01-01 between Company A and Company B."
    print(processor.extract_entities(sample))
