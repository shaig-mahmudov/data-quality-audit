import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd


def create_sample_datasets() -> None:
    """Generates synthetic CSV, JSON, and XML datasets containing deliberate dirty data."""
    
    csv_content = """id,full_name,age,faculty,gpa
1,Alice Johnson,20,Computer Science,3.85
2,Bob Smith,,Information Systems,2.90
3,Charlie Brown,21,,3.40
4,Diana Prince,22,Computer Science,3.10
4,Diana Prince,22,Computer Science,3.10
"""
    with open("students.csv", "w", encoding="utf-8") as f:
        f.write(csv_content.strip())

    json_content = [
        {"id": 1, "full_name": "Alice Johnson", "age": 20, "faculty": "Computer Science", "gpa": 3.85},
        {"id": 2, "full_name": "Bob Smith", "age": None, "faculty": "Information Systems", "gpa": 2.90},
        {"id": 3, "full_name": "Charlie Brown", "age": 21, "faculty": None, "gpa": 3.40},
        {"id": 4, "full_name": "Diana Prince", "age": 22, "faculty": "Computer Science", "gpa": 3.10},
        {"id": 4, "full_name": "Diana Prince", "age": 22, "faculty": "Computer Science", "gpa": 3.10}
    ]
    with open("students.json", "w", encoding="utf-8") as f:
        json.dump(json_content, f, indent=4)

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<students>
    <student>
        <id>1</id>
        <full_name>Alice Johnson</full_name>
        <age>20</age>
        <faculty>Computer Science</faculty>
        <gpa>3.85</gpa>
    </student>
    <student>
        <id>2</id>
        <full_name>Bob Smith</full_name>
        <age></age>
        <faculty>Information Systems</faculty>
        <gpa>2.90</gpa>
    </student>
    <student>
        <id>3</id>
        <full_name>Charlie Brown</full_name>
        <age>21</age>
        <faculty></faculty>
        <gpa>3.40</gpa>
    </student>
    <student>
        <id>4</id>
        <full_name>Diana Prince</full_name>
        <age>22</age>
        <faculty>Computer Science</faculty>
        <gpa>3.10</gpa>
    </student>
    <student>
        <id>4</id>
        <full_name>Diana Prince</full_name>
        <age>22</age>
        <faculty>Computer Science</faculty>
        <gpa>3.10</gpa>
    </student>
</students>
"""
    with open("students.xml", "w", encoding="utf-8") as f:
        f.write(xml_content.strip())

    print("[SUCCESS] Sample datasets (CSV, JSON, XML) generated successfully.\n")


class DataQualityAuditor:
    """
    Automated Data Profiler for inspecting structure,
    identifying duplicates, and detecting missing values.
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.df: Optional[pd.DataFrame] = None
        self.report: Dict[str, Any] = {}

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        self._load_file()

    def _load_file(self) -> None:
        """Parses the input file into a Pandas DataFrame based on file extension."""
        ext = self.file_path.suffix.lower()

        if ext == ".csv":
            self.df = pd.read_csv(self.file_path)
        elif ext == ".json":
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.df = pd.json_normalize(data)
        elif ext == ".xml":
            self.df = pd.read_xml(self.file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def run_audit(self) -> Dict[str, Any]:
        """Calculates key data quality metrics."""
        if self.df is None or self.df.empty:
            return {"status": "FAILED", "error": "Dataset is empty or failed to load."}

        total_rows, total_cols = self.df.shape
        duplicate_count = int(self.df.duplicated().sum())
        duplicate_pct = round((duplicate_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

        missing_series = self.df.isnull().sum()
        missing_pct_series = (missing_series / total_rows) * 100

        column_stats = []
        for col in self.df.columns:
            column_stats.append({
                "column": col,
                "dtype": str(self.df[col].dtype),
                "missing_count": int(missing_series[col]),
                "missing_pct": round(float(missing_pct_series[col]), 2),
                "unique_values": int(self.df[col].nunique(dropna=True))
            })

        rows_with_nan = int(self.df.isnull().any(axis=1).sum())

        self.report = {
            "file_name": self.file_path.name,
            "format": self.file_path.suffix.lower(),
            "dimensions": {"rows": total_rows, "columns": total_cols},
            "memory_usage_kb": round(self.df.memory_usage(deep=True).sum() / 1024, 2),
            "duplicates": {
                "count": duplicate_count,
                "percentage": duplicate_pct
            },
            "missing_data": {
                "rows_affected": rows_with_nan,
                "rows_affected_pct": round((rows_with_nan / total_rows) * 100, 2),
                "columns_detail": column_stats
            }
        }
        return self.report

    def print_summary(self) -> None:
        """Displays formatted audit results in the console."""
        if not self.report:
            self.run_audit()

        r = self.report
        print("=" * 65)
        print(f" DATA QUALITY AUDIT REPORT: {r['file_name']}")
        print("=" * 65)
        print(f"Format: {r['format']} | Memory Usage: {r['memory_usage_kb']} KB")
        print(f"Dimensions: {r['dimensions']['rows']} rows x {r['dimensions']['columns']} columns")
        print(f"Duplicates: {r['duplicates']['count']} row(s) ({r['duplicates']['percentage']}%)")
        print(f"Rows with Missing Values: {r['missing_data']['rows_affected']} ({r['missing_data']['rows_affected_pct']}%)")
        print("-" * 65)

        cols_df = pd.DataFrame(r["missing_data"]["columns_detail"])
        cols_df.columns = ["Column", "Dtype", "Missing", "Missing %", "Unique"]
        print(cols_df.to_string(index=False))
        print("=" * 65 + "\n")

    def clean_and_export(self, output_path: str) -> pd.DataFrame:
        """Deduplicates rows, imputes missing values, and exports the clean dataset."""
        if self.df is None:
            raise RuntimeError("No dataframe available to clean.")

        cleaned_df = self.df.drop_duplicates().copy()

        for col in cleaned_df.columns:
            if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
            else:
                cleaned_df[col] = cleaned_df[col].fillna("Unknown")

        out_ext = Path(output_path).suffix.lower()
        if out_ext == ".csv":
            cleaned_df.to_csv(output_path, index=False)
        elif out_ext == ".json":
            cleaned_df.to_json(output_path, orient="records", indent=4)
        elif out_ext == ".xml":
            cleaned_df.to_xml(output_path, index=False)
        else:
            raise ValueError(f"Unsupported output format: {out_ext}")

        print(f"[EXPORTED] Cleaned dataset saved to: {output_path}")
        return cleaned_df


if __name__ == "__main__":

    create_sample_datasets()

    files = ["students.csv", "students.json", "students.xml"]
    for file in files:
        auditor = DataQualityAuditor(file)
        auditor.run_audit()
        auditor.print_summary()

    print("Initiating Data Cleaning & Transformation...")
    csv_auditor = DataQualityAuditor("students.csv")
    cleaned_data = csv_auditor.clean_and_export("students_cleaned.csv")
    
    print("\nSample of Cleaned Data:")
    print(cleaned_data)