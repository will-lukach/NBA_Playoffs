import os
import sys
import time

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['NBA_data', 'models', 'Images']
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Creating directory: {directory}")
            os.makedirs(directory)

def run_step(step_name, script_name):
    """Run a step in the pipeline and check for success"""
    print(f"\n{'=' * 40}")
    print(f"STEP: {step_name}")
    print(f"{'=' * 40}\n")
    
    result = os.system(f"python {script_name}")
    
    if result != 0:
        print(f"\nERROR: {step_name} failed with exit code {result}")
        return False
    
    print(f"\n{step_name} completed successfully!")
    return True

def main():
    """Run the complete pipeline"""
    print("\nNBA Playoffs Predictor 2025 - Pipeline Runner")
    print("=" * 50)
    
    # Check if Python environment has required packages
    try:
        import pandas
        import numpy
        import matplotlib
        import sklearn
        import requests
        import bs4
        import seaborn
        import joblib
        import nba_api
    except ImportError as e:
        print(f"ERROR: Missing required package: {e}")
        print("Please install all required packages: pip install -r requirements.txt")
        return 1
    
    # Create directories
    create_directories()
    
    # Step 0: Download NBA logos
    if not run_step("Logo Download", "download_logos.py"):
        return 1
    
    # Step 1: Get NBA data
    if not run_step("Data Collection", "nba_scraper_2025.py"):
        return 1
    
    # Step 2: Preprocess data
    if not run_step("Data Preprocessing", "preprocess_data.py"):
        return 1
    
    # Step 3: Train models
    if not run_step("Model Training", "train_models.py"):
        return 1
    
    # Step 4: Generate visualizations
    if not run_step("Visualization Generation", "generate_visualizations.py"):
        return 1
    
    # Step 5: Update predictions
    if not run_step("Prediction Update", "update_predictions.py"):
        return 1

    # Step 6: Run playoff simulations
    if not run_step("Playoff Simulations", "playoff_simulator.py"):
        return 1

    # Step 7: Generate playoff visualizations
    print("\n" + "=" * 40)
    print("STEP: Playoff Visualization Generation")
    print("=" * 40 + "\n")

    try:
        from generate_visualizations import Visualizer
        import json

        # Load simulation results
        with open("NBA_data/playoff_simulations.json", "r") as f:
            simulation_results = json.load(f)

        # Create visualizations
        visualizer = Visualizer()
        
        # Generate playoff bracket with all matchups
        visualizer.plot_playoff_bracket(simulation_results)
        
        # Generate round probabilities
        visualizer.plot_round_probabilities(simulation_results)
        
        print("\nPlayoff visualizations completed successfully!")
    except Exception as e:
        print(f"\nERROR: Playoff visualization generation failed: {str(e)}")
        return 1
    
    print("\n" + "=" * 50)
    print("Pipeline completed successfully!")
    print("=" * 50)
    
    # Open results in browser
    print("\nOpening results in web browser...")
    import webbrowser
    webbrowser.open('file://' + os.path.realpath('index.html'))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())