import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from nba_api.stats.endpoints import leaguegamefinder, teamestimatedmetrics, leaguestandings
from nba_api.stats.static import teams
import time

class NBAScraper:
    def __init__(self):
        self.nba_teams = teams.get_teams()
        self.cache_dir = "NBA_data/cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, endpoint, season):
        """Get cache file path for a specific endpoint and season"""
        return os.path.join(self.cache_dir, f"{endpoint}_{season}.json")
    
    def _load_cache(self, endpoint, season):
        """Load cached data if available"""
        cache_path = self._get_cache_path(endpoint, season)
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None
    
    def _save_cache(self, endpoint, season, data):
        """Save data to cache"""
        cache_path = self._get_cache_path(endpoint, season)
        with open(cache_path, 'w') as f:
            json.dump(data, f)
    
    def get_season_data(self, year=2025):
        """Get NBA data for a specific season using the NBA.com Stats API"""
        print(f"Fetching data for {year} NBA season...")
        
        # Check if the requested year is in the future
        current_year = datetime.now().year
        if year > current_year:
            print(f"Warning: Data for {year} is not available yet. Using {current_year} data instead.")
            year = current_year
        
        try:
            # Get season string (e.g., "2024-25" for 2025)
            season = f"{year-1}-{str(year)[2:]}"
            
            # Get standings data
            print("Fetching standings data...")
            cached_standings = self._load_cache("standings", season)
            if cached_standings:
                print("Using cached standings data")
                standings_df = pd.DataFrame(cached_standings)
            else:
                standings = leaguestandings.LeagueStandings(season=season)
                standings_df = standings.get_data_frames()[0]
                self._save_cache("standings", season, standings_df.to_dict('records'))
            
            # Get team metrics
            print("Fetching team metrics...")
            cached_metrics = self._load_cache("metrics", season)
            if cached_metrics:
                print("Using cached metrics data")
                metrics_df = pd.DataFrame(cached_metrics)
            else:
                metrics = teamestimatedmetrics.TeamEstimatedMetrics(season=season)
                metrics_df = metrics.get_data_frames()[0]
                self._save_cache("metrics", season, metrics_df.to_dict('records'))
            
            print(f"Metrics columns: {metrics_df.columns.tolist()}")
            
            # Get game results
            print("Fetching game results...")
            cached_games = self._load_cache("games", season)
            if cached_games:
                print("Using cached game results")
                games_df = pd.DataFrame(cached_games)
            else:
                gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
                games_df = gamefinder.get_data_frames()[0]
                self._save_cache("games", season, games_df.to_dict('records'))
            
            # Process standings data
            team_data = []
            for _, team in standings_df.iterrows():
                try:
                    team_id = team['TeamID']
                    
                    # Get team games
                    team_games = games_df[games_df['TEAM_ID'] == team_id]
                    
                    # Calculate points per game
                    if not team_games.empty:
                        ppg = team_games['PTS'].mean()
                        point_diff = team_games['PLUS_MINUS'].mean() if 'PLUS_MINUS' in team_games else 0
                        papg = ppg - point_diff
                    else:
                        ppg = float(team['PointsPG']) if 'PointsPG' in team else 0
                        papg = float(team['OppPointsPG']) if 'OppPointsPG' in team else 0
                    
                    # Get team metrics
                    team_metrics = metrics_df[metrics_df['TEAM_ID'] == team_id]
                    if team_metrics.empty:
                        team_metrics = pd.Series({
                            'E_OFF_RATING': 0, 'E_DEF_RATING': 0, 'E_NET_RATING': 0,
                            'E_PACE': 0, 'E_AST_RATIO': 0, 'E_OREB_PCT': 0,
                            'E_DREB_PCT': 0, 'E_REB_PCT': 0, 'E_TM_TOV_PCT': 0
                        })
                    else:
                        team_metrics = team_metrics.iloc[0]
                    
                    # Map conference name
                    conference = team['Conference']
                    if conference == 'Eastern':
                        conference = 'East'
                    elif conference == 'Western':
                        conference = 'West'
                    
                    team_info = {
                        'Team': team['TeamName'],
                        'Conference': conference,
                        'W': int(team['WINS']),
                        'L': int(team['LOSSES']),
                        'W/L%': float(team['WinPCT']),
                        'GB': float(team['ConferenceGamesBack']) if team['ConferenceGamesBack'] != '-' else 0.0,
                        'PS/G': ppg,
                        'PA/G': papg,
                        'SRS': None,  # Not available in API
                        'Year': year,
                        'FG': float(team_metrics['E_OFF_RATING']),
                        'FGA': float(team_metrics['E_DEF_RATING']),
                        'FG%': float(team_metrics['E_NET_RATING']),
                        '3P': float(team_metrics['E_PACE']),
                        '3PA': float(team_metrics['E_AST_RATIO']),
                        '3P%': float(team_metrics['E_OREB_PCT']),
                        '2P': float(team_metrics['E_DREB_PCT']),
                        '2PA': float(team_metrics['E_REB_PCT']),
                        '2P%': float(team_metrics['E_TM_TOV_PCT']),
                        'FT': float(team_metrics['E_OFF_RATING']),  # Using offensive rating as proxy
                        'FTA': float(team_metrics['E_DEF_RATING']),  # Using defensive rating as proxy
                        'FT%': float(team_metrics['E_NET_RATING']),  # Using net rating as proxy
                        'ORB': float(team_metrics['E_OREB_PCT']),
                        'DRB': float(team_metrics['E_DREB_PCT']),
                        'TRB': float(team_metrics['E_REB_PCT']),
                        'AST': float(team_metrics['E_AST_RATIO']),
                        'STL': 0.0,  # Not directly available
                        'BLK': 0.0,  # Not directly available
                        'TOV': float(team_metrics['E_TM_TOV_PCT']),
                        'PF': 0.0,  # Not directly available
                        'PTS': ppg
                    }
                    
                    team_data.append(team_info)
                    
                except Exception as e:
                    print(f"Warning: Error processing team {team.get('TeamName', 'Unknown')}: {str(e)}")
                    continue
            
            if not team_data:
                print("No team data was collected.")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(team_data)
            print(f"Successfully fetched data for {len(df)} teams.")
            
            # Verify conference distribution
            east_count = len(df[df['Conference'] == 'East'])
            west_count = len(df[df['Conference'] == 'West'])
            print(f"Conference distribution - East: {east_count}, West: {west_count}")
            
            return df
            
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return None

if __name__ == "__main__":
    # Create NBA_data directory if it doesn't exist
    if not os.path.exists("NBA_data"):
        os.makedirs("NBA_data")
    
    scraper = NBAScraper()
    
    # Get current season data
    print("\nFetching current season data...")
    current_season = scraper.get_season_data(2025)
    if current_season is not None and not current_season.empty:
        current_season.to_csv("NBA_data/current_season.csv", index=False)
        print("Current season data saved to 'NBA_data/current_season.csv'")
    else:
        print("Error: Failed to fetch current season data")
        exit(1)
    
    # Get historical data (last 5 seasons for training)
    print("\nFetching historical data...")
    current_year = datetime.now().year
    historical_data = []
    
    for year in range(current_year - 5, current_year):
        print(f"\nFetching {year} season data...")
        season_data = scraper.get_season_data(year)
        if season_data is not None and not season_data.empty:
            historical_data.append(season_data)
        time.sleep(2)  # Rate limiting between seasons
    
    if historical_data:
        historical_df = pd.concat(historical_data, ignore_index=True)
        historical_df.to_csv("NBA_data/historical_data.csv", index=False)
        print("\nHistorical data saved to 'NBA_data/historical_data.csv'")
    else:
        print("Error: Failed to fetch historical data")
        exit(1)