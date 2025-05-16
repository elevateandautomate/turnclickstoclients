"""
Machine learning module for form field recognition

This module provides functionality to:
1. Extract features from form fields
2. Train a classifier to recognize field types
3. Save and load trained models
4. Predict field types based on field attributes
"""

import os
import pickle
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
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

class FormFieldClassifier:
    """Machine learning classifier for form fields"""
    
    def __init__(self, model_path: str = 'form_field_model.pkl'):
        """Initialize the classifier
        
        Args:
            model_path: Path to save/load the model
        """
        self.model_path = model_path
        self.vectorizer = None
        self.classifier = None
        self.is_trained = False
        
        # Try to load an existing model
        if os.path.exists(model_path):
            self.load_model()
    
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
        
        # Combine all text features for easier vectorization
        features['all_text'] = ' '.join([
            features['id_text'],
            features['name_text'],
            features['class_text'],
            features['type_text'],
            features['placeholder_text'],
            features['label_text'],
            features['aria_label_text']
        ])
        
        return features
    
    def prepare_training_data(self, fields: List[Dict[str, Any]]) -> Tuple[List[Dict[str, str]], List[str]]:
        """Prepare training data from field examples
        
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
                
            field_features = self.extract_features(field)
            features.append(field_features)
            labels.append(field['type'])
        
        return features, labels
    
    def train(self, fields: List[Dict[str, Any]], test_size: float = 0.2) -> Dict[str, Any]:
        """Train the classifier on field examples
        
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
        
        # Create and fit vectorizer
        self.vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 2), min_df=2)
        X = self.vectorizer.fit_transform(text_features)
        
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=test_size, random_state=42)
        
        # Train classifier
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.classifier.fit(X_train, y_train)
        
        # Evaluate on test set
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Save the trained model
        self.is_trained = True
        self.save_model()
        
        return {
            'accuracy': accuracy,
            'report': report,
            'num_samples': len(features),
            'num_features': X.shape[1]
        }
    
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
        prediction = self.classifier.predict(X)[0]
        
        return prediction
    
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
    
    def save_model(self) -> None:
        """Save the trained model to disk"""
        if not self.is_trained:
            return
        
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'classes': self.classifier.classes_
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self) -> bool:
        """Load a trained model from disk
        
        Returns:
            True if model was loaded successfully
        """
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.classifier = model_data['classifier']
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            self.is_trained = False
            return False

# Function to collect field data from a form
def collect_field_data(driver, form_element) -> List[Dict[str, Any]]:
    """Collect data about fields in a form for training
    
    Args:
        driver: Selenium WebDriver instance
        form_element: Form element to analyze
        
    Returns:
        List of field dictionaries with attributes
    """
    fields = []
    
    # Collect input fields
    input_elements = form_element.find_elements_by_tag_name('input')
    for input_el in input_elements:
        field = {
            'tag_name': 'input',
            'type': input_el.get_attribute('type'),
            'id': input_el.get_attribute('id'),
            'name': input_el.get_attribute('name'),
            'class': input_el.get_attribute('class'),
            'placeholder': input_el.get_attribute('placeholder'),
            'aria-label': input_el.get_attribute('aria-label')
        }
        
        # Try to find associated label
        label_for = None
        if field['id']:
            label_elements = driver.execute_script(
                f"return document.querySelectorAll('label[for=\"{field['id']}\"]');"
            )
            if label_elements and len(label_elements) > 0:
                label_for = label_elements[0].text
        
        field['label'] = label_for
        fields.append(field)
    
    # Collect textareas
    textarea_elements = form_element.find_elements_by_tag_name('textarea')
    for textarea_el in textarea_elements:
        field = {
            'tag_name': 'textarea',
            'id': textarea_el.get_attribute('id'),
            'name': textarea_el.get_attribute('name'),
            'class': textarea_el.get_attribute('class'),
            'placeholder': textarea_el.get_attribute('placeholder'),
            'aria-label': textarea_el.get_attribute('aria-label')
        }
        
        # Try to find associated label
        label_for = None
        if field['id']:
            label_elements = driver.execute_script(
                f"return document.querySelectorAll('label[for=\"{field['id']}\"]');"
            )
            if label_elements and len(label_elements) > 0:
                label_for = label_elements[0].text
        
        field['label'] = label_for
        fields.append(field)
    
    # Collect selects
    select_elements = form_element.find_elements_by_tag_name('select')
    for select_el in select_elements:
        field = {
            'tag_name': 'select',
            'id': select_el.get_attribute('id'),
            'name': select_el.get_attribute('name'),
            'class': select_el.get_attribute('class'),
            'aria-label': select_el.get_attribute('aria-label')
        }
        
        # Try to find associated label
        label_for = None
        if field['id']:
            label_elements = driver.execute_script(
                f"return document.querySelectorAll('label[for=\"{field['id']}\"]');"
            )
            if label_elements and len(label_elements) > 0:
                label_for = label_elements[0].text
        
        field['label'] = label_for
        fields.append(field)
    
    return fields
