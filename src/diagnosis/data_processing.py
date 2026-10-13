
"""
NetSages | NetDoctor
Dataset loading, numeric extraction, statistical analysis,
and missing-value reporting.
"""

import csv
import math
import statistics
from pathlib import Path


# ---------------------------------------------------------
# 1. DATASET PATH
# ---------------------------------------------------------

# The CSV file is located at src/tests/data/network_data.csv.
DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "tests"
    / "data"
    / "network_data.csv"
)


# ---------------------------------------------------------
# 2. LOAD THE DATASET
# ---------------------------------------------------------


def load_dataset(file_path=DATASET_PATH):
    """Load CSV rows and return them as a list of dictionaries."""

    # Check that the dataset exists.
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    # Open the CSV file with UTF-8 encoding support.
    with file_path.open(
        mode="r",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        # Skip blank lines before reading the CSV headers.
        non_blank_lines = (
            line for line in file if line.strip()
        )

        # Read the CSV headers and records.
        reader = csv.DictReader(non_blank_lines)
        rows = list(reader)

        # Stop if the file contains no CSV headers.
        if not reader.fieldnames:
            raise ValueError(
                f"The dataset is empty or has no CSV headers: {file_path}"
            )

    return rows



# ---------------------------------------------------------
# 3. EXTRACT NUMERIC COLUMNS
# ---------------------------------------------------------

def extract_numeric_columns(rows):
    """Extract finite numeric values from each CSV column."""

    numeric_columns = {}

    if not rows:
        return numeric_columns

    # Each dictionary key represents a CSV column.
    for column in rows[0].keys():
        values = []

        for row in rows:
            raw_value = row.get(column)

            # Ignore missing and blank values.
            if raw_value is None or raw_value.strip() == "":
                continue

            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                # Categorical values such as 'strong' are not numeric.
                continue

            # Exclude NaN and positive/negative infinity.
            if math.isfinite(value):
                values.append(value)

        # Store columns that contain at least one numeric value.
        if values:
            numeric_columns[column] = values

    return numeric_columns


# ---------------------------------------------------------
# 4. CALCULATE NUMERIC STATISTICS
# ---------------------------------------------------------

def calculate_statistics(numeric_columns):
    """Calculate count, mean, standard deviation, min and max."""

    results = {}

    for column, values in numeric_columns.items():
        results[column] = {
            "count": len(values),
            "mean": statistics.mean(values),
            # Sample standard deviation requires at least two values.
            "std": (
                statistics.stdev(values)
                if len(values) > 1
                else 0.0
            ),
            "min": min(values),
            "max": max(values),
        }

    return results


# ---------------------------------------------------------
# 5. COUNT MISSING VALUES
# ---------------------------------------------------------

def count_missing_values(rows):
    """Count missing or blank cells in each dataset column."""

    if not rows:
        return {}

    missing_counts = {}

    for column in rows[0].keys():
        missing_counts[column] = sum(
            row.get(column) is None
            or row.get(column).strip() == ""
            for row in rows
        )

    return missing_counts


# ---------------------------------------------------------
# 6. MAIN DATA-PROCESSING WORKFLOW
# ---------------------------------------------------------

def main():
    """Load the dataset and display its analysis."""

    print("NetSages | NetDoctor - Dataset Analysis")
    print("=" * 45)

    # Load the CSV file.
    rows = load_dataset()

    print(f"\nDataset path: {DATASET_PATH}")
    print(f"Total rows: {len(rows)}")

    # Display a preview of up to five records.
    print("\nDataset Preview")
    print("-" * 45)

    for row in rows[:5]:
        print(row)

    # Extract numeric values and calculate their statistics.
    numeric_columns = extract_numeric_columns(rows)
    summary = calculate_statistics(numeric_columns)

    print("\nNumerical Statistics")
    print("-" * 45)

    if summary:
        for column, stats in summary.items():
            print(f"\nColumn: {column}")
            print(f"  Count: {stats['count']}")
            print(f"  Mean:  {stats['mean']:.2f}")
            print(f"  Std:   {stats['std']:.2f}")
            print(f"  Min:   {stats['min']:.2f}")
            print(f"  Max:   {stats['max']:.2f}")
    else:
        print("No numeric data found.")

    # Report blank or missing cells.
    missing_counts = count_missing_values(rows)

    print("\nMissing-Value Counts")
    print("-" * 45)

    for column, count in missing_counts.items():
        print(f"{column}: {count}")

    print("\nDataset analysis completed.")


# ---------------------------------------------------------
# 7. EXECUTION ENTRY POINT
# ---------------------------------------------------------

# Run main() only when this file is executed directly.
if __name__ == "__main__":
    main()
