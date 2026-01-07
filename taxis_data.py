import requests
import pandas as pd
from pathlib import Path
import os

# URLs des données NYC Taxi 2024
DATA_URLS = {
    "yellow_2024_01": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet",
    "yellow_2024_02": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-02.parquet",
    "yellow_2024_03": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-03.parquet",
    "yellow_2024_04": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-04.parquet",
    "yellow_2024_05": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-05.parquet",
    "yellow_2024_06": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-06.parquet",
    "yellow_2024_07": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-07.parquet",
    "yellow_2024_08": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-08.parquet",
    "yellow_2024_09": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-09.parquet",
    "yellow_2024_10": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-10.parquet",
    "yellow_2024_11": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-11.parquet",
    "yellow_2024_12": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-12.parquet",
    "taxi_zones": "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip",
    "central_park_weather": "https://d37ci6vzurychx.cloudfront.net/misc/central_park_weather.csv"
}

def download_file(url, output_path):
    """Télécharge un fichier depuis une URL"""
    print(f"Téléchargement de {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Fichier sauvegardé: {output_path}")
    return output_path

def main():
    # Créer la structure de dossiers
    data_dir = Path("data/raw/Nyc_Taxi")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Télécharger les fichiers
    for name, url in DATA_URLS.items():
        ext = url.split('.')[-1]
        output_path = data_dir / f"{name}.{ext}"
        
        if not output_path.exists():
            try:
                download_file(url, output_path)
            except Exception as e:
                print(f"Erreur lors du téléchargement de {name}: {e}")
        else:
            print(f"Fichier existe déjà: {output_path}")
    
    # Afficher les informations sur les données
    print("\n=== Informations des données téléchargées ===")
    for file in data_dir.glob("*.parquet"):
        try:
            df = pd.read_parquet(file)
            print(f"{file.name}: {len(df):,} lignes, {len(df.columns)} colonnes")
            print(f"  Colonnes: {list(df.columns)}")
            print(f"  Période: {df['tpep_pickup_datetime'].min()} to {df['tpep_pickup_datetime'].max()}")
        except Exception as e:
            print(f"Erreur lecture {file}: {e}")

if __name__ == "__main__":
    main()