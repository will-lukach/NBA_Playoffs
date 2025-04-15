import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import os
import json
from matplotlib.patches import Rectangle, ConnectionPatch, FancyBboxPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as path_effects

class Visualizer:
    def __init__(self):
        self.output_dir = "Images"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # NBA team colors (primary, secondary)
        self.team_colors = {
            'Hawks': ('#E03A3E', '#C1D32F'),
            'Celtics': ('#007A33', '#BA9653'),
            'Nets': ('#000000', '#FFFFFF'),
            'Hornets': ('#1D1160', '#00788C'),
            'Bulls': ('#CE1141', '#000000'),
            'Cavaliers': ('#860038', '#041E42'),
            'Mavericks': ('#00538C', '#002B5E'),
            'Nuggets': ('#0E2240', '#FEC524'),
            'Pistons': ('#C8102E', '#1D42BA'),
            'Warriors': ('#1D428A', '#FFC72C'),
            'Rockets': ('#CE1141', '#000000'),
            'Pacers': ('#002D62', '#FDBB30'),
            'Clippers': ('#C8102E', '#1D428A'),
            'Lakers': ('#552583', '#FDB927'),
            'Grizzlies': ('#5D76A9', '#12173F'),
            'Heat': ('#98002E', '#F9A01B'),
            'Bucks': ('#00471B', '#EEE1C6'),
            'Timberwolves': ('#0C2340', '#236192'),
            'Pelicans': ('#0C2340', '#C8102E'),
            'Knicks': ('#006BB6', '#F58426'),
            'Thunder': ('#007AC1', '#EF3B24'),
            'Magic': ('#0077C0', '#C4CED4'),
            '76ers': ('#006BB6', '#ED174C'),
            'Suns': ('#1D1160', '#E56020'),
            'Trail Blazers': ('#E03A3E', '#000000'),
            'Kings': ('#5A2D81', '#63727A'),
            'Spurs': ('#C4CED4', '#000000'),
            'Raptors': ('#CE1141', '#000000'),
            'Jazz': ('#002B5C', '#00471B'),
            'Wizards': ('#002B5C', '#E31837')
        }
        
        # Set style for NBA look
        plt.style.use('default')
        self.round_names = {
            'first_round': 'FIRST ROUND',
            'conference_semis': 'CONFERENCE SEMIFINALS',
            'conference_finals': 'CONFERENCE FINALS',
            'NBA_Finals': 'NBA FINALS'
        }
        
    def load_team_logo(self, team_name):
        """Load team logo from Images/logos directory"""
        logo_path = os.path.join("Images", "logos", f"{team_name}.png")
        if os.path.exists(logo_path):
            return mpimg.imread(logo_path)
        return None

    def plot_playoff_bracket(self, simulation_results, conference=None):
        """Create interactive playoff bracket"""
        # Read the template
        with open('index.html', 'r') as f:
            template = f.read()

        # Create a copy of the simulation results to modify
        bracket_data = simulation_results.copy()

        # Fix the logo paths by removing the leading slash
        for round_data in bracket_data["rounds"]:
            for matchup in round_data["matchups"]:
                if matchup["team1"]:
                    matchup["team1"]["logo"] = matchup["team1"]["logo"].lstrip('/')
                if matchup["team2"]:
                    matchup["team2"]["logo"] = matchup["team2"]["logo"].lstrip('/')
        
        # Save the updated HTML with the simulation results
        output_path = os.path.join(self.output_dir, 'playoff_bracket.html')
        with open(output_path, 'w') as f:
            f.write(template.replace(
                'const bracketData = {',
                f'const bracketData = {json.dumps(bracket_data, indent=2)}'
            ))

    def plot_round_probabilities(self, simulation_results):
        """Plot round-by-round advancement probabilities for all teams"""
        # Collect probabilities for each team in each round
        team_probs = {}
        rounds = ['first_round', 'conference_semis', 'conference_finals', 'NBA_Finals']
        round_colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728']  # Distinct colors for each round
        
        # Process conference rounds
        for conf in ['East', 'West']:
            for round_name in rounds[:-1]:  # Exclude NBA_Finals for now
                if round_name not in simulation_results[conf]:
                    continue
                    
                round_data = simulation_results[conf][round_name]
                for series in round_data.values():
                    for team, prob in [(series['team1'], series['team1_prob']),
                                    (series['team2'], series['team2_prob'])]:
                        if team not in team_probs:
                            team_probs[team] = {r: 0.0 for r in rounds}
                        team_probs[team][round_name] = prob

        # Add NBA Finals probabilities if available
        if 'NBA_Finals' in simulation_results and 'series_1' in simulation_results['NBA_Finals']:
            finals = simulation_results['NBA_Finals']['series_1']
            if finals['team1'] and finals['team2']:  # Only process if teams are not None
                for team, prob in [(finals['team1'], finals['team1_prob']),
                                (finals['team2'], finals['team2_prob'])]:
                    if team not in team_probs:
                        team_probs[team] = {r: 0.0 for r in rounds}
                    team_probs[team]['NBA_Finals'] = prob

        # Create plot
        plt.figure(figsize=(20, 12))
        
        # Sort teams by their maximum probability across all rounds
        teams = sorted(team_probs.keys(),
                      key=lambda x: max(team_probs[x].values()),
                      reverse=True)
        x = np.arange(len(teams))
        width = 0.18
        multiplier = 0

        # Plot bars for each round
        bars = []
        for round_name, color in zip(rounds, round_colors):
            probs = [team_probs[team][round_name] for team in teams]
            offset = width * multiplier
            bar = plt.bar(x + offset, probs, width,
                         label=self.round_names[round_name],
                         color=color,
                         alpha=0.8)
            
            # Add percentage labels on bars
            for i, prob in enumerate(probs):
                if prob > 0.02:  # Only show labels for probabilities > 2%
                    plt.text(x[i] + offset, prob, f'{prob:.0%}',
                            ha='center', va='bottom',
                            fontsize=8, rotation=90)
            
            bars.append(bar)
            multiplier += 1

        # Enhance plot styling
        plt.xlabel('Teams', fontsize=12, labelpad=10)
        plt.ylabel('Probability', fontsize=12, labelpad=10)
        plt.title('NBA Playoff Round Advancement Probabilities',
                 fontsize=16, pad=20)
        
        # Rotate team names for better readability
        plt.xticks(x + width * 1.5, teams, rotation=45, ha='right',
                  fontsize=10)
        plt.yticks(fontsize=10)
        
        # Add legend with enhanced positioning and styling
        plt.legend(loc='upper right', bbox_to_anchor=(1, 1),
                  fontsize=10, framealpha=0.9)
        
        # Add grid for better readability
        plt.grid(True, axis='y', alpha=0.3, linestyle='--')
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save with high DPI for better quality
        plt.savefig(os.path.join(self.output_dir, "round_probabilities.png"),
                   dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    from preprocess_data import DataPreprocessor
    from train_models import ModelTrainer
    
    # Load and preprocess data
    preprocessor = DataPreprocessor()
    data = preprocessor.load_data("NBA_data/historical_data.csv")
    processed_data = preprocessor.preprocess(data)
    
    # Split data by conference
    east_data, west_data = preprocessor.split_conferences(processed_data)
    
    # Load trained models
    trainer = ModelTrainer()
    trainer.load_models()
    
    # Initialize visualizer
    visualizer = Visualizer()
    
    # Generate visualizations for each conference
    for conf_data, conf_name in [(east_data, 'East'), (west_data, 'West')]:
        # Prepare recent data
        X_recent = conf_data[conf_data['Year'] == 2024][preprocessor.features]
        y_recent = conf_data[conf_data['Year'] == 2024][preprocessor.target]
        teams = conf_data[conf_data['Year'] == 2024]['Team']
        
        # Get predictions
        predictions, probabilities, _, _ = trainer.predict_playoffs(X_recent, conf_name)
        
        # Generate visualizations
        visualizer.plot_feature_importance(
            trainer.trained_models[conf_name],
            preprocessor.features,
            conf_name
        )
        
        visualizer.plot_confusion_matrices(y_recent, predictions, conf_name)
        
        visualizer.plot_prediction_probabilities(
            probabilities,
            teams.values,
            conf_name
        )
    
    print("Visualizations generated!")