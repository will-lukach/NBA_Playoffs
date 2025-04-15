import json
from generate_visualizations import Visualizer

def test_visualizations():
    # Load playoff simulation data
    with open('NBA_data/playoff_simulations.json', 'r') as f:
        simulation_results = json.load(f)

    # Initialize visualizer
    visualizer = Visualizer()

    # Generate playoff bracket visualization
    print("Generating playoff bracket visualization...")
    visualizer.plot_playoff_bracket(simulation_results)

    # Prepare data for round probabilities
    # Convert the data structure to match what plot_round_probabilities expects
    conference_data = {
        'East': {
            'first_round': {},
            'conference_semis': {},
            'conference_finals': {}
        },
        'West': {
            'first_round': {},
            'conference_semis': {},
            'conference_finals': {}
        }
    }

    # Process first round matchups
    for i, matchup in enumerate(simulation_results['rounds'][0]['matchups']):
        # First 4 matchups are West, last 4 are East
        conf = 'West' if i < 4 else 'East'
        series_num = i + 1 if i < 4 else i - 3
        
        conference_data[conf]['first_round'][f'series_{series_num}'] = {
            'team1': matchup['team1']['name'],
            'team2': matchup['team2']['name'],
            'team1_prob': matchup['team1']['probability'],
            'team2_prob': matchup['team2']['probability']
        }

    # Generate round probabilities visualization
    print("Generating round probabilities visualization...")
    visualizer.plot_round_probabilities(conference_data)

    print("Visualizations generated! Check the Images directory for:")
    print("1. playoff_bracket.html")
    print("2. round_probabilities.png")

if __name__ == "__main__":
    test_visualizations()