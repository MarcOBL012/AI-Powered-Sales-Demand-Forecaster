import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.db_handler import DBHandler

db = DBHandler("local_forecaster.duckdb")
print("--- PROJECTS ---")
print(db.get_projects())
