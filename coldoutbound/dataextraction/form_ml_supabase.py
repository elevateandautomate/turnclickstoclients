"""
Machine learning classifier for form fields with Supabase storage
"""

import os
import json
import pickle
import base64
from typing import Dict, List, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# Field types we want to recognize
FIELD_TYPES = [
    'first_name',
    'last_name',
    'full_name',
    'email',
    'phone',
    'company',
    'message',
    'subject',
    'address',
    'city',
    'state',
    'zip',
    'country',
    'website',
    'date',
    'time',
    'checkbox',
    'radio',
    'dropdown',
    'submit',
    'unknown'
]

class FormFieldClassifier:
    """Machine learning classifier for form fields with Supabase storage"""

    def __init__(self, supabase_client=None, model_name: str = 'form_field_classifier'):
        """Initialize the classifier

        Args:
            supabase_client: Supabase client instance
            model_name: Name of the model in the database
        """
        self.supabase = supabase_client
        self.model_name = model_name
        self.vectorizer = None
        self.classifier = None
        self.is_trained = False

        # For local development fallback
        self.model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{model_name}.pkl")

        # Try to load an existing model
        if self.supabase:
            # Try to load from Supabase first
            if not self.load_model_from_supabase():
                # If not found in Supabase, try local file
                self.load_model_from_file()
        else:
            print("Warning: No Supabase client provided. Using local file storage.")
            self.load_model_from_file()

    def load_model_from_supabase(self) -> bool:
        """Load the model from Supabase

        Returns:
            True if model was loaded successfully, False otherwise
        """
        try:
            # Get the latest version of the model
            response = self.supabase.table('contact_bot_brain') \
                .select('model_data, version') \
                .eq('model_name', self.model_name) \
                .order('version', desc=True) \
                .limit(1) \
                .execute()

            if response.data and len(response.data) > 0:
                # Decode the model data from base64
                model_data_base64 = response.data[0]['model_data']
                model_data_bytes = base64.b64decode(model_data_base64)

                # Load the model from bytes
                model_dict = pickle.loads(model_data_bytes)
                self.vectorizer = model_dict['vectorizer']
                self.classifier = model_dict['classifier']
                self.is_trained = True

                print(f"Loaded model '{self.model_name}' (version {response.data[0]['version']}) from Supabase")
                return True
            else:
                print(f"No model '{self.model_name}' found in Supabase")
                return False
        except Exception as e:
            print(f"Error loading model from Supabase: {e}")
            return False

    def save_model_to_supabase(self) -> bool:
        """Save the trained model to Supabase

        Returns:
            True if model was saved successfully, False otherwise
        """
        if not self.is_trained or not self.supabase:
            print("Model not trained or no Supabase client provided")
            return False

        try:
            # Serialize the model to bytes
            model_dict = {
                'vectorizer': self.vectorizer,
                'classifier': self.classifier
            }
            model_bytes = pickle.dumps(model_dict)

            # Encode as base64 for storage
            model_base64 = base64.b64encode(model_bytes).decode('utf-8')

            # Get the current version
            response = self.supabase.table('contact_bot_brain') \
                .select('version') \
                .eq('model_name', self.model_name) \
                .order('version', desc=True) \
                .limit(1) \
                .execute()

            current_version = 0
            if response.data and len(response.data) > 0:
                current_version = response.data[0]['version']

            # Insert new version
            self.supabase.table('contact_bot_brain').insert({
                'model_name': self.model_name,
                'model_data': model_base64,
                'version': current_version + 1,
                'updated_at': 'now()'
            }).execute()

            print(f"Saved model '{self.model_name}' (version {current_version + 1}) to Supabase")
            return True
        except Exception as e:
            print(f"Error saving model to Supabase: {e}")
            # Fallback to local file
            self.save_model_to_file()
            return False

    def load_model_from_file(self) -> bool:
        """Load the model from local file (fallback method)"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_dict = pickle.load(f)
                    self.vectorizer = model_dict['vectorizer']
                    self.classifier = model_dict['classifier']
                    self.is_trained = True
                    print(f"Loaded model from local file {self.model_path}")
                    return True
            else:
                print(f"No model file found at {self.model_path}")
                return False
        except Exception as e:
            print(f"Error loading model from file: {e}")
            return False

    def save_model_to_file(self) -> bool:
        """Save the model to local file (fallback method)"""
        if not self.is_trained:
            print("Model not trained yet")
            return False

        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'vectorizer': self.vectorizer,
                    'classifier': self.classifier
                }, f)
            print(f"Saved model to local file {self.model_path}")
            return True
        except Exception as e:
            print(f"Error saving model to file: {e}")
            return False

    def extract_features(self, field: Dict[str, Any]) -> Dict[str, str]:
        """Extract features from a form field

        Args:
            field: Dictionary with field attributes

        Returns:
            Dictionary with extracted features
        """
        # Extract text features from field attributes
        features = {
            'id_text': field.get('id', '').lower(),
            'name_text': field.get('name', '').lower(),
            'class_text': field.get('class', '').lower(),
            'type_text': field.get('type', '').lower(),
            'placeholder_text': field.get('placeholder', '').lower(),
            'label_text': field.get('label', '').lower(),
            'aria_label_text': field.get('aria-label', '').lower(),
            'tag_name': field.get('tag_name', '').lower()
        }

        # Combine all text features for better vectorization
        all_text = ' '.join(features.values())
        features['all_text'] = all_text

        return features

    def train(self, training_data: List[Dict[str, Any]], field_types: List[str]) -> None:
        """Train the classifier on labeled data

        Args:
            training_data: List of dictionaries with field attributes
            field_types: List of field type labels corresponding to training_data
        """
        if not training_data or not field_types:
            print("No training data provided")
            return

        # Extract features from training data
        X_text = []
        for field in training_data:
            features = self.extract_features(field)
            X_text.append(features['all_text'])

        # Create vectorizer and transform text features
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5))
        X = self.vectorizer.fit_transform(X_text)

        # Train classifier
        self.classifier = RandomForestClassifier(n_estimators=100)
        self.classifier.fit(X, field_types)

        self.is_trained = True

        # Save the model
        if self.supabase:
            self.save_model_to_supabase()
        else:
            self.save_model_to_file()

    def predict(self, field: Dict[str, Any]) -> str:
        """Predict the type of a form field

        Args:
            field: Dictionary with field attributes

        Returns:
            Predicted field type
        """
        if not self.is_trained:
            return 'unknown'

        # Extract features
        field_features = self.extract_features(field)
        text_feature = field_features['all_text']

        # Vectorize
        X = self.vectorizer.transform([text_feature])

        # Predict
        return self.classifier.predict(X)[0]

    def predict_proba(self, field: Dict[str, Any]) -> Dict[str, float]:
        """Predict probabilities for each field type

        Args:
            field: Dictionary with field attributes

        Returns:
            Dictionary mapping field types to probabilities
        """
        if not self.is_trained:
            return {'unknown': 1.0}

        # Extract features
        field_features = self.extract_features(field)
        text_feature = field_features['all_text']

        # Vectorize
        X = self.vectorizer.transform([text_feature])

        # Predict probabilities
        probas = self.classifier.predict_proba(X)[0]

        # Map to field types
        result = {}
        for i, field_type in enumerate(self.classifier.classes_):
            result[field_type] = probas[i]

        return result

    def add_training_example(self, field_attributes: Dict[str, Any], field_type: str, source: str = None, success: bool = True) -> bool:
        """Add a new training example to the database

        Args:
            field_attributes: Dictionary with field attributes
            field_type: The correct field type
            source: Source of the example (e.g., website URL)
            success: Whether the form submission was successful

        Returns:
            True if example was added successfully, False otherwise
        """
        if not self.supabase:
            print("No Supabase client provided")
            return False

        try:
            self.supabase.table('contact_bot_brain').insert({
                'model_name': self.model_name,
                'field_attributes': json.dumps(field_attributes),
                'field_type': field_type,
                'source': source,
                'success': success
            }).execute()

            print(f"Added new training example for field type '{field_type}'")
            return True
        except Exception as e:
            print(f"Error adding training example: {e}")
            return False

    def retrain_with_all_data(self) -> bool:
        """Retrain the model with all available training data from Supabase

        Returns:
            True if model was retrained successfully, False otherwise
        """
        if not self.supabase:
            print("No Supabase client provided")
            return False

        try:
            # Get all successful training examples
            response = self.supabase.table('contact_bot_brain') \
                .select('field_attributes, field_type') \
                .eq('success', True) \
                .execute()

            if not response.data or len(response.data) == 0:
                print("No training data found in Supabase")
                return False

            # Prepare training data
            training_data = []
            field_types = []

            for example in response.data:
                field_attributes = json.loads(example['field_attributes'])
                training_data.append(field_attributes)
                field_types.append(example['field_type'])

            # Train the model
            self.train(training_data, field_types)

            print(f"Retrained model with {len(training_data)} examples from Supabase")
            return True
        except Exception as e:
            print(f"Error retraining model: {e}")
            return False
