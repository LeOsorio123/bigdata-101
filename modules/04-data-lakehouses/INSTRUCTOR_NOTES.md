# Instructor Notes — Data Lakehouses

## Module Overview

This module introduces the Data Lakehouse architecture, the Medallion pattern (Bronze/Silver/Gold), and Delta Lake features. Students work with real data on Azure Databricks connected to ADLS Gen2.

**Audience**: Students who completed modules 01-mapreduce, 02-spark, and 03-databricks
**Duration**: 4-5 hours of instruction + 3-4 hours of practice
**Prerequisites**: Databricks workspace, ADLS Gen2 storage account, Uber dataset uploaded

## Teaching Strategy

### Core Principle
Start with the "why" — students already know Spark and DataFrames. The question now is: how do we organize data at scale? The Lakehouse answers this by combining the best of warehouses and lakes.

### Recommended Progression

```
Session 1: Concepts — Warehouse vs Lake vs Lakehouse (60 min)
    ↓
Session 2: Medallion — Bronze ingestion (90 min)
    ↓
Session 3: Medallion — Silver cleaning + Gold aggregations (90 min)
    ↓
Session 4: Delta Lake features — ACID, Time Travel, MERGE (90 min)
```

---

## Session 1: Concepts (60 minutes)

### Lesson Plan

**1. Motivation: why do we need a new architecture? (15 min)**
- Draw on the board: Data Warehouse (structured, expensive, SQL) vs Data Lake (cheap, any format, messy)
- Ask the class: "What if you could have cheap storage AND schema enforcement?"
- Introduce the Lakehouse concept

**2. Live demo: `01_warehouse_vs_lake.py` (30 min)**
- Run each section live, pausing to explain:
  - Schema-on-Write: define schema first, reject bad data
  - Schema-on-Read: store everything, figure out types later
  - Lakehouse: Delta Lake gives us Schema-on-Write on lake storage
- Emphasize the comparison table at the end

**3. Discussion (15 min)**
- "Where does your company/project store data today?"
- "What problems would a Lakehouse solve?"
- Preview: "Next we'll build a real Lakehouse with the Medallion pattern"

### Key Points to Emphasize
- The Lakehouse is not just a buzzword — it solves real problems (cost, flexibility, governance)
- Delta Lake is the technology that enables the Lakehouse pattern
- Other formats exist (Apache Iceberg, Apache Hudi) but Delta is the most mature on Databricks

---

## Session 2: Bronze Ingestion (90 minutes)

### Lesson Plan

**1. The Medallion Architecture (20 min)**
- Draw on the board: Bronze → Silver → Gold
- Bronze = raw data, as-is, append-only
- Silver = cleaned, validated, conformed
- Gold = aggregated, business-ready
- Analogy: "Bronze is the raw ingredient, Silver is the prepared ingredient, Gold is the dish"

**2. ADLS Gen2 Setup (15 min)**
- Walk through the setup together (students should have done this beforehand)
- Show the landing zone in Azure Portal
- Explain the `abfss://` protocol

**3. Live demo: `01_bronze_ingestion.py` (40 min)**
- Run each cell, pausing to explain:
  - Why we read everything as STRING (preserve raw data)
  - Why we add `_ingestion_timestamp` and `_source_file` (lineage)
  - Why append-only (Bronze is the historical source of truth)
  - The CSV → Delta conversion (content stays the same, format changes)
- Show the Delta table in the Databricks catalog
- Show `DESCRIBE HISTORY` — time travel from day one

**4. Practice (15 min)**
- Students run the notebook themselves
- Verify record counts match
- Explore the Bronze table with SQL queries

### Common Student Mistakes

| Mistake | Symptom | Solution |
|---------|---------|----------|
| Wrong Access Key | `Access denied` error | Double-check key1 in Azure Portal |
| CSVs not uploaded | `Path does not exist` | Verify files are in `landing/uber/` |
| Running Silver before Bronze | `Table not found` | Run notebooks in order |
| Using `inferSchema` in Bronze | Types get auto-cast | Use explicit STRING schema |

---

## Session 3: Silver + Gold (90 minutes)

### Lesson Plan

**1. Silver: cleaning and validation (45 min)**
- Run `02_silver_cleaning.py` live
- Key transformations to highlight:
  - Column renaming (spaces → snake_case)
  - Type casting (STRING → INT, DOUBLE)
  - City extraction from file name (regex)
  - Null filtering and deduplication
- Show the before/after record counts
- Ask: "Why did some records get rejected?"

**2. Gold: business aggregations (30 min)**
- Run `03_gold_aggregations.py` live
- Two Gold tables with different purposes:
  - `city_metrics`: KPIs per city (for executives)
  - `top_routes`: slowest routes per city (for analysts)
- Show window functions (`row_number`, `PARTITION BY`)
- "These tables are what Power BI or Tableau would connect to"

**3. End-to-end review (15 min)**
- Draw the full pipeline on the board:
  ```
  CSV (landing) → Bronze (raw Delta) → Silver (clean Delta) → Gold (aggregated Delta)
  ```
- Ask: "If we get new data next month, which layers do we re-run?"
  - Answer: all three, but Bronze is append, Silver/Gold are overwrite
- Ask: "If we find a bug in Silver logic, do we lose the raw data?"
  - Answer: no, Bronze is untouched — we fix Silver and reprocess

---

## Session 4: Delta Lake Features (90 minutes)

### Lesson Plan

**1. ACID Transactions (20 min)**
- Run INSERT, UPDATE, DELETE on `delta_demo`
- Emphasize: these operations are atomic — if they fail, nothing changes
- Compare with plain Parquet: "What happens if your Parquet write fails halfway?"

**2. Time Travel (20 min)**
- Show `DESCRIBE HISTORY`
- Query `VERSION AS OF 0` — the original data is still there
- Use case: "Your analyst accidentally deleted rows. With Time Travel, you can recover them."
- Show the comparison query between versions

**3. Schema Evolution (15 min)**
- Add `travel_minutes` column via `mergeSchema`
- Show that old records get NULL in the new column
- "In a traditional warehouse, adding a column requires a migration. Here it's one option."

**4. MERGE / Upserts (20 min)**
- This is the most complex feature — take your time
- Explain the match condition clearly
- Show the result: 1 updated row + 1 new row
- Use case: CDC (Change Data Capture) from transactional databases

**5. OPTIMIZE and Z-ORDER (15 min)**
- Explain the small files problem (many small Parquet files = slow reads)
- OPTIMIZE compacts them
- Z-ORDER co-locates data for filtered queries
- "If you always filter by city, Z-ORDER by city makes those queries faster"

### Concepts Students Find Difficult

**MERGE syntax**: The match condition can be confusing. Draw it as a Venn diagram:
- Left circle: existing data (target)
- Right circle: new data (source)
- Overlap: matched → UPDATE
- Right only: not matched → INSERT

**Time Travel vs Backups**: "Time Travel is NOT a backup strategy. Delta keeps history for a limited time (default 30 days). For real backups, use a separate process."

**Schema Evolution vs Schema Enforcement**: "Evolution adds columns. Enforcement rejects data that doesn't match. They work together — you can evolve the schema, but new data must still match the evolved schema."

---

## Suggested Assessment

### Assignment 1: Build a Medallion Pipeline (25 points)
**Due**: 1 week

Using a different dataset (students choose or instructor provides), build a complete Bronze → Silver → Gold pipeline.

**Rubric**:
- Bronze: raw ingestion with metadata (5 pts)
- Silver: cleaning, type casting, validation (8 pts)
- Gold: at least 2 aggregation tables with business value (8 pts)
- Documentation and clean code (4 pts)

### Assignment 2: Delta Lake Features (15 points)
**Due**: Next class

Using the `delta_demo` table:
1. Add 5 new records and show the version history (3 pts)
2. Use Time Travel to compare version 0 with the current version (3 pts)
3. Perform a MERGE with 2 updates and 3 inserts (5 pts)
4. Run OPTIMIZE and explain what changed (4 pts)

---

## Transition to Next Module

After completing this module, students should:
- ✅ Understand the Lakehouse architecture and why it exists
- ✅ Build a complete Medallion pipeline (Bronze → Silver → Gold)
- ✅ Use Delta Lake features: ACID, Time Travel, Schema Evolution, MERGE
- ✅ Work with ADLS Gen2 as the storage layer
- ✅ Write production-quality data pipelines in Databricks

**Next step**: `../05-data-science/` — Exploratory analysis, feature engineering, and MLlib

**Pedagogical bridge**: "You now know how to organize and manage data at scale with the Lakehouse. Next, we'll use that clean Gold data to do data science — EDA, feature engineering, and machine learning with Spark MLlib."

---

**Last updated**: March 2026
**Version**: 1.0
