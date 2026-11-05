# Data Quality Audit: Structured & Semi-Structured Data

An automated data engineering pipeline designed to ingest, inspect, and clean structured and semi-structured datasets (`CSV`, `JSON`, and `XML`). Deliberate data quality issues—such as missing values and duplicate records—are profiled and resolved automatically.

---

## Repository Structure

```text
data-quality-audit/
├── data_engineering_lab.py   # Unified pipeline: data generation, auditing, and cleaning
├── students.csv              # Raw structured dataset (CSV)
├── students.json             # Raw semi-structured dataset (JSON)
├── students.xml              # Raw semi-structured dataset (XML)
└── students_cleaned.csv      # Exported artifact after deduplication and imputation
```

---

## Key Features

- **Multi-Format Ingestion:** Reads tabular and hierarchical data formats using `pandas` and `lxml` (`read_csv`, `json_normalize`, `read_xml`).
- **Automated Quality Profiling (`DataQualityAuditor`):**
  - **Uniqueness Check:** Identifies redundant duplicate rows.
  - **Completeness Check:** Computes column-level missing value counts and percentage ratios.
  - **Schema & Memory Inspection:** Reports memory footprint and column data types (`dtypes`).
- **Data Remediation & Cleaning:**
  - Removes identical records via `.drop_duplicates()`.
  - Imputes numerical gaps with the column **median**.
  - Imputes categorical missing fields with `"Unknown"`.

---

## 🛠 Prerequisites & Installation

Ensure you have Python 3.8+ installed, then install the required dependencies:

```bash
pip install pandas lxml
```

---

## Usage

Run the single-file pipeline from your terminal:

```bash
python data_engineering_lab.py
```

### Execution Flow:
1. Generates test datasets (`students.csv`, `students.json`, `students.xml`) with simulated quality defects.
2. Audits all three datasets and outputs formatted quality reports to stdout.
3. Cleans the primary dataset and exports the sanitized version to `students_cleaned.csv`.

---

## Sample Audit Output

```text
=================================================================
 DATA QUALITY AUDIT REPORT: students.csv
=================================================================
Format: .csv | Memory Usage: 1.42 KB
Dimensions: 5 rows x 5 columns
Duplicates: 1 row(s) (20.0%)
Rows with Missing Values: 2 (40.0%)
-----------------------------------------------------------------
Column      Dtype     Missing   Missing %   Unique
id          int64           0         0.0        4
full_name  object           0         0.0        4
age       float64           1        20.0        3
faculty    object           1        20.0        2
gpa       float64           0         0.0        4
=================================================================
```
