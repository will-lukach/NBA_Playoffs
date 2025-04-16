import os
import requests
import time
from PIL import Image
import io

def download_file(url, local_path, headers=None):
    """Download a file from a URL to a local path"""
    try:
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://www.espn.com/',
                'Origin': 'https://www.espn.com'
            }
        
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Write the file directly
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded: {local_path}")
        return True
    
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def main():
    """Download NBA logos for the web interface"""
    print("Downloading NBA logos...")
    
    # Create Images directory if it doesn't exist
    if not os.path.exists("Images"):
        os.makedirs("Images")
    
    # Create logos directory if it doesn't exist
    logos_dir = os.path.join("Images", "logos")
    if not os.path.exists(logos_dir):
        os.makedirs(logos_dir)

    # Team logo URLs from ESPN's CDN
    team_logos = {
        "Hawks": "https://a.espncdn.com/i/teamlogos/nba/500/atl.png",
        "Celtics": "https://a.espncdn.com/i/teamlogos/nba/500/bos.png",
        "Nets": "https://a.espncdn.com/i/teamlogos/nba/500/bkn.png",
        "Hornets": "https://a.espncdn.com/i/teamlogos/nba/500/cha.png",
        "Bulls": "https://a.espncdn.com/i/teamlogos/nba/500/chi.png",
        "Cavaliers": "https://a.espncdn.com/i/teamlogos/nba/500/cle.png",
        "Mavericks": "https://a.espncdn.com/i/teamlogos/nba/500/dal.png",
        "Nuggets": "https://a.espncdn.com/i/teamlogos/nba/500/den.png",
        "Pistons": "https://a.espncdn.com/i/teamlogos/nba/500/det.png",
        "Warriors": "https://a.espncdn.com/i/teamlogos/nba/500/gsw.png",
        "Rockets": "https://a.espncdn.com/i/teamlogos/nba/500/hou.png",
        "Pacers": "https://a.espncdn.com/i/teamlogos/nba/500/ind.png",
        "Clippers": "https://a.espncdn.com/i/teamlogos/nba/500/lac.png",
        "Lakers": "https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
        "Grizzlies": "https://a.espncdn.com/i/teamlogos/nba/500/mem.png",
        "Heat": "https://a.espncdn.com/i/teamlogos/nba/500/mia.png",
        "Bucks": "https://a.espncdn.com/i/teamlogos/nba/500/mil.png",
        "Timberwolves": "https://a.espncdn.com/i/teamlogos/nba/500/min.png",
        "Pelicans": "https://a.espncdn.com/i/teamlogos/nba/500/nop.png",
        "Knicks": "https://a.espncdn.com/i/teamlogos/nba/500/nyk.png",
        "Thunder": "https://a.espncdn.com/i/teamlogos/nba/500/okc.png",
        "Magic": "https://a.espncdn.com/i/teamlogos/nba/500/orl.png",
        "76ers": "https://a.espncdn.com/i/teamlogos/nba/500/phi.png",
        "Suns": "https://a.espncdn.com/i/teamlogos/nba/500/phx.png",
        "Trail Blazers": "https://a.espncdn.com/i/teamlogos/nba/500/por.png",
        "Kings": "https://a.espncdn.com/i/teamlogos/nba/500/sac.png",
        "Spurs": "https://a.espncdn.com/i/teamlogos/nba/500/sas.png",
        "Raptors": "https://a.espncdn.com/i/teamlogos/nba/500/tor.png",
        "Jazz": "https://a.espncdn.com/i/teamlogos/nba/500/uta.png",
        "Wizards": "https://a.espncdn.com/i/teamlogos/nba/500/wsh.png"
    }

    # URLs for NBA logos (conference and league)
    main_logos = {
        "nba_no_background.png": "https://a.espncdn.com/i/teamlogos/leagues/500/nba.png",
        "nba-Eastern_Conference_logo.png": "https://a.espncdn.com/i/teamlogos/nba/500/east.png",
        "nba-Western_Conference_logo.png": "https://a.espncdn.com/i/teamlogos/nba/500/west.png"
    }

    # Download main logos
    success_count = 0
    total_logos = len(main_logos) + len(team_logos)

    for filename, url in main_logos.items():
        local_path = os.path.join("Images", filename)
        
        if os.path.exists(local_path):
            print(f"File already exists: {local_path}")
            success_count += 1
            continue
        
        if download_file(url, local_path):
            success_count += 1
        
        time.sleep(0.5)

    # Download team logos
    for team, url in team_logos.items():
        local_path = os.path.join(logos_dir, f"{team}.png")
        
        if os.path.exists(local_path):
            # Remove existing file if it's an SVG saved as PNG
            with open(local_path, 'rb') as f:
                if b'<?xml' in f.read(100) or b'<svg' in f.read(100):
                    os.remove(local_path)
                else:
                    print(f"File already exists: {local_path}")
                    success_count += 1
                    continue
        
        if download_file(url, local_path):
            success_count += 1
        
        time.sleep(0.5)
    
    # Print summary
    print(f"\nDownloaded {success_count} of {total_logos} logos.")
    
    if success_count == total_logos:
        print("All logos downloaded successfully!")
    else:
        print("Some logos could not be downloaded.")
        print("The web interface may not display correctly.")

if __name__ == "__main__":
    main()