import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

# Path to service account key
# User needs to place 'serviceAccountKey.json' in the root or config folder
SERVICE_ACCOUNT_KEY = 'serviceAccountKey.json'

class MockFirestore:
    """
    In-memory mock for Firestore when no credentials are provided.
    Allows the app to run locally for demonstration purposes.
    """
    def __init__(self):
        self._data = {
            'contracts': {},
            'risk_analysis': {},
            'audit_logs': {}
        }
        print("WARNING: Running in Mock Firestore mode. Data will not be persisted.")

    def collection(self, name):
        return MockCollection(self._data, name)

class MockCollection:
    def __init__(self, db_data, name):
        self.db_data = db_data
        self.name = name
        if name not in self.db_data:
            self.db_data[name] = {}

    def document(self, doc_id=None):
        if doc_id is None:
            import uuid
            doc_id = str(uuid.uuid4())
        return MockDocument(self.db_data[self.name], doc_id)

    def add(self, data):
        import uuid
        doc_id = str(uuid.uuid4())
        data['id'] = doc_id
        data['timestamp'] = datetime.now()
        self.db_data[self.name][doc_id] = data
        return None, MockDocument(self.db_data[self.name], doc_id)
    
    def stream(self):
        for doc_id, data in self.db_data[self.name].items():
            yield MockDocumentSnapshot(doc_id, data)

class MockDocument:
    def __init__(self, collection_data, doc_id):
        self.collection_data = collection_data
        self.doc_id = doc_id

    def set(self, data, merge=False):
        if merge and self.doc_id in self.collection_data:
            self.collection_data[self.doc_id].update(data)
        else:
            self.collection_data[self.doc_id] = data
            
    def get(self):
        data = self.collection_data.get(self.doc_id)
        if data:
            return MockDocumentSnapshot(self.doc_id, data)
        return MockDocumentSnapshot(self.doc_id, None, exists=False)

class MockDocumentSnapshot:
    def __init__(self, doc_id, data, exists=True):
        self.id = doc_id
        self._data = data
        self.exists = exists

    def to_dict(self):
        return self._data

def initialize_firebase():
    """
    Initializes Firebase app.
    Returns a Firestore client (real or mock).
    """
    try:
        if os.path.exists(SERVICE_ACCOUNT_KEY):
            cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
            # Check if app is already initialized to avoid errors on reload
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("SUCCESS: Connected to Firebase Firestore.")
            return db
        else:
            # Fallback to mock if no key found
            print(f"NOTICE: {SERVICE_ACCOUNT_KEY} not found. Using MockFirestore.")
            return MockFirestore()
    except Exception as e:
        print(f"ERROR: Failed to initialize Firebase: {e}. Using MockFirestore.")
        return MockFirestore()

# Initialize on module load or call explicitly
db = initialize_firebase()
