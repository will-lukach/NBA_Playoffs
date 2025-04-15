import pandas as pd
import numpy as np
from preprocess_data import DataPreprocessor
from train_models import ModelTrainer
from generate_visualizations import Visualizer
import os

class PlayoffPredictor:
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.trainer = ModelTrainer()
        self.visualizer = Visualizer()
        
        # Create necessary directories
        for dir_name in ['NBA_data', 'models', 'Images']:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

    def update_data(self):
        """Update the dataset with latest NBA data"""
        from nba_scraper_2025 import NBAScraper
        
        # Scrape new data
        scraper = NBAScraper()
        current_data = scraper.get_season_data(2025)
        
        # Save current season data
        current_data.to_csv("NBA_data/current_season.csv", index=False)
        
        # Load and combine with historical data if it exists
        if os.path.exists("NBA_data/historical_data.csv"):
            historical_data = pd.read_csv("NBA_data/historical_data.csv")
            # Remove current year if it exists in historical data
            historical_data = historical_data[historical_data['Year'] != 2025]
            # Combine data
            full_data = pd.concat([historical_data, current_data], ignore_index=True)
            full_data.to_csv("NBA_data/historical_data.csv", index=False)
        else:
            current_data.to_csv("NBA_data/historical_data.csv", index=False)

    def generate_predictions(self):
        """Generate playoff predictions for current season"""
        # Load and preprocess data
        data = self.preprocessor.load_data("NBA_data/historical_data.csv")
        processed_data = self.preprocessor.preprocess(data)
        
        # Split data by conference
        east_data, west_data = self.preprocessor.split_conferences(processed_data)
        
        # Load trained models
        self.trainer.load_models()
        
        predictions = {}
        
        # Generate predictions for each conference
        for conf_data, conf_name in [(east_data, 'East'), (west_data, 'West')]:
            # Get current season data
            current_data = conf_data[conf_data['Year'] == 2025]
            X_current = current_data[self.preprocessor.features]
            teams = current_data['Team']
            
            # Get predictions
            model_predictions, probabilities, final_predictions, avg_proba = \
                self.trainer.predict_playoffs(X_current, conf_name)
            
            # Store predictions
            predictions[conf_name] = {
                'teams': teams.values,
                'probabilities': avg_proba,
                'predictions': final_predictions
            }
            
            # Generate visualization
            self.visualizer.plot_prediction_probabilities(
                probabilities,
                teams.values,
                conf_name,
                2025
            )
        
        return predictions

    def save_predictions(self, predictions):
        """Save predictions to a formatted file"""
        with open("NBA_data/predictions_2025.txt", "w") as f:
            f.write("NBA Playoff Predictions 2025\n")
            f.write("===========================\n\n")
            
            for conference in ['East', 'West']:
                f.write(f"{conference}ern Conference\n")
                f.write("-" * 20 + "\n\n")
                
                # Sort teams by probability
                teams = predictions[conference]['teams']
                probas = predictions[conference]['probabilities']
                preds = predictions[conference]['predictions']
                
                sorted_indices = np.argsort(probas)[::-1]
                
                for idx in sorted_indices:
                    team = teams[idx]
                    probability = probas[idx]
                    prediction = preds[idx]
                    
                    status = "PLAYOFF BOUND" if prediction == 1 else "PREDICTED OUT"
                    f.write(f"{team:<25} {probability:.1%} ({status})\n")
                
                f.write("\n")

def main():
    predictor = PlayoffPredictor()
    
    print("Updating NBA data...")
    predictor.update_data()
    
    print("\nGenerating predictions...")
    predictions = predictor.generate_predictions()
    
    print("\nSaving predictions...")
    predictor.save_predictions(predictions)
    
    print("\nPrediction update complete! Check 'NBA_data/predictions_2025.txt' for results.")

if __name__ == "__main__":
    main()