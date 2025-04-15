import pandas as pd
import numpy as np
from sklearn.preprocessing import QuantileTransformer

class DataPreprocessor:
    def __init__(self):
        self.features = [
            'W', 'L', 'W/L%', 'GB', 'PS/G', 'PA/G',
            'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%',
            'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK',
            'TOV', 'PF', 'PTS'
        ]
        self.target = 'Playoffs'
        self.transformer = None
    
    def load_data(self, filepath):
        """Load and clean the NBA data"""
        print(f"Loading data from {filepath}")
        df = pd.read_csv(filepath)
        print(f"Loaded {len(df)} rows with columns: {df.columns.tolist()}")
        
        # Fill missing values with 0
        for feature in self.features:
            if feature not in df.columns:
                print(f"Warning: Column {feature} not found in data, filling with 0")
                df[feature] = 0
            else:
                df[feature] = df[feature].fillna(0)
        
        # Add playoff indicator (top 8 teams in each conference)
        df['Playoffs'] = 0
        for year in df['Year'].unique():
            for conf in ['East', 'West']:
                mask = (df['Year'] == year) & (df['Conference'] == conf)
                conf_df = df[mask]
                if not conf_df.empty:
                    df.loc[mask, 'Playoffs'] = (
                        conf_df['W/L%'].rank(ascending=False) <= 8
                    ).astype(int)
        
        print(f"Data loaded and cleaned. Shape: {df.shape}")
        return df
    
    def preprocess(self, df, by_year=True):
        """Preprocess the data using quantile transformation"""
        if df.empty:
            print("Error: Empty DataFrame provided")
            return df
        
        print("Starting preprocessing...")
        processed_dfs = []
        
        if by_year:
            # Process each year separately to maintain relative stats
            years = df['Year'].unique()
            print(f"Processing data by year. Years found: {years}")
            
            for year in years:
                year_df = df[df['Year'] == year].copy()
                if not year_df.empty:
                    print(f"Processing year {year} with {len(year_df)} teams")
                    year_df[self.features] = self._transform_features(year_df[self.features])
                    processed_dfs.append(year_df)
                else:
                    print(f"Warning: No data found for year {year}")
            
            if processed_dfs:
                result = pd.concat(processed_dfs, ignore_index=True)
                print(f"Preprocessing complete. Final shape: {result.shape}")
                return result
            else:
                print("Error: No data to process")
                return df
        else:
            # Process all years together
            print("Processing all years together")
            df_copy = df.copy()
            df_copy[self.features] = self._transform_features(df[self.features])
            print(f"Preprocessing complete. Shape: {df_copy.shape}")
            return df_copy
    
    def _transform_features(self, X):
        """Apply quantile transformation to features"""
        if X.empty:
            return X
        
        # Replace infinities and very large numbers with 0
        X = X.replace([np.inf, -np.inf], 0)
        X = X.clip(-1e6, 1e6)  # Clip very large values
        
        self.transformer = QuantileTransformer(output_distribution='normal')
        transformed = pd.DataFrame(
            self.transformer.fit_transform(X),
            columns=X.columns,
            index=X.index
        )
        return transformed
    
    def split_conferences(self, df):
        """Split data by conference"""
        east_df = df[df['Conference'] == 'East']
        west_df = df[df['Conference'] == 'West']
        print(f"Split data: East ({len(east_df)} teams), West ({len(west_df)} teams)")
        return east_df, west_df
    
    def prepare_train_test(self, df, test_year=2024):
        """Prepare training and testing datasets"""
        print(f"Preparing train/test split with test_year={test_year}")
        
        # Split into train and test
        train_df = df[df['Year'] < test_year]
        test_df = df[df['Year'] == test_year]
        
        print(f"Train set: {len(train_df)} samples")
        print(f"Test set: {len(test_df)} samples")
        
        # Split features and target
        X_train = train_df[self.features]
        y_train = train_df[self.target]
        X_test = test_df[self.features]
        y_test = test_df[self.target]
        
        return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    
    # Load and preprocess data
    print("\nLoading data...")
    raw_data = preprocessor.load_data("NBA_data/historical_data.csv")
    
    print("\nPreprocessing data...")
    processed_data = preprocessor.preprocess(raw_data)
    
    if processed_data is not None and not processed_data.empty:
        # Save processed data
        processed_data.to_csv("NBA_data/processed_data.csv", index=False)
        print("\nData preprocessing complete! Saved to 'NBA_data/processed_data.csv'")
    else:
        print("\nError: Failed to process data")
        exit(1)