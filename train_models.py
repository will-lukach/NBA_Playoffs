import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class ModelTrainer:
    def __init__(self):
        self.models = {
            'logistic': LogisticRegression(random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'svm': SVC(probability=True, random_state=42)
        }
        self.trained_models = {}

    def train_models(self, X_train, y_train, conference):
        """Train all models for a specific conference"""
        conference_models = {}
        
        for name, model in self.models.items():
            print(f"Training {name} for {conference} conference...")
            model.fit(X_train, y_train)
            conference_models[name] = model
        
        self.trained_models[conference] = conference_models
        return conference_models

    def evaluate_models(self, X_test, y_test, conference):
        """Evaluate all models for a specific conference"""
        results = {}
        
        for name, model in self.trained_models[conference].items():
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred)
            
            results[name] = {
                'accuracy': accuracy,
                'report': report
            }
            
            print(f"\nResults for {name} ({conference} conference):")
            print(f"Accuracy: {accuracy:.4f}")
            print("Classification Report:")
            print(report)
        
        return results

    def predict_playoffs(self, X, conference):
        """Make playoff predictions using all models"""
        predictions = {}
        probabilities = {}
        
        for name, model in self.trained_models[conference].items():
            predictions[name] = model.predict(X)
            probabilities[name] = model.predict_proba(X)[:, 1]
        
        # Average predictions across models
        avg_proba = np.mean([prob for prob in probabilities.values()], axis=0)
        final_predictions = (avg_proba > 0.5).astype(int)
        
        return predictions, probabilities, final_predictions, avg_proba

    def save_models(self, output_dir="models"):
        """Save trained models to disk"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for conference, models in self.trained_models.items():
            conf_dir = os.path.join(output_dir, conference.lower())
            if not os.path.exists(conf_dir):
                os.makedirs(conf_dir)
            
            for name, model in models.items():
                model_path = os.path.join(conf_dir, f"{name}.joblib")
                joblib.dump(model, model_path)
                print(f"Saved {name} model for {conference} conference to {model_path}")

    def load_models(self, input_dir="models"):
        """Load trained models from disk"""
        self.trained_models = {}
        
        for conference in ['East', 'West']:
            conf_dir = os.path.join(input_dir, conference.lower())
            self.trained_models[conference] = {}
            
            for name in self.models.keys():
                model_path = os.path.join(conf_dir, f"{name}.joblib")
                if os.path.exists(model_path):
                    self.trained_models[conference][name] = joblib.load(model_path)
                    print(f"Loaded {name} model for {conference} conference from {model_path}")

if __name__ == "__main__":
    from preprocess_data import DataPreprocessor
    
    # Initialize preprocessor and load data
    preprocessor = DataPreprocessor()
    data = preprocessor.load_data("NBA_data/historical_data.csv")
    processed_data = preprocessor.preprocess(data)
    
    # Split data by conference
    east_data, west_data = preprocessor.split_conferences(processed_data)
    
    # Initialize trainer
    trainer = ModelTrainer()
    
    # Train and evaluate models for each conference
    for conf_data, conf_name in [(east_data, 'East'), (west_data, 'West')]:
        # Prepare train/test data
        X_train, X_test, y_train, y_test = preprocessor.prepare_train_test(conf_data)
        
        # Train models
        trainer.train_models(X_train, y_train, conf_name)
        
        # Evaluate models
        trainer.evaluate_models(X_test, y_test, conf_name)
    
    # Save models
    trainer.save_models()
    print("\nModel training complete!")