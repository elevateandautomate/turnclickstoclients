"""
Enhanced machine learning classifier for form fields with advanced NLP capabilities
"""

import os
import json
import pickle
import base64
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

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

class EnhancedFormFieldClassifier:
    """Enhanced machine learning classifier for form fields with advanced NLP capabilities"""
    
    def __init__(self, supabase_client=None, model_path: str = 'enhanced_form_field_model.pkl'):
        """Initialize the classifier
        
        Args:
            supabase_client: Optional Supabase client for storing/retrieving model data
            model_path: Path to save/load the model (used if supabase_client is None)
        """
        self.model_path = model_path
        self.supabase = supabase_client
        self.vectorizer = None
        self.classifier = None
        self.is_trained = False
        self.form_fingerprints = {}  # Store form fingerprints for quick recognition
        
        # Try to load an existing model
        if self.supabase:
            self._load_model_from_supabase()
        elif os.path.exists(model_path):
            self._load_model_from_file()
    
    def extract_features(self, field: Dict[str, Any]) -> Dict[str, str]:
        """Extract features from a form field with enhanced context awareness
        
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
            'tag_name': field.get('tag_name', '').lower(),
            'parent_class': field.get('parent_class', '').lower(),
            'sibling_fields': field.get('sibling_fields', '').lower(),
            'field_position': field.get('field_position', '').lower(),
            'form_type': field.get('form_type', '').lower()
        }
        
        # Combine all text features for vectorization
        all_text = ' '.join([
            features['id_text'],
            features['name_text'],
            features['class_text'],
            features['type_text'],
            features['placeholder_text'],
            features['label_text'],
            features['aria_label_text'],
            features['tag_name'],
            features['parent_class'],
            features['sibling_fields'],
            features['field_position'],
            features['form_type']
        ])
        
        features['all_text'] = all_text
        
        return features
    
    def prepare_training_data(self, fields: List[Dict[str, Any]]) -> Tuple[List[Dict[str, str]], List[str]]:
        """Prepare training data from field examples with enhanced context
        
        Args:
            fields: List of field dictionaries with attributes and known type
            
        Returns:
            Tuple of (features, labels)
        """
        features = []
        labels = []
        
        for field in fields:
            if 'type' not in field:
                continue  # Skip fields without a known type
                
            # Add contextual information if available
            if 'form_url' in field and 'field_index' in field:
                # Extract form type from URL
                form_type = self._extract_form_type_from_url(field['form_url'])
                field['form_type'] = form_type
                
                # Add field position information
                field['field_position'] = f"position_{field['field_index']}"
            
            field_features = self.extract_features(field)
            features.append(field_features)
            labels.append(field['type'])
        
        return features, labels
    
    def _extract_form_type_from_url(self, url: str) -> str:
        """Extract form type from URL for contextual understanding
        
        Args:
            url: Form URL
            
        Returns:
            Form type string
        """
        url_lower = url.lower()
        
        if 'contact' in url_lower:
            return 'contact_form'
        elif 'register' in url_lower or 'signup' in url_lower:
            return 'registration_form'
        elif 'login' in url_lower or 'signin' in url_lower:
            return 'login_form'
        elif 'checkout' in url_lower or 'payment' in url_lower:
            return 'payment_form'
        elif 'subscribe' in url_lower or 'newsletter' in url_lower:
            return 'subscription_form'
        else:
            return 'unknown_form'
    
    def train(self, fields: List[Dict[str, Any]], test_size: float = 0.2) -> Dict[str, Any]:
        """Train the classifier on field examples with enhanced features
        
        Args:
            fields: List of field dictionaries with attributes and known type
            test_size: Proportion of data to use for testing
            
        Returns:
            Dictionary with training results
        """
        # Prepare training data
        features, labels = self.prepare_training_data(fields)
        
        if not features:
            raise ValueError("No valid training data provided")
        
        # Extract text features for vectorization
        text_features = [f['all_text'] for f in features]
        
        # Create and fit vectorizer with improved parameters
        self.vectorizer = TfidfVectorizer(
            analyzer='word', 
            ngram_range=(1, 3),  # Use up to trigrams for better context
            min_df=2,
            max_features=5000  # Limit features to prevent overfitting
        )
        X = self.vectorizer.fit_transform(text_features)
        
        # Split data into training and testing sets
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=test_size, random_state=42)
        
        # Train classifier with improved parameters
        self.classifier = RandomForestClassifier(
            n_estimators=200,  # More trees for better accuracy
            max_depth=20,      # Deeper trees for complex patterns
            min_samples_split=5,
            random_state=42
        )
        self.classifier.fit(X_train, y_train)
        
        # Evaluate on test set
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Save the trained model
        self.is_trained = True
        self._save_model()
        
        return {
            'accuracy': accuracy,
            'report': report,
            'num_samples': len(features),
            'num_features': X.shape[1]
        }
    
    def predict(self, field: Dict[str, Any]) -> str:
        """Predict the type of a form field with enhanced context awareness
        
        Args:
            field: Dictionary with field attributes
            
        Returns:
            Predicted field type
        """
        if not self.is_trained:
            return 'unknown'
        
        # Add contextual information if available
        if 'form_url' in field:
            form_type = self._extract_form_type_from_url(field['form_url'])
            field['form_type'] = form_type
        
        # Extract features
        field_features = self.extract_features(field)
        text_feature = field_features['all_text']
        
        # Vectorize
        X = self.vectorizer.transform([text_feature])
        
        # Predict
        prediction = self.classifier.predict(X)[0]
        
        return prediction
    
    def predict_proba(self, field: Dict[str, Any]) -> Dict[str, float]:
        """Predict probabilities for each field type with enhanced confidence
        
        Args:
            field: Dictionary with field attributes
            
        Returns:
            Dictionary mapping field types to probabilities
        """
        if not self.is_trained:
            return {'unknown': 1.0}
        
        # Add contextual information if available
        if 'form_url' in field:
            form_type = self._extract_form_type_from_url(field['form_url'])
            field['form_type'] = form_type
        
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
    
    def _save_model(self) -> bool:
        """Save the trained model to Supabase or file"""
        if self.supabase:
            return self._save_model_to_supabase()
        else:
            return self._save_model_to_file()
    
    def _save_model_to_file(self) -> bool:
        """Save the trained model to a file"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'vectorizer': self.vectorizer,
                    'classifier': self.classifier,
                    'is_trained': self.is_trained
                }, f)
            print(f"Model saved to {self.model_path}")
            return True
        except Exception as e:
            print(f"Error saving model to file: {e}")
            return False
    
    def _save_model_to_supabase(self) -> bool:
        """Save the trained model to Supabase"""
        try:
            # Serialize the model
            model_data = pickle.dumps({
                'vectorizer': self.vectorizer,
                'classifier': self.classifier,
                'is_trained': self.is_trained
            })
            
            # Encode as base64
            model_base64 = base64.b64encode(model_data).decode('utf-8')
            
            # Save to Supabase
            self.supabase.table('contact_bot_brain').upsert({
                'id': 'enhanced_form_field_model',
                'model_data': model_base64,
                'updated_at': 'now()'
            }).execute()
            
            print("Model saved to Supabase")
            return True
        except Exception as e:
            print(f"Error saving model to Supabase: {e}")
            return False
    
    def _load_model_from_file(self) -> bool:
        """Load the trained model from a file"""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
                self.vectorizer = model_data['vectorizer']
                self.classifier = model_data['classifier']
                self.is_trained = model_data['is_trained']
            print(f"Model loaded from {self.model_path}")
            return True
        except Exception as e:
            print(f"Error loading model from file: {e}")
            return False
    
    def _load_model_from_supabase(self) -> bool:
        """Load the trained model from Supabase"""
        try:
            # Get model data from Supabase
            response = self.supabase.table('contact_bot_brain').select('model_data').eq('id', 'enhanced_form_field_model').execute()
            
            if response.data and len(response.data) > 0 and response.data[0].get('model_data'):
                # Decode base64
                model_base64 = response.data[0]['model_data']
                model_data = base64.b64decode(model_base64)
                
                # Deserialize the model
                model_dict = pickle.loads(model_data)
                self.vectorizer = model_dict['vectorizer']
                self.classifier = model_dict['classifier']
                self.is_trained = model_dict['is_trained']
                
                print("Model loaded from Supabase")
                return True
            else:
                print("No model found in Supabase")
                return False
        except Exception as e:
            print(f"Error loading model from Supabase: {e}")
            return False
