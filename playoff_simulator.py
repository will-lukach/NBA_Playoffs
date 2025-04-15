import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import json

class PlayoffSimulator:
    def __init__(self, n_simulations: int = 10000):
        self.n_simulations = n_simulations
        self.home_court_advantage = 3.0  # Average NBA home court advantage in points
        
    def load_team_data(self, filepath: str) -> pd.DataFrame:
        """Load and prepare team data for simulation"""
        df = pd.read_csv(filepath)
        current_season = df[df['Year'] == 2025].copy()
        
        # Calculate net rating from offensive and defensive ratings
        current_season['NET_RATING'] = current_season['FG'] - current_season['FGA']
        
        # Sort teams by conference and win percentage
        east = current_season[current_season['Conference'] == 'East'].sort_values('W/L%', ascending=False)
        west = current_season[current_season['Conference'] == 'West'].sort_values('W/L%', ascending=False)
        
        return east, west
    
    def simulate_game(self, team1_stats: pd.Series, team2_stats: pd.Series, 
                     home_team: int) -> int:
        """Simulate a single game between two teams
        
        Args:
            team1_stats: Statistics for first team
            team2_stats: Statistics for second team
            home_team: 1 if team1 is home, 2 if team2 is home
            
        Returns:
            1 if team1 wins, 2 if team2 wins
        """
        # Base expected margin from net ratings
        expected_margin = team1_stats['NET_RATING'] - team2_stats['NET_RATING']
        
        # Add home court advantage
        if home_team == 1:
            expected_margin += self.home_court_advantage
        elif home_team == 2:
            expected_margin -= self.home_court_advantage
            
        # Add random variance (standard deviation of ~12 points)
        actual_margin = np.random.normal(expected_margin, 12.0)
        
        return 1 if actual_margin > 0 else 2
    
    def simulate_series(self, team1_stats: pd.Series, team2_stats: pd.Series, 
                       team1_home_court: bool) -> int:
        """Simulate a 7-game playoff series between two teams
        
        Args:
            team1_stats: Statistics for first team
            team2_stats: Statistics for second team
            team1_home_court: Whether team1 has home court advantage
            
        Returns:
            1 if team1 wins series, 2 if team2 wins series
        """
        wins_needed = 4
        team1_wins = 0
        team2_wins = 0
        game_num = 0
        
        # 2-2-1-1-1 format
        home_court = [1,1,2,2,1,2,1] if team1_home_court else [2,2,1,1,2,1,2]
        
        while team1_wins < wins_needed and team2_wins < wins_needed:
            winner = self.simulate_game(team1_stats, team2_stats, home_court[game_num])
            if winner == 1:
                team1_wins += 1
            else:
                team2_wins += 1
            game_num += 1
            
        return 1 if team1_wins == wins_needed else 2
    
    def simulate_playoff_round(self, matchups: List[Tuple[pd.Series, pd.Series]]) -> Dict:
        """Simulate a full round of playoff matchups multiple times
        
        Args:
            matchups: List of (team1, team2) matchup tuples
            
        Returns:
            Dictionary with series win probabilities for each team
        """
        results = {}
        
        for i, (team1, team2) in enumerate(matchups):
            team1_wins = 0
            
            for _ in range(self.n_simulations):
                # Higher seed (team1) has home court
                winner = self.simulate_series(team1, team2, True)
                if winner == 1:
                    team1_wins += 1
            
            prob_team1 = team1_wins / self.n_simulations
            results[f"series_{i+1}"] = {
                "team1": team1['Team'],
                "team2": team2['Team'],
                "team1_prob": prob_team1,
                "team2_prob": 1 - prob_team1
            }
            
        return results
    
    def simulate_play_in(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Simulate play-in tournament
        
        Args:
            df: Conference dataframe (should contain teams ranked 7-10)
            
        Returns:
            Tuple of (7th seed, 8th seed) after play-in
        """
        # 7-8 game
        seven_eight = self.simulate_game(df.iloc[6], df.iloc[7], 1)  # 7th has home court
        winner_7_8 = df.iloc[6] if seven_eight == 1 else df.iloc[7]
        loser_7_8 = df.iloc[7] if seven_eight == 1 else df.iloc[6]
        
        # 9-10 game
        nine_ten = self.simulate_game(df.iloc[8], df.iloc[9], 1)  # 9th has home court
        winner_9_10 = df.iloc[8] if nine_ten == 1 else df.iloc[9]
        
        # 7/8 loser vs 9/10 winner for 8th seed
        final_game = self.simulate_game(loser_7_8, winner_9_10, 1)  # loser 7/8 has home court
        eighth_seed = loser_7_8 if final_game == 1 else winner_9_10
        
        return winner_7_8, eighth_seed

    def simulate_playoffs(self, east_df: pd.DataFrame, west_df: pd.DataFrame) -> Dict:
        """Simulate entire playoff bracket including play-in
        
        Args:
            east_df: Eastern conference teams dataframe
            west_df: Western conference teams dataframe
            
        Returns:
            Dictionary with round-by-round probabilities
        """
        rounds = [
            {"name": "First Round", "matchups": []},
            {"name": "Conference Semifinals", "matchups": []},
            {"name": "Conference Finals", "matchups": []},
            {"name": "Finals", "matchups": []}
        ]
        
        # Process each conference
        for conf, df in [("West", west_df), ("East", east_df)]:
            # Simulate play-in tournament
            orig_7_10 = df.iloc[6:10].copy()
            seventh_seed_counts = {team: 0 for team in orig_7_10['Team']}
            eighth_seed_counts = {team: 0 for team in orig_7_10['Team']}
            
            for _ in range(self.n_simulations):
                seventh, eighth = self.simulate_play_in(df.iloc[:10])
                seventh_seed_counts[seventh['Team']] += 1
                eighth_seed_counts[eighth['Team']] += 1
            
            # Use most likely outcome for bracket
            most_likely_7th = max(seventh_seed_counts.items(), key=lambda x: x[1])[0]
            most_likely_8th = max(eighth_seed_counts.items(), key=lambda x: x[1])[0]
            
            # Update dataframe with play-in results
            df.iloc[6] = df[df['Team'] == most_likely_7th].iloc[0]
            df.iloc[7] = df[df['Team'] == most_likely_8th].iloc[0]
            
            # First round matchups (1v8, 4v5, 3v6, 2v7)
            seeds = [(1,8), (4,5), (3,6), (2,7)]
            team_indices = [(0,7), (3,4), (2,5), (1,6)]
            
            for (seed1, seed2), (idx1, idx2) in zip(seeds, team_indices):
                team1, team2 = df.iloc[idx1], df.iloc[idx2]
                matchup = {
                    "team1": {
                        "name": team1['Team'],
                        "seed": seed1,
                        "logo": f"/Images/logos/{team1['Team']}.png",
                        "probability": 0.0  # Will be updated
                    },
                    "team2": {
                        "name": team2['Team'],
                        "seed": seed2,
                        "logo": f"/Images/logos/{team2['Team']}.png",
                        "probability": 0.0  # Will be updated
                    }
                }
                
                # Simulate series multiple times
                team1_wins = 0
                for _ in range(self.n_simulations):
                    winner = self.simulate_series(team1, team2, True)
                    if winner == 1:
                        team1_wins += 1
                
                # Update probabilities
                prob = team1_wins / self.n_simulations
                matchup["team1"]["probability"] = prob
                matchup["team2"]["probability"] = 1 - prob
                
                rounds[0]["matchups"].append(matchup)
            
            # Add empty matchups for later rounds
            for i in range(2):
                rounds[1]["matchups"].append({"team1": None, "team2": None})
            rounds[2]["matchups"].append({"team1": None, "team2": None})
        
        # Add empty Finals matchup
        rounds[3]["matchups"].append({"team1": None, "team2": None})
        
        return {
            "title": "MODEL PREDICTIONS",
            "rounds": rounds
        }

def main():
    # Initialize simulator
    simulator = PlayoffSimulator(n_simulations=10000)
    
    # Load team data
    east_df, west_df = simulator.load_team_data("NBA_data/current_season.csv")
    
    # Run playoff simulations
    results = simulator.simulate_playoffs(east_df, west_df)
    
    # Save results
    with open("NBA_data/playoff_simulations.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Playoff simulations complete! Results saved to 'NBA_data/playoff_simulations.json'")

if __name__ == "__main__":
    main()