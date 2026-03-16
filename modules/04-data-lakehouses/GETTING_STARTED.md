# Getting Started with Data Lakehouses

## Prerequisites

- A Databricks workspace (Azure Databricks recommended)
- An Azure Data Lake Storage Gen2 account
- The 7 Uber Travel Times CSV files (in `datasets/uber/`)

## Step 1: Create the ADLS Gen2 Storage Account

1. Go to Azure Portal → Create a resource → Storage Account
2. Enable **"Hierarchical namespace"** under the Advanced tab (this makes it ADLS Gen2)
3. Note down the storage account name (e.g., `introbigdataupb`)

## Step 2: Create the container and upload data

1. Inside the Storage Account → Containers → `+ Container` → Name: `bigdata`
2. Create the folder structure: `bigdata/landing/uber/`
3. Upload all 7 CSV files from `datasets/uber/` into that folder

```
bigdata/
└── landing/
    └── uber/
        ├── Travel_Times - Bogota.csv
        ├── Travel_Times - Boston.csv
        ├── Travel_Times - Johannesburg and Pretoria.csv
        ├── Travel_Times - Manila.csv
        ├── Travel_Times - Paris.csv
        ├── Travel_Times - Sydney.csv
        └── Travel_Times - Washington DC.csv
```

## Step 3: Get the Access Key

1. Azure Portal → Storage Account → Security + networking → Access keys
2. Copy **key1**

## Step 4: Configure the notebooks

In each notebook, replace the configuration variables:

```python
STORAGE_ACCOUNT = "<your_storage_account>"   # e.g.: "introbigdataupb"
CONTAINER       = "bigdata"
ACCESS_KEY      = "<your_access_key>"        # key1 from the previous step
```

> **Security note**: In production, use Databricks Secrets instead of hardcoding keys.

## Step 5: Run the notebooks in order

1. `01-concepts/01_warehouse_vs_lake.py` — standalone, run anytime
2. `02-medallion/01_bronze_ingestion.py` — creates the Bronze layer
3. `02-medallion/02_silver_cleaning.py` — requires Bronze
4. `02-medallion/03_gold_aggregations.py` — requires Silver
5. `03-delta-lake/01_delta_features.py` — standalone, run anytime

## How to import notebooks into Databricks

1. In Databricks → Workspace → right-click → Import
2. Select the `.py` file
3. Databricks recognizes the `# Databricks notebook source` header and `# COMMAND ----------` separators

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Access denied` on ADLS | Verify the Access Key is correct and the container name matches |
| `Path does not exist` | Check that CSVs are uploaded to `landing/uber/` inside the container |
| `Table already exists` | Run `DROP TABLE IF EXISTS <table>` before re-running |
| Schema mismatch errors | Ensure you're running notebooks in order (Bronze → Silver → Gold) |
| Cluster not starting | Check Databricks Runtime version (13.x+ required for Delta Lake) |
