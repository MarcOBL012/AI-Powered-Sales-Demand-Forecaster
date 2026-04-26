import duckdb
import pandas as pd
import os

class DBHandler:
    def __init__(self, db_path="local_forecaster.duckdb"):
        self.db_path = db_path
        self.conn = duckdb.connect(self.db_path)
        self._initialize_schema()

    def _initialize_schema(self):
        # Create core tables if they don't exist
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_projects START 1;
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_projects'),
                name VARCHAR UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_skus START 1;
            CREATE TABLE IF NOT EXISTS skus (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_skus'),
                project_id INTEGER,
                sku_code VARCHAR,
                category VARCHAR,
                description VARCHAR,
                UNIQUE(project_id, sku_code)
            )
        """)
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_sales START 1;
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_sales'),
                sku_id INTEGER,
                date DATE,
                volume DOUBLE,
                price DOUBLE,
                inventory DOUBLE,
                UNIQUE(sku_id, date)
            )
        """)
        
    def create_project(self, name: str):
        try:
            self.conn.execute("INSERT INTO projects (name) VALUES (?)", (name,))
            return self.get_project_by_name(name)['id'].iloc[0]
        except duckdb.ConstraintException:
            return self.get_project_by_name(name)['id'].iloc[0]

    def get_project_by_name(self, name: str):
         return self.conn.execute("SELECT * FROM projects WHERE name = ?", (name,)).fetchdf()

    def load_sales_dataframe(self, project_id: int, df: pd.DataFrame, mapping: dict):
        """
        df (pd.DataFrame): DataFrame from uploaded file
        mapping (dict): dict like {'sku_code': 'Item', 'date': 'Date', 'volume': 'Qty', 'price': 'Unit_Price', 'category': 'Type'}
        """
        # This is a simplified loading mechanism
        unique_skus = df[mapping['sku_code']].unique()
        
        for sku in unique_skus:
            # Prepare sales data
            sku_df = df[df[mapping['sku_code']] == sku].copy()
            
            # Extract category if present
            category = None
            if 'category' in mapping and mapping['category'] in sku_df.columns:
                category_val = sku_df[mapping['category']].iloc[0]
                category = str(category_val) if pd.notna(category_val) else None
                
            # Insert SKU if not exists
            try:
                 self.conn.execute("INSERT INTO skus (project_id, sku_code, category) VALUES (?, ?, ?)", (project_id, sku, category))
            except duckdb.ConstraintException:
                 # If we wanted to update category for existing SKUs, we could do it here
                 pass
                 
            # Get SKU ID
            sku_id = self.conn.execute("SELECT id FROM skus WHERE project_id = ? AND sku_code = ?", (project_id, sku)).fetchone()[0]
            
            for index, row in sku_df.iterrows():
                try:
                    self.conn.execute(
                        "INSERT INTO sales (sku_id, date, volume, price) VALUES (?, ?, ?, ?)", 
                        (sku_id, row[mapping['date']], row[mapping['volume']], row.get(mapping.get('price'), 0))
                    )
                except duckdb.ConstraintException:
                    pass

    def get_projects(self):
        return self.conn.execute("SELECT * FROM projects").fetchdf()

    def get_skus(self, project_id: int):
        return self.conn.execute("SELECT * FROM skus WHERE project_id = ?", (project_id,)).fetchdf()

    def get_sales_data(self, sku_id: int):
        return self.conn.execute("SELECT * FROM sales WHERE sku_id = ? ORDER BY date", (sku_id,)).fetchdf()

    def close(self):
        self.conn.close()
