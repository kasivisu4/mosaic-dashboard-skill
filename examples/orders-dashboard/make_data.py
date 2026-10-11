"""Create the example's data files: orders.parquet (test data) and orders_clean.parquet (the plan's export).

Usage (from anywhere): python examples/orders-dashboard/make_data.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import duckdb

here = Path(__file__).resolve().parent
root = here.parent.parent
subprocess.run([sys.executable, str(root / "skills/planning-dashboard/evals/make_fixtures.py")], check=True)
shutil.copy(root / "skills/planning-dashboard/evals/files/orders.parquet", here / "orders.parquet")
os.chdir(here)
duckdb.sql("COPY (SELECT * FROM 'orders.parquet') TO 'orders_clean.parquet'")
print(f"wrote orders.parquet and orders_clean.parquet to {here}")
