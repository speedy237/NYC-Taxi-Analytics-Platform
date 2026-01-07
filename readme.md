

```markdown
# 🚕 NYC Taxi Analytics Platform — End-to-End Data Engineering Project

## 📌 Overview
This project is an **end-to-end data engineering analytics platform** built on NYC Taxi data, enriched with weather information, and designed following modern **Lakehouse best practices**.

It demonstrates:
* **Robust Architecture:** Bronze / Silver / Gold layers.
* **Modern Storage:** Apache Iceberg as the table format.
* **Processing:** Apache Spark for heavy transformations.
* **Analytics:** Trino for high-speed querying.
* **Visualization:** Apache Superset for business dashboards.

> **🎯 Goal:** Transform raw operational data into business-ready analytics for operations, finance, and strategy.

---

## 🏗️ Architecture

The platform follows a linear, schema-enforced pipeline moving from raw files to business-grade tables.



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

## 🧰 Tech Stack

| Layer | Technology | Description |
| --- | --- | --- |
| **Storage** | **Apache Iceberg** | High-performance table format for huge analytic datasets. |
| **Processing** | **Apache Spark (PySpark)** | Distributed data processing engine for ETL. |
| **Query Engine** | **Trino** | Distributed SQL query engine for interactive analytics. |
| **BI / Dashboards** | **Apache Superset** | Modern data exploration and visualization platform. |
| **Data Source** | **NYC Taxi + Weather** | TLC Trip Record Data & Central Park Weather Data. |
| **Format** | **Parquet** | Columnar storage format. |
| **Orchestration** | **Notebook/Airflow** | Workflow management (Extensible). |

---

## 📂 Data Layers

### 🥉 Bronze — Raw Ingestion

* **Tables:** `bronze.taxi_trips_2024`, `bronze.taxi_zones`, `bronze.weather_2024`
* **Principles:**
* Strict Schema enforcement.
* No business logic applied.
* Native Iceberg partitioning (hidden partitions).



### 🥈 Silver — Clean & Enriched

* **Tables:** `silver.trips_enriched`, `silver.trips_with_zones`, `silver.trips_complete`
* **Enhancements:**
* Trip validation & filtering (removing outliers).
* Duration & speed calculations.
* Zone enrichment (Joining Location IDs with Zone names).
* **Weather Join:** Hourly weather data joined with trips.
* **Flags:** `is_rainy`, `is_cold`, `is_hot`.



### 🥇 Gold — Business Analytics

* **Tables:** `gold.daily_metrics`, `gold.hourly_patterns`, `gold.top_routes`, `gold.driver_performance`, `gold.weather_impact`, `gold.payment_analysis`
* **Value:** Each table is aggregated, optimized for read-heavy workloads (Trino), and directly mapped to Superset charts.

---

## 📊 Dashboards (Apache Superset)

### 1. Executive Overview

* **Objective:** Global business health monitoring.
* **KPIs:** Total trips, Total revenue, Revenue per trip, Avg trip duration, Tip %.
* **Charts:**
* 📈 Line: Trips & revenue over time.
* 📊 Bar: Revenue by borough.
* 🍩 Donut: Payment type distribution.



### 2. Temporal & Traffic Patterns

* **Objective:** Operational optimization.
* **Charts:**
* 📈 Line: Avg trip duration over time.
* 🔥 Heatmap: Trips by hour & day.
* 📊 Bar: Rush hours vs regular hours.



### 3. Weather Impact Analysis

* **Objective:** Understand how weather influences demand and efficiency.
* **Charts:**
* 🔵 Scatter: Rain (precipitation) vs Revenue.
* 📈 Line: Avg duration by weather condition.
* 📊 Bar: Trips per weather condition.



### 4. Driver Performance

* **Objective:** Operational efficiency tracking.
* **KPIs:** Revenue per hour, Avg trip duration, Avg tip %.
* **Charts:**
* 📊 Bar: Revenue by Vendor.
* 🔵 Scatter: Speed vs Revenue.
* 🔢 Table: Top drivers ranking.



### 5. Payment Behavior

* **Objective:** Payment optimization and financial trends.
* **KPIs:** % Credit Card usage, Avg tip per payment type, Revenue by payment method.
* **Charts:**
* 🍩 Donut: Payment type distribution.
* 📊 Bar: Tips by payment method.
* 📈 Line: Credit card usage over time.



---

## 🧪 Example SQL — % Credit Card Usage

Here is a sample query used in the **Payment Behavior** dashboard, executed via Trino on the Gold layer:

```sql
SELECT
    pickup_date,
    SUM(
        CASE WHEN payment_type_label = 'credit_card'
        THEN trip_count ELSE 0 END
    ) * 100.0
    /
    SUM(trip_count) AS credit_card_percentage
FROM iceberg.gold.payment_analysis
GROUP BY pickup_date
ORDER BY pickup_date;

```

---

## 📈 Key Business Insights

* **Weather:** Rain increases trip duration significantly but also increases revenue per trip.
* **Payment:** Credit card payments consistently generate higher tip percentages than cash.
* **Traffic:** Night trips show higher average speeds but also higher variance in safety metrics.
* **Routes:** Airport routes (JFK/LGA) dominate the top revenue-generating routes.
* **Impact:** Extreme weather events have a quantifiable impact on operational performance (down to the hour).

---

## 🚀 Future Improvements

* [ ] Implement **Airflow** for robust DAG orchestration.
* [ ] Integrate **dbt** for metric governance and documentation.
* [ ] Add **ML demand forecasting** based on historical patterns.
* [ ] Upgrade to **Real-time ingestion** using Kafka.
* [ ] Enable **Iceberg Time Travel** analytics for historical auditing.

---

## ⭐ Why this project matters

* ✅ **Realistic Data:** Handles real-world volume and messiness.
* ✅ **Modern Architecture:** Uses the standard "Modern Data Stack" (Lakehouse).
* ✅ **Business Value:** Focuses on extracting insights, not just moving data.
* ✅ **Full Cycle:** Covers Engineering (Spark), Storage (Iceberg), Serving (Trino), and BI (Superset).

---

### 👨‍💻 Author

**Data Engineer Portfolio Project**
*Built with production-grade tooling & best practices.*

