
# 🚕 NYC Taxi Analytics Platform 

## . 📌 Overview
This project is an **end-to-end data engineering analytics platform** built on NYC Taxi data, enriched with weather information. It moves beyond traditional warehousing by implementing a **Modern Data Lakehouse**.

It demonstrates:
* **Robust Architecture:** Bronze / Silver / Gold layers.
* **Modern Storage:** Apache Iceberg as the table format.
* **Processing:** Apache Spark for heavy transformations.
* **Analytics:** Trino for high-speed querying.
* **Visualization:** Apache Superset for business dashboards.

> **🎯 Goal:** Transform raw operational data into business-ready analytics for operations, finance, and strategy.



## 📖 The Lakehouse Concept & Architecture

### Why a Lakehouse?
Traditionally, companies maintained two separate systems: a **Data Lake** for raw, unstructured data (cheap, flexible) and a **Data Warehouse** for structured, high-performance analytics (reliable, expensive).

This project implements a **Lakehouse architecture**, which combines the best of both worlds:
* **ACID Transactions:** Ensures data integrity during writes/updates (via Apache Iceberg).
* **Decoupled Storage & Compute:** Storage (S3/Local) is cheap; Compute (Spark/Trino) scales independently.
* **Open Formats:** Data is stored in open Parquet files, not locked into a proprietary vendor format.


## 🧰 Tech Stack

| Category | Technology | Role |
| :--- | :--- | :--- |
| **Compute Engine** | **Apache Spark** | Distributed data processing and heavy ETL transformations. |
| **Storage** | **MinIO** | S3-compatible object storage for the Data Lake. |
| **Query Engine** | **Trino** | High-speed distributed SQL query engine for analytics. |
| **Table Format** | **Apache Iceberg** | Open table format providing ACID transactions and schema evolution. |
| **Orchestrator** | **Apache Airflow** | Workflow management and pipeline scheduling. |
| **Reporting** | **Apache Superset** | Business Intelligence dashboards and data visualization. |

### Architectural Flow
The pipeline follows the "Medallion" architecture (Bronze/Silver/Gold):


0. **Download:** Python scripts fetch raw data from NYC Open Data & Meteostat APIs.
1.  **Ingest:** Pyspark scripts fetch from raw zone. 
2.  **Process:** Apache Spark cleans and transforms data into Iceberg tables.
3.  **Serve:** Trino provides a high-speed SQL query engine over the Iceberg tables.
4.  **Visualize:** Apache Superset consumes Trino views for business intelligence.

---

## 📂 Dataset Overview

The analysis is based on three core datasets organized in the `data/raw/NYC_Taxi` directory:

1.  **🚕 Taxi Trips (`/taxi_trips`):**
    * **Source:** NYC Taxi & Limousine Commission (TLC).
    * **Content:** Detailed records of yellow taxi trips (Pick-up/Drop-off times, distances, fares, payment types, passenger counts).
    * **Volume:** ~3 Million+ records/month.

2.  **🌦️ Weather Data (`/weather`):**
    * **Source:** Meteostat (Station 72505 - Central Park).
    * **Content:** Hourly metrics for Temperature, Precipitation, Snow, Wind Speed.
    * **Goal:** Correlate weather conditions with taxi demand and traffic speed.

3.  **🗺️ Taxi Zones (`/taxi_zones`):**
    * **Source:** NYC Open Data (GIS).
    * **Content:** Shapefiles and mapping tables linking `LocationID` to readable Boroughs and Zones (e.g., "Manhattan - Upper East Side").

---

## 🛠️ Data Acquisition

The following scripts are used to fetch the data and organize the directory structure.

### 1. File Directory Structure
To match the ingestion pipeline expectation, the raw data is organized as follows:

```text
data/raw/NYC_Taxi/
├── taxi_trips/      # Contains .parquet files (Jan-Dec 2024)
├── taxi_zones/      # Contains .zip/.csv zone definitions
└── weather/         # Contains central_park_weather_2024.csv

```

### 2. Weather Data Ingestion (Python)

We use the `meteostat` library to fetch hourly precision data for Central Park.

```python
import pandas as pd
from meteostat import hourly
from datetime import datetime
import os

# Ensure directory exists
os.makedirs('data/raw/NYC_Taxi/weather', exist_ok=True)

# 1. Configuration (Central Park Station)
station_id = '72505' 
start = datetime(2024, 1, 1)
end = datetime(2024, 12, 31, 23, 59)

# 2. Fetch Data
data = hourly(station_id, start, end)
df = data.fetch()

# 3. Secure Column Selection
target_columns = ['temp', 'dwpt', 'rhum', 'prcp', 'snow', 'wspd', 'pres']
available_columns = [col for col in target_columns if col in df.columns]
df = df[available_columns]

# 4. Save
output_path = 'data/raw/NYC_Taxi/weather/central_park_weather_2024.csv'
df.to_csv(output_path)
print(f"Weather data saved to: {output_path}")

```

### 3. Taxi Data Ingestion (Python)

This script downloads the heavy Parquet files and Zone data directly from the cloud source.

```python
import requests
import pandas as pd
from pathlib import Path

# Configuration
BASE_DIR = Path("data/raw/NYC_Taxi")
URLS = {
    "taxi_trips": [
        f"[https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-){str(i).zfill(2)}.parquet"
        for i in range(1, 13)
    ],
    "taxi_zones": [
        "[https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip](https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip)"
    ]
}

def download_file(url, folder):
    """Downloads a file to the specified subfolder"""
    target_dir = BASE_DIR / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    
    filename = url.split('/')[-1]
    output_path = target_dir / filename
    
    if output_path.exists():
        print(f"Skipping (exists): {filename}")
        return

    print(f"Downloading {filename}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

def main():
    print("=== Starting Ingestion ===")
    
    # Download Trips
    for url in URLS["taxi_trips"]:
        download_file(url, "taxi_trips")
        
    # Download Zones
    for url in URLS["taxi_zones"]:
        download_file(url, "taxi_zones")

    print("\n✅ Ingestion Complete.")
    
    # Validation Sample
    sample_file = list((BASE_DIR / "taxi_trips").glob("*.parquet"))[0]
    df = pd.read_parquet(sample_file)
    print(f"\nSample Check ({sample_file.name}):")
    print(f"Rows: {len(df):,}, Columns: {len(df.columns)}")

if __name__ == "__main__":
    main()

```

---

## 🏗️ Pipeline Architecture

```text
Raw Data (Parquet / CSV)
        ↓
┌─────────────┐
│  Bronze     │  → Raw, schema-validated, immutable
│  Iceberg    │
└─────────────┘
        ↓
┌─────────────┐
│  Silver     │  → Cleaned, enriched, joined
│  Iceberg    │
└─────────────┘
        ↓
┌─────────────┐
│  Gold       │  → Business metrics & KPIs
│  Iceberg    │
└─────────────┘
        ↓
Trino SQL → Apache Superset Dashboards

```

---

## 🧪 Analysis & Query Showcase

Below are actual SQL queries executed via Trino on the **Gold** layer, showcasing the analytical capabilities of the platform.

### A. Executive Overview – Global Performance

**Goal:** Track revenue evolution and customer behavior over time.

```sql
SELECT
  pickup_date,
  total_trips,
  ROUND(daily_revenue, 2) AS daily_revenue,
  ROUND(revenue_per_trip, 2) AS revenue_per_trip,
  ROUND(avg_tip_percentage, 2) AS avg_tip_pct
FROM iceberg.gold.daily_metrics
ORDER BY pickup_date;

```

**📊 Actual Results:**
| pickup_date | total_trips | daily_revenue | revenue_per_trip | avg_tip_pct |
| :--- | :--- | :--- | :--- | :--- |
| 2002-12-31 | 4 | 103.08 | 25.77 | 6.16 |
| 2008-12-31 | 1 | 19.90 | 19.90 | 10.05 |
| 2023-12-31 | 10 | 224.62 | 22.46 | 11.25 |
| 2024-01-01 | 66,945 | 2,086,395.98 | 31.17 | 11.53 |
| 2024-01-02 | 70,140 | 2,166,462.60 | 30.89 | 11.32 |
| 2024-01-03 | 77,096 | 2,254,236.52 | 29.24 | 11.54 |
| 2024-01-04 | 96,446 | 2,675,258.69 | 27.74 | 11.92 |

> **💡 Insight:** The data reveals historical outliers (dates in 2002/2008) likely due to meter errors. However, starting Jan 1st 2024, we see a clear ramp-up in volume with stable tip percentages (~11.5%).

---

### 🌤️ B. Weather Impact Analysis

**Goal:** Analyze if rain increases demand or duration.

```sql
SELECT
  weather_condition,
  COUNT(*) AS days,
  ROUND(AVG(total_trips), 0) AS avg_trips,
  ROUND(AVG(avg_fare), 2) AS avg_fare,
  ROUND(AVG(avg_duration), 2) AS avg_duration
FROM iceberg.gold.weather_impact
GROUP BY weather_condition
ORDER BY avg_trips DESC;

```

**📊 Actual Results:**
| weather_condition | days | avg_trips | avg_fare | avg_duration |
| :--- | :--- | :--- | :--- | :--- |
| dry_warm | 340 | 72,989 | 29.50 | 17.40 |
| dry_cold | 133 | 49,936 | 27.88 | 15.77 |
| rainy_warm | 127 | 25,276 | 29.48 | 16.43 |
| rainy_cold | 32 | 24,980 | 27.39 | 15.01 |

> **💡 Insight:** Contrary to popular belief, "Dry" days see significantly higher average trip volumes than rainy days. Fare prices remain relatively stable regardless of weather.

---

### 🕐 C. Rush Hours & Congestion

**Goal:** Identify rush hours and urban congestion impact on speed.

```sql
SELECT
  hour_type,
  ROUND(AVG(trip_count), 0) AS avg_trips,
  ROUND(AVG(avg_speed), 2) AS avg_speed
FROM iceberg.gold.hourly_patterns
GROUP BY hour_type
ORDER BY avg_trips DESC;

```

**📊 Actual Results:**
| hour_type | avg_trips | avg_speed (mph) |
| :--- | :--- | :--- |
| evening_rush | 6,330 | 10.53 |
| regular_hours | 4,965 | 11.17 |
| morning_rush | 2,855 | 13.59 |
| night | 2,196 | 16.08 |

> **💡 Insight:** Clear trade-off between volume and speed. **Evening rush** is the most congested time (lowest speed ~10.5 mph), while **Night** trips are ~50% faster (16.08 mph).

---

### 🚕 D. Driver Performance (Vendors)

**Goal:** Compare objective performance between vendors.

```sql
SELECT
  VendorID,
  ROUND(SUM(total_revenue), 2) AS revenue,
  ROUND(AVG(avg_tip_percentage), 2) AS avg_tip_pct,
  ROUND(AVG(revenue_per_hour), 2) AS revenue_per_hour
FROM iceberg.gold.driver_performance
GROUP BY VendorID
ORDER BY revenue DESC;

```

**📊 Actual Results:**
| VendorID | revenue ($) | avg_tip_pct | revenue_per_hour |
| :--- | :--- | :--- | :--- |
| 2 | 800,971,057.45 | 12.32% | 107.10 |
| 1 | 226,683,488.85 | 11.80% | 93.55 |

> **💡 Insight:** Vendor 2 dominates market share (~78% of revenue) and achieves higher efficiency (revenue/hour) compared to Vendor 1.

---

### 💳 E. Payment Analysis

**Goal:** Determine if payment methods influence tipping behavior.

```sql
SELECT
  payment_type_label,
  SUM(trip_count) AS total_trips,
  ROUND(SUM(total_revenue), 2) AS revenue,
  ROUND(AVG(avg_tip_pct), 2) AS avg_tip_pct
FROM iceberg.gold.payment_analysis
GROUP BY payment_type_label
ORDER BY revenue DESC;

```

**📊 Actual Results:**
| payment_type | total_trips | revenue ($) | avg_tip_pct |
| :--- | :--- | :--- | :--- |
| credit_card | 29,801,007 | 885,052,653 | 14.61% |
| cash | 5,167,606 | 128,843,509 | 0.00% |
| dispute | 361,190 | 10,233,710 | 0.02% |
| no_charge | 137,491 | 3,524,672 | 0.02% |

> **💡 Insight:** Credit card payments are the standard and generate a healthy **14.6%** tip average. Cash tips are typically not recorded in the system (showing 0%).

---

### 🗺️ F. Most Profitable Routes

**Goal:** Identify high-volume, high-efficiency routes (LocationIDs).

```sql
SELECT
  route_id,
  SUM(trip_count) AS total_trips,
  ROUND(AVG(avg_fare), 2) AS avg_fare,
  ROUND(AVG(efficiency_ratio), 2) AS efficiency
FROM iceberg.gold.top_routes
GROUP BY route_id
ORDER BY total_trips DESC
LIMIT 5;

```

**📊 Actual Results:**
| route_id | total_trips | avg_fare | efficiency |
| :--- | :--- | :--- | :--- |
| 237_236 | 237,154 | 15.77 | 0.15 |
| 236_237 | 188,098 | 16.33 | 0.13 |
| 237_237 | 115,818 | 14.20 | 0.10 |
| 236_236 | 109,231 | 13.35 | 0.13 |
| 161_237 | 31,674 | 18.49 | 0.10 |

> **💡 Insight:** Routes between zones 236 and 237 (Upper East Side) represent the absolute highest volume of traffic in the city.

---

## 🚀 Future Improvements

* [ ] **Airflow Integration:** Move from scripts to DAG-based orchestration.
* [ ] **Data Quality:** Add `Great Expectations` for handling schema drift and date outliers.
* [ ] **dbt:** Implement dbt-trino for managing Gold layer transformations.
* [ ] **Real-time:** Ingest live data via Kafka.

---

### 👨‍💻 Author

**Louis Jordan Yiyueme Teyou**
*Data Architect | Data Engineer | Data Scientist*
*Computer Engineer | Chef de Projet Data*

```

***

### Prochaine étape possible :
Si tu as les screenshots des dashboards Superset qui correspondent à ces résultats, je peux t'aider à formater la section "Dashboards" pour inclure les images juste à côté de ces analyses SQL. Cela créerait un lien visuel très fort pour un recruteur.

```
