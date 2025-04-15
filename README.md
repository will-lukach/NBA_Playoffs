# NBA Playoffs Predictor 2025

![NBA Logo](Images/nba_no_background.png)

This project uses machine learning to predict which NBA teams will make the playoffs in 2025, based on regular season performance statistics from 1980 onwards. It's an updated version of the original project by [hanesy](https://github.com/hanesy/NBA_Playoffs).

## Introduction

Every NBA regular season, 30 teams compete across two conferences (Eastern and Western), with each team playing 82 games. At the end of the regular season, the eight teams with the most wins in each conference qualify for the playoffs.

This project uses historical NBA data from the 1980 season (when the 3-point line was introduced) through 2024 to train machine learning models that predict which teams will make the playoffs in 2025.

## Methodology

We developed three different types of models to predict playoff teams:

1. **Logistic Regression** - A linear model that excels at understanding the relationship between variables
2. **Random Forest** - An ensemble model that uses multiple decision trees to make predictions
3. **Support Vector Machine (SVM)** - A model that finds the optimal boundary between playoff and non-playoff teams

### Data Preprocessing

Each performance statistic is scaled using a quantile transformer by each year and normalized, making the statistics comparable across different NBA eras. We train separate models for the Eastern and Western conferences to account for conference-specific patterns.

### Feature Importance

Our models identified several important factors for predicting playoff teams:

- Game outcomes (wins and losses) are the most important features
- Defensive rebounds (DRB) are important for both conferences
- Steals (STL) and turnovers (TOV) are important for logistic regression and SVM models
- Shooting percentages (FG%, 2P%, 3P%) are important for random forest models

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/NBA-Playoffs-2025.git
   cd NBA-Playoffs-2025
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

The project consists of several Python scripts that can be run sequentially:

1. **Scrape the data**:
   ```
   python nba_scraper_2025.py
   ```

2. **Preprocess the data**:
   ```
   python preprocess_data.py
   ```

3. **Train the models**:
   ```
   python train_models.py
   ```

4. **Generate visualizations**:
   ```
   python generate_visualizations.py
   ```

5. **Update predictions for 2025**:
   ```
   python update_predictions.py
   ```

6. **View the results**:
   Open `index.html` in a web browser to see the predictions and visualizations.

## File Structure

- `nba_scraper_2025.py` - Scrapes NBA data from basketball-reference.com
- `preprocess_data.py` - Cleans and preprocesses the raw data
- `train_models.py` - Trains the prediction models on historical data
- `generate_visualizations.py` - Creates visualizations for the results
- `update_predictions.py` - Updates predictions for the current season
- `index.html` - Web interface to view predictions and results
- `NBA_data/` - Directory containing raw and processed data
- `models/` - Directory containing trained models
- `Images/` - Directory containing visualizations

## Results

The final predictions are determined by averaging the probabilities from all three models. The top 8 teams from each conference with the highest probabilities are predicted to make the playoffs.

Check `index.html` or `NBA_data/predictions_2025.txt` for the latest predictions.

## Credits and Acknowledgments

This project is an updated version of the [original NBA Playoffs prediction project](https://github.com/hanesy/NBA_Playoffs) by hanesy.

Original project contributors:
- Dagney Cooke
- Shaymus McTeague
- Diana Silva
- Heain Yee

Data source: [Basketball Reference](https://www.basketball-reference.com/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.