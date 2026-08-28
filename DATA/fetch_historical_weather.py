import requests
import pandas as pd
import io

def fetch_nasa_data():
    print("Fetching historical weather data for KIIT University...")
    
    # KIIT Coordinates
    lat = 20.353
    lon = 85.818
    
    # Parameters: PRECTOTCORR (Rainfall), T2M (Temp), WS10M (Wind Speed)
    # Dates: Jan 1, 2021 to Jan 1, 2026
    url = (f"https://power.larc.nasa.gov/api/temporal/daily/point?"
           f"parameters=PRECTOTCORR,T2M,WS10M&community=RE&"
           f"longitude={lon}&latitude={lat}&start=20210101&end=20260101&format=CSV")
    
    response = requests.get(url)
    
    if response.status_code == 200:
        # NASA's CSV has some header text at the top. We need to skip those lines.
        # Usually, the actual data starts after the "-END HEADER-" line.
        content = response.text
        data_lines = content.split("-END HEADER-")[1].strip()
        
        # Read into Pandas DataFrame
        df = pd.read_csv(io.StringIO(data_lines))
        
        # Save to a clean CSV for Member 3
        csv_filename = "KIIT_Historical_Weather_2021_2026.csv"
        df.to_csv(csv_filename, index=False)
        
        print(f"Success! Data saved to {csv_filename}")
        print(df.head()) # Show a preview
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

if __name__ == "__main__":
    fetch_nasa_data()