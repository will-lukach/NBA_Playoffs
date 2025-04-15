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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # For SVG files from NBA CDN, convert to PNG
        if url.endswith('.svg'):
            # Save SVG content first
            svg_path = local_path.replace('.png', '.svg')
            with open(svg_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Use alternative PNG URL for better quality
            png_url = url.replace('/primary/L/logo.svg', '/global/L/logo.png')
            png_response = requests.get(png_url, stream=True, headers=headers)
            
            if png_response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in png_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                # Remove temporary SVG file
                os.remove(svg_path)
            else:
                # If PNG not available, keep SVG (browser will handle it)
                os.rename(svg_path, local_path)
        else:
            # Write the file directly for non-SVG files
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

    # URLs for NBA logos (conference and league)
    main_logos = {
        "nba_no_background.png": "https://cdn.nba.com/logos/leagues/logo-nba.svg",
        "nba-Eastern_Conference_logo.png": "https://cdn.nba.com/logos/leagues/logo-eastern.svg",
        "nba-Western_Conference_logo.png": "https://cdn.nba.com/logos/leagues/logo-western.svg"
    }

    # URLs for team logos using NBA's CDN
    team_logos = {
        "Hawks": "https://cdn.nba.com/logos/nba/1610612737/primary/L/logo.svg",
        "Celtics": "https://cdn.nba.com/logos/nba/1610612738/primary/L/logo.svg",
        "Nets": "https://cdn.nba.com/logos/nba/1610612751/primary/L/logo.svg",
        "Hornets": "https://cdn.nba.com/logos/nba/1610612766/primary/L/logo.svg",
        "Bulls": "https://cdn.nba.com/logos/nba/1610612741/primary/L/logo.svg",
        "Cavaliers": "https://cdn.nba.com/logos/nba/1610612739/primary/L/logo.svg",
        "Mavericks": "https://cdn.nba.com/logos/nba/1610612742/primary/L/logo.svg",
        "Nuggets": "https://cdn.nba.com/logos/nba/1610612743/primary/L/logo.svg",
        "Pistons": "https://cdn.nba.com/logos/nba/1610612765/primary/L/logo.svg",
        "Warriors": "https://cdn.nba.com/logos/nba/1610612744/primary/L/logo.svg",
        "Rockets": "https://cdn.nba.com/logos/nba/1610612745/primary/L/logo.svg",
        "Pacers": "https://cdn.nba.com/logos/nba/1610612754/primary/L/logo.svg",
        "Clippers": "https://cdn.nba.com/logos/nba/1610612746/primary/L/logo.svg",
        "Lakers": "https://cdn.nba.com/logos/nba/1610612747/primary/L/logo.svg",
        "Grizzlies": "https://cdn.nba.com/logos/nba/1610612763/primary/L/logo.svg",
        "Heat": "https://cdn.nba.com/logos/nba/1610612748/primary/L/logo.svg",
        "Bucks": "https://cdn.nba.com/logos/nba/1610612749/primary/L/logo.svg",
        "Timberwolves": "https://cdn.nba.com/logos/nba/1610612750/primary/L/logo.svg",
        "Pelicans": "https://cdn.nba.com/logos/nba/1610612740/primary/L/logo.svg",
        "Knicks": "https://cdn.nba.com/logos/nba/1610612752/primary/L/logo.svg",
        "Thunder": "https://cdn.nba.com/logos/nba/1610612760/primary/L/logo.svg",
        "Magic": "https://cdn.nba.com/logos/nba/1610612753/primary/L/logo.svg",
        "76ers": "https://cdn.nba.com/logos/nba/1610612755/primary/L/logo.svg",
        "Suns": "https://cdn.nba.com/logos/nba/1610612756/primary/L/logo.svg",
        "Trail Blazers": "https://cdn.nba.com/logos/nba/1610612757/primary/L/logo.svg",
        "Kings": "https://cdn.nba.com/logos/nba/1610612758/primary/L/logo.svg",
        "Spurs": "https://cdn.nba.com/logos/nba/1610612759/primary/L/logo.svg",
        "Raptors": "https://cdn.nba.com/logos/nba/1610612761/primary/L/logo.svg",
        "Jazz": "https://cdn.nba.com/logos/nba/1610612762/primary/L/logo.svg",
        "Wizards": "https://cdn.nba.com/logos/nba/1610612764/primary/L/logo.svg"
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
        
        time.sleep(0.5)  # Reduced delay

    # Download team logos
    for team, url in team_logos.items():
        local_path = os.path.join(logos_dir, f"{team}.png")
        
        if os.path.exists(local_path):
            print(f"File already exists: {local_path}")
            success_count += 1
            continue
        
        if download_file(url, local_path):
            success_count += 1
        
        time.sleep(0.5)  # Reduced delay
    
    # Print summary
    print(f"\nDownloaded {success_count} of {total_logos} logos.")
    
    if success_count == total_logos:
        print("All logos downloaded successfully!")
    else:
        print("Some logos could not be downloaded.")
        print("The web interface may not display correctly.")

if __name__ == "__main__":
    main()