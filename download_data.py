import pandas as pd
from meteostat import hourly
from datetime import datetime

# 1. Configuration
station_id = '72505' 
start = datetime(2024, 1, 1)
end = datetime(2024, 12, 31, 23, 59) # Ajout de l'heure de fin pour couvrir toute l'année

# 2. Récupérer les données
data = hourly(station_id, start, end)
df = data.fetch()

# 3. Sélection sécurisée des colonnes
# On définit les colonnes idéales pour l'analyse NYC Taxi
target_columns = ['temp', 'dwpt', 'rhum', 'prcp', 'snow', 'wspd', 'pres']

# On ne garde que celles qui existent réellement dans le résultat
available_columns = [col for col in target_columns if col in df.columns]
df = df[available_columns]

# 4. Sauvegarde
df.to_csv('central_park_weather_2024.csv')

print(f"Fichier créé avec les colonnes suivantes : {available_columns}")
print(df.head())